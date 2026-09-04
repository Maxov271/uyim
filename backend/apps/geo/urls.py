from django.urls import path

from .views import CityListView, DistrictListView, GeoSuggestView

urlpatterns = [
    path("geo/cities", CityListView.as_view(), name="geo-cities"),
    path("geo/districts", DistrictListView.as_view(), name="geo-districts"),
    path("geo/suggest", GeoSuggestView.as_view(), name="geo-suggest"),
]
