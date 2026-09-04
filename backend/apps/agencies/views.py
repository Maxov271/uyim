from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.exceptions import error_response
from apps.core.humanize_uz import time_ago_uz  # noqa: F401 (kept for future profile fields)

from .models import Agency
from .serializers import serialize_agent

User = get_user_model()


class AgentDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, agent_id: str):
        if not agent_id.startswith("u"):
            return error_response("not_found", "Agent topilmadi", "Агент не найден", 404)
        user = User.objects.filter(id=agent_id[1:]).first()
        if not user:
            return error_response("not_found", "Agent topilmadi", "Агент не найден", 404)
        return Response(serialize_agent(user))


class AgencyAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, agency_id: int):
        agency = Agency.objects.filter(id=agency_id).first()
        if not agency:
            return error_response("not_found", "Agentlik topilmadi", "Агентство не найдено", 404)
        if agency.user_id != request.user.id and request.user.role != "moderator":
            return error_response("permission_denied", "Ruxsat yo'q", "Доступ запрещён", 403)

        listings = agency.user.listings.all()
        since = timezone.now() - timedelta(days=14)
        views_by_day = (
            listings.filter(published_at__gte=since)
            .values("published_at__date")
            .annotate(views=Sum("views"))
            .order_by("published_at__date")
        )
        from apps.leads.models import Lead

        leads_by_channel = {
            row["channel"]: row["n"]
            for row in Lead.objects.filter(listing__owner=agency.user)
            .values("channel")
            .annotate(n=Count("id"))
        }

        return Response(
            {
                "listings_total": listings.count(),
                "listings_active": listings.filter(status="active").count(),
                "views_total": listings.aggregate(v=Sum("views"))["v"] or 0,
                "calls_total": leads_by_channel.get("call", 0),
                "tg_leads_total": leads_by_channel.get("telegram", 0),
                "views_by_day": [
                    {"date": str(row["published_at__date"]), "views": row["views"] or 0}
                    for row in views_by_day
                ],
                "leads_by_channel": leads_by_channel,
            }
        )
