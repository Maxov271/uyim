from django.urls import path

from .views import TelegramWebhookView

urlpatterns = [
    path("telegram/webhook/<str:secret>", TelegramWebhookView.as_view(), name="telegram-webhook"),
]
