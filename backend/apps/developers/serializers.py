from rest_framework import serializers

from .models import Developer, Project


class DeveloperSerializer(serializers.ModelSerializer):
    city = serializers.CharField(source="city.name")
    projects = serializers.IntegerField(source="projects_count")

    class Meta:
        model = Developer
        fields = ["id", "name", "logo", "city", "projects", "description", "founded_year"]


class ProjectSerializer(serializers.ModelSerializer):
    developer = serializers.CharField(source="developer.name")
    developer_id = serializers.IntegerField(source="developer.id")
    district = serializers.CharField(source="district.name")
    city = serializers.CharField(source="city_id")
    price_from_usd = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False, allow_null=True
    )

    class Meta:
        model = Project
        fields = [
            "id", "name", "developer", "developer_id", "city", "district", "lat", "lng",
            "stage", "completion_label", "price_from_usd", "installment_available",
            "tour_3d_url", "cover_image", "description",
        ]
