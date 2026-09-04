from django.urls import path

from .views import (
    ListingBoostView,
    ListingDetailView,
    ListingLeadView,
    ListingListCreateView,
    ListingPhotoUploadView,
)

urlpatterns = [
    path("listings", ListingListCreateView.as_view(), name="listing-list-create"),
    path("listings/<int:pk>", ListingDetailView.as_view(), name="listing-detail"),
    path("listings/<int:pk>/photos", ListingPhotoUploadView.as_view(), name="listing-photos"),
    path(
        "listings/<int:pk>/photos/<int:photo_id>",
        ListingPhotoUploadView.as_view(),
        name="listing-photo-detail",
    ),
    path("listings/<int:pk>/boost", ListingBoostView.as_view(), name="listing-boost"),
    path("listings/<int:pk>/lead", ListingLeadView.as_view(), name="listing-lead"),
]
