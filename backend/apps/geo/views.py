from django.db.models import Q
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import City, District, Mahalla
from .serializers import CitySerializer, DistrictSerializer


class CityListView(generics.ListAPIView):
    queryset = City.objects.all()
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class DistrictListView(generics.ListAPIView):
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = District.objects.select_related("city").prefetch_related("mahallas")
        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city_id=city)
        return qs


class GeoSuggestView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = (request.query_params.get("q") or "").strip().lower()
        hits = []
        if not q:
            return Response(hits)

        for city in City.objects.filter(name__icontains=q)[:5]:
            hits.append({"n": city.name, "k": "Shahar", "v": city.id, "t": "city"})

        for district in District.objects.filter(name__icontains=q).select_related("city")[:5]:
            hits.append({"n": district.name, "k": district.city.name, "v": district.id, "t": "district"})

        for mahalla in Mahalla.objects.filter(name__icontains=q).select_related("district")[:9]:
            hits.append(
                {
                    "n": f"{mahalla.name} mahallasi",
                    "k": mahalla.district.name,
                    "v": mahalla.district_id,
                    "t": "mahalla",
                }
            )

        return Response(hits[:9])
