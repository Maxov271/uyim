from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.agencies.serializers import serialize_agent
from apps.core.currency import get_usd_rate
from apps.developers.models import Developer
from apps.developers.serializers import DeveloperSerializer
from apps.favorites.models import SavedSearch
from apps.favorites.serializers import SavedSearchSerializer
from apps.geo.models import City, District
from apps.geo.serializers import CitySerializer, DistrictSerializer
from apps.listings.models import Listing
from apps.listings.serializers import ListingCardSerializer
from apps.listings.stats import district_stats
from apps.listings.views import _base_queryset
from apps.mortgage.models import Bank
from apps.mortgage.serializers import BankSerializer

from .notifications import build_notifications

User = get_user_model()


class BootstrapView(APIView):
    """One aggregate read that hands the frontend everything data.js used to hardcode —
    see frontend/assets/js/data.js (window.UyimData) for the exact shape this mirrors, and
    frontend/assets/js/data.js's replacement (a single synchronous fetch of this endpoint)
    for how it's consumed.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        districts = District.objects.select_related("city").prefetch_related("mahallas")
        listings = _base_queryset().filter(status=Listing.Status.ACTIVE)

        agents = (
            User.objects.annotate(listings_count=Count("listings"))
            .filter(listings_count__gt=0)
            .select_related("agency")
        )

        ctx = {"request": request}
        data = {
            "CITIES": CitySerializer(City.objects.all(), many=True).data,
            "DISTRICTS": DistrictSerializer(districts, many=True).data,
            "DEAL_TYPES": [{"id": v, "label": l} for v, l in Listing.Deal.choices],
            "PROP_TYPES": [v for v, _ in Listing.PropType.choices],
            "BANKS": BankSerializer(Bank.objects.filter(active=True), many=True).data,
            "DEVELOPERS": DeveloperSerializer(
                Developer.objects.annotate(projects_count=Count("projects")), many=True
            ).data,
            "AGENTS": [serialize_agent(u) for u in agents],
            "LISTINGS": ListingCardSerializer(listings, many=True, context=ctx).data,
            "SAVED_SEARCHES": SavedSearchSerializer(
                SavedSearch.objects.filter(user=request.user) if request.user.is_authenticated else [],
                many=True,
            ).data,
            "DISTRICT_STATS": district_stats(),
            "NOTIFICATIONS": build_notifications(request.user),
            "RATE_UZS": get_usd_rate(),
        }
        return Response(data)
