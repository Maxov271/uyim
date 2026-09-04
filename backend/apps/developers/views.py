from django.db.models import Count
from rest_framework import generics, permissions

from .models import Developer, Project
from .serializers import DeveloperSerializer, ProjectSerializer


class DeveloperListView(generics.ListAPIView):
    serializer_class = DeveloperSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Developer.objects.select_related("city").annotate(projects_count=Count("projects"))


class ProjectListView(generics.ListAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = Project.objects.select_related("developer", "city", "district")
        params = self.request.query_params
        if params.get("developer"):
            qs = qs.filter(developer_id=params["developer"])
        if params.get("city"):
            qs = qs.filter(city_id=params["city"])
        if params.get("district"):
            qs = qs.filter(district_id=params["district"])
        return qs
