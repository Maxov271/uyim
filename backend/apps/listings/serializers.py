from rest_framework import serializers

from apps.agencies.serializers import agent_key_for_user, serialize_agent
from apps.core.geo_utils import jitter_point
from apps.core.humanize_uz import time_ago_uz

from .models import Listing, ListingPhoto
from .stats import month_label_uz


class ListingPhotoSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = ListingPhoto
        fields = ["id", "url", "order", "is_cover"]

    def get_url(self, obj):
        request = self.context.get("request")
        url = obj.image.url
        return request.build_absolute_uri(url) if request else url


def _telegram_live(listing: Listing) -> bool:
    annotated = getattr(listing, "tg_posted_count", None)
    if annotated is not None:
        return annotated > 0
    return listing.telegram_posts.filter(status="posted").exists()


class ListingCardSerializer(serializers.ModelSerializer):
    """Matches the shape of a mock listing produced by L(...) in data.js exactly, so the
    frontend's rendering code (Uyim.propertyCard, badges, priceLabel, …) needs no changes.
    """

    deal = serializers.CharField()
    price = serializers.DecimalField(
        source="price_usd", max_digits=12, decimal_places=2, coerce_to_string=False
    )
    area = serializers.DecimalField(max_digits=8, decimal_places=1, coerce_to_string=False)
    district = serializers.CharField(source="district_id")
    mahalla = serializers.CharField()
    city = serializers.CharField(source="city_id")
    photos = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    verified = serializers.BooleanField(source="verified_owner")
    top = serializers.SerializerMethodField()
    hot = serializers.SerializerMethodField()
    isNew = serializers.SerializerMethodField()
    tg = serializers.SerializerMethodField()
    mortgage = serializers.BooleanField(source="mortgage_allowed")
    created = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    priceHistory = serializers.SerializerMethodField()
    desc = serializers.CharField(source="description")
    metro = serializers.CharField(source="metro_name")
    metroMin = serializers.IntegerField(source="metro_minutes")

    class Meta:
        model = Listing
        fields = [
            "id", "deal", "type", "price", "rooms", "area", "floor", "floors",
            "district", "mahalla", "city", "lat", "lng", "photos", "year", "condition",
            "agent", "verified", "top", "hot", "isNew", "tg", "metro", "metroMin",
            "mortgage", "created", "views", "priceHistory", "features", "desc",
        ]

    def get_photos(self, obj):
        return getattr(obj, "photo_count", None) or obj.photos.count()

    def get_agent(self, obj):
        return agent_key_for_user(obj.owner)

    def get_top(self, obj):
        return obj.is_top

    def get_hot(self, obj):
        return obj.is_hot

    def get_isNew(self, obj):
        return obj.is_new_building

    def get_tg(self, obj):
        return _telegram_live(obj)

    def get_created(self, obj):
        return time_ago_uz(obj.created_at)

    def get_lat(self, obj):
        lat, _ = jitter_point(obj.lat, obj.lng, obj.id)
        return lat

    def get_lng(self, obj):
        _, lng = jitter_point(obj.lat, obj.lng, obj.id)
        return lng

    def get_priceHistory(self, obj):
        history = list(obj.price_history.all())
        if not history:
            return [{"m": month_label_uz(obj.created_at), "v": float(obj.price_usd)}]
        return [{"m": month_label_uz(row.changed_at), "v": float(row.price_usd)} for row in history]


class ListingDetailSerializer(ListingCardSerializer):
    photos = serializers.SerializerMethodField()
    agent_profile = serializers.SerializerMethodField()
    poi = serializers.SerializerMethodField()
    similar = serializers.SerializerMethodField()

    class Meta(ListingCardSerializer.Meta):
        fields = ListingCardSerializer.Meta.fields + [
            "title", "address_hidden", "negotiable", "swap_allowed", "status",
            "agent_profile", "poi", "similar",
        ]

    def get_photos(self, obj):
        return ListingPhotoSerializer(obj.photos.all(), many=True, context=self.context).data

    def get_agent_profile(self, obj):
        return serialize_agent(obj.owner)

    def get_poi(self, obj):
        # Nearby infrastructure (schools, clinics, transport) — hook point for an Overpass
        # API / manually curated POI dataset. Empty until that data source is wired up.
        return []

    def get_similar(self, obj):
        qs = (
            Listing.objects.filter(status=Listing.Status.ACTIVE, district=obj.district, deal=obj.deal)
            .exclude(id=obj.id)
            .order_by("-published_at")[:6]
        )
        return ListingCardSerializer(qs, many=True, context=self.context).data


class ListingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = [
            "deal", "type", "price_usd", "negotiable", "mortgage_allowed", "swap_allowed",
            "rooms", "area", "floor", "floors", "year", "condition",
            "city", "district", "mahalla", "lat", "lng",
            "metro_name", "metro_minutes", "title", "description", "features",
            "cadastre_doc",
        ]

    def validate(self, attrs):
        district = attrs.get("district") or getattr(self.instance, "district", None)
        city = attrs.get("city") or getattr(self.instance, "city", None)
        if district and city and district.city_id != city.id:
            raise serializers.ValidationError({"district": "Tuman tanlangan shahar ichida emas"})
        return attrs
