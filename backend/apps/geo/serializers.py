from rest_framework import serializers

from .models import City, District, Mahalla


class CitySerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()

    class Meta:
        model = City
        fields = ["id", "name", "center", "zoom"]

    def get_center(self, obj):
        return [obj.lat, obj.lng]


class DistrictSerializer(serializers.ModelSerializer):
    center = serializers.SerializerMethodField()
    city = serializers.CharField(source="city_id")
    ppm = serializers.SerializerMethodField()
    mahallas = serializers.SerializerMethodField()

    class Meta:
        model = District
        fields = ["id", "city", "name", "center", "ppm", "mahallas"]

    def get_center(self, obj):
        return [obj.lat, obj.lng]

    def get_mahallas(self, obj):
        names = getattr(obj, "_mahalla_names", None)
        if names is not None:
            return names
        return list(obj.mahallas.values_list("name", flat=True))

    def get_ppm(self, obj):
        from apps.listings.stats import district_ppm

        return district_ppm(obj.id)
