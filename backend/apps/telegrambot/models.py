from django.db import models


class TelegramChannel(models.Model):
    username = models.CharField(max_length=64, unique=True, help_text="@chilonzor_uylar")
    chat_id = models.BigIntegerField(null=True, blank=True, help_text="Bot admin qilingach to'ldiriladi")
    district = models.ForeignKey(
        "geo.District", on_delete=models.CASCADE, related_name="telegram_channels"
    )
    agency = models.ForeignKey(
        "agencies.Agency", null=True, blank=True, on_delete=models.SET_NULL, related_name="telegram_channels"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.username


class TelegramPost(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Navbatda"
        POSTED = "posted", "Joylandi"
        FAILED = "failed", "Xatolik"
        SOLD = "sold", "Sotildi belgisi qo'yildi"

    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="telegram_posts"
    )
    channel = models.ForeignKey(TelegramChannel, on_delete=models.CASCADE, related_name="posts")
    message_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    error = models.CharField(max_length=255, blank=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [("listing", "channel")]

    def __str__(self):
        return f"{self.listing_id} → {self.channel} ({self.status})"
