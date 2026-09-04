"""AgentSerializer normalizes either an Agency *or* a plain owner User into the single
{id, name, type, verified, years, listings, rating, phone, tg} shape the frontend's
D.AGENTS array (and `l.agent` lookups) expect — see frontend/assets/js/data.js AGENTS.
"""

from rest_framework import serializers


def agent_key_for_user(user) -> str:
    return f"u{user.id}"


def serialize_agent(user) -> dict:
    agency = getattr(user, "agency", None)
    listings_count = user.listings.filter(status="active").count()
    if agency:
        return {
            "id": agent_key_for_user(user),
            "name": agency.name,
            "type": "agency",
            "verified": agency.verified,
            "years": agency.years,
            "listings": listings_count,
            "rating": float(agency.rating),
            "phone": user.phone,
            "tg": f"@{user.telegram_username}" if user.telegram_username else "",
        }
    return {
        "id": agent_key_for_user(user),
        "name": user.name or user.phone,
        "type": "owner",
        "verified": user.verified_phone,
        "years": 0,
        "listings": listings_count,
        "rating": 0,
        "phone": user.phone,
        "tg": f"@{user.telegram_username}" if user.telegram_username else "",
    }


class AgentSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    type = serializers.ChoiceField(choices=["agency", "owner"])
    verified = serializers.BooleanField()
    years = serializers.IntegerField()
    listings = serializers.IntegerField()
    rating = serializers.FloatField()
    phone = serializers.CharField()
    tg = serializers.CharField(allow_blank=True)


class AgencyAnalyticsSerializer(serializers.Serializer):
    listings_total = serializers.IntegerField()
    listings_active = serializers.IntegerField()
    views_total = serializers.IntegerField()
    calls_total = serializers.IntegerField()
    tg_leads_total = serializers.IntegerField()
    views_by_day = serializers.ListField(child=serializers.DictField())
    leads_by_channel = serializers.DictField()
