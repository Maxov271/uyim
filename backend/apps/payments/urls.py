from django.urls import path

from .views import ClickCompleteView, ClickPrepareView, PaymeWebhookView

urlpatterns = [
    path("payments/payme/webhook", PaymeWebhookView.as_view(), name="payme-webhook"),
    path("payments/click/prepare", ClickPrepareView.as_view(), name="click-prepare"),
    path("payments/click/complete", ClickCompleteView.as_view(), name="click-complete"),
]
