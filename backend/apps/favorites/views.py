from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import error_response
from apps.listings.models import Listing
from apps.listings.serializers import ListingCardSerializer
from apps.listings.views import _base_queryset

from .models import Compare, Favorite, SavedSearch
from .serializers import SavedSearchSerializer


class _ListingSetView(APIView):
    """Shared GET (list)/POST (add)/DELETE (remove) behaviour for favorites & compare."""

    permission_classes = [permissions.IsAuthenticated]
    model = None
    max_items = None

    def get(self, request):
        listing_ids = self.model.objects.filter(user=request.user).values_list("listing_id", flat=True)
        qs = _base_queryset().filter(id__in=list(listing_ids), status=Listing.Status.ACTIVE)
        return Response(ListingCardSerializer(qs, many=True, context={"request": request}).data)

    def post(self, request):
        listing_id = request.data.get("listing")
        listing = get_object_or_404(Listing, pk=listing_id)
        if self.max_items and self.model.objects.filter(user=request.user).count() >= self.max_items:
            return error_response(
                "limit_reached",
                f"Ko'pi bilan {self.max_items} ta mulk qo'shish mumkin",
                f"Максимум {self.max_items} объектов",
                400,
            )
        obj, _created = self.model.objects.get_or_create(user=request.user, listing=listing)
        return Response({"listing": listing.id}, status=status.HTTP_201_CREATED)

    def delete(self, request, listing_id):
        deleted, _ = self.model.objects.filter(user=request.user, listing_id=listing_id).delete()
        if not deleted:
            return error_response("not_found", "Topilmadi", "Не найдено", 404)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteView(_ListingSetView):
    model = Favorite


class CompareView(_ListingSetView):
    model = Compare
    max_items = 4


class SavedSearchListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = SavedSearch.objects.filter(user=request.user)
        return Response(SavedSearchSerializer(qs, many=True).data)

    def post(self, request):
        serializer = SavedSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save(user=request.user)
        return Response(SavedSearchSerializer(instance).data, status=status.HTTP_201_CREATED)


class SavedSearchDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(SavedSearch, pk=pk, user=request.user)

    def patch(self, request, pk):
        instance = self.get_object(request, pk)
        serializer = SavedSearchSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
