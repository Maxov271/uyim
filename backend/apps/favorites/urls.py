from django.urls import path

from .views import (
    CompareView,
    FavoriteView,
    SavedSearchDetailView,
    SavedSearchListCreateView,
)

urlpatterns = [
    path("favorites", FavoriteView.as_view(), name="favorites"),
    path("favorites/<int:listing_id>", FavoriteView.as_view(), name="favorite-detail"),
    path("compare", CompareView.as_view(), name="compare"),
    path("compare/<int:listing_id>", CompareView.as_view(), name="compare-detail"),
    path("saved-searches", SavedSearchListCreateView.as_view(), name="saved-search-list"),
    path("saved-searches/<int:pk>", SavedSearchDetailView.as_view(), name="saved-search-detail"),
]
