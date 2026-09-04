from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import error_response
from apps.core.geo_utils import bbox_of, cluster_points
from apps.core.permissions import IsOwnerOrModerator
from apps.core.throttling import LeadThrottle, SearchThrottle

from .filters import apply_filters, apply_radius
from .models import Listing, ListingPhoto
from .serializers import (
    ListingCardSerializer,
    ListingDetailSerializer,
    ListingPhotoSerializer,
    ListingWriteSerializer,
)


def _base_queryset():
    return (
        Listing.objects.select_related("city", "district", "owner", "owner__agency")
        .prefetch_related("photos", "price_history")
        .annotate(
            photo_count=Count("photos", distinct=True),
            tg_posted_count=Count(
                "telegram_posts", filter=Q(telegram_posts__status="posted"), distinct=True
            ),
        )
    )


class ListingListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    throttle_classes = [SearchThrottle]

    def get(self, request):
        qs = _base_queryset().filter(status=Listing.Status.ACTIVE)
        qs = apply_filters(qs, request.query_params)

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")
        radius = request.query_params.get("radius")
        all_matching = list(qs)
        if lat and lng and radius:
            all_matching = apply_radius(all_matching, float(lat), float(lng), float(radius))

        total = len(all_matching)

        try:
            page = max(1, int(request.query_params.get("page", 1)))
            limit = min(50, max(1, int(request.query_params.get("limit", 20))))
        except ValueError:
            page, limit = 1, 20

        start = (page - 1) * limit
        page_items = all_matching[start : start + limit]

        points = [(it.lat, it.lng, it.id) for it in all_matching]
        bbox = bbox_of([(p[0], p[1]) for p in points])
        clusters = cluster_points(points)

        serializer = ListingCardSerializer(page_items, many=True, context={"request": request})
        return Response(
            {
                "items": serializer.data,
                "total": total,
                "page": page,
                "limit": limit,
                "bbox": bbox,
                "clusters": clusters,
            }
        )

    def post(self, request):
        if not request.user.is_authenticated:
            return error_response(
                "not_authenticated", "Avval tizimga kiring", "Сначала войдите в систему", 401
            )
        serializer = ListingWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.save(
            owner=request.user,
            agency=getattr(request.user, "agency", None),
            status=Listing.Status.MODERATION,
        )
        return Response(
            ListingDetailSerializer(listing, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ListingDetailView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrModerator]

    def get_object(self, request, pk):
        listing = get_object_or_404(_base_queryset(), pk=pk)
        is_owner_or_mod = request.user.is_authenticated and (
            listing.owner_id == request.user.id or request.user.role == "moderator"
        )
        if listing.status != Listing.Status.ACTIVE and not is_owner_or_mod:
            return None
        self.check_object_permissions(request, listing)
        return listing

    def get(self, request, pk):
        listing = self.get_object(request, pk)
        if listing is None:
            return error_response("not_found", "E'lon topilmadi", "Объявление не найдено", 404)
        Listing.objects.filter(pk=pk).update(views=listing.views + 1)
        listing.views += 1
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    def patch(self, request, pk):
        listing = self.get_object(request, pk)
        if listing is None:
            return error_response("not_found", "E'lon topilmadi", "Объявление не найдено", 404)
        serializer = ListingWriteSerializer(listing, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(ListingDetailSerializer(listing, context={"request": request}).data)

    def delete(self, request, pk):
        listing = self.get_object(request, pk)
        if listing is None:
            return error_response("not_found", "E'lon topilmadi", "Объявление не найдено", 404)
        listing.status = Listing.Status.ARCHIVED
        listing.save(update_fields=["status"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingPhotoUploadView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner_id != request.user.id and request.user.role != "moderator":
            return error_response("permission_denied", "Ruxsat yo'q", "Доступ запрещён", 403)

        files = request.FILES.getlist("images")
        if not files:
            return error_response(
                "validation_error", "Kamida bitta foto yuklang", "Загрузите хотя бы одно фото", 400
            )
        start_order = listing.photos.count()
        created = []
        for i, f in enumerate(files):
            created.append(
                ListingPhoto.objects.create(
                    listing=listing, image=f, order=start_order + i, is_cover=(start_order + i == 0)
                )
            )
        return Response(
            ListingPhotoSerializer(created, many=True, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def delete(self, request, pk, photo_id):
        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner_id != request.user.id and request.user.role != "moderator":
            return error_response("permission_denied", "Ruxsat yo'q", "Доступ запрещён", 403)
        deleted, _ = ListingPhoto.objects.filter(pk=photo_id, listing=listing).delete()
        if not deleted:
            return error_response("not_found", "Foto topilmadi", "Фото не найдено", 404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListingBoostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        from apps.payments.services import create_boost_order

        listing = get_object_or_404(Listing, pk=pk)
        if listing.owner_id != request.user.id and request.user.role != "moderator":
            return error_response("permission_denied", "Ruxsat yo'q", "Доступ запрещён", 403)

        package = request.data.get("package")
        provider = request.data.get("provider", "payme")
        if package not in ("top", "hot", "tg_push", "banner"):
            return error_response(
                "validation_error", "Paket noto'g'ri", "Некорректный пакет", 400
            )
        order = create_boost_order(listing, package, provider)
        return Response(
            {
                "order_id": order.id,
                "package": order.package,
                "price_uzs": order.price_uzs,
                "payment_url": order.payment_url,
                "status": order.status,
            },
            status=status.HTTP_201_CREATED,
        )


class ListingLeadView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LeadThrottle]
    throttle_scope = "lead"

    def post(self, request, pk):
        from apps.leads.models import Lead

        listing = get_object_or_404(Listing, pk=pk)
        channel = request.data.get("channel")
        if channel not in dict(Lead.Channel.choices):
            return error_response(
                "validation_error", "Aloqa kanali noto'g'ri", "Некорректный канал", 400
            )
        lead = Lead.objects.create(
            listing=listing,
            user=request.user if request.user.is_authenticated else None,
            channel=channel,
        )

        from apps.telegrambot.tasks import notify_owner_new_lead

        notify_owner_new_lead.delay(lead.id)

        return Response({"id": lead.id, "created_at": lead.created_at}, status=status.HTTP_201_CREATED)
