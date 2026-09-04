from django.conf import settings
from django.db import models


class Lead(models.Model):
    class Channel(models.TextChoices):
        CALL = "call", "Qo'ng'iroq"
        CHAT = "chat", "Chat"
        TELEGRAM = "telegram", "Telegram"

    listing = models.ForeignKey("listings.Listing", on_delete=models.CASCADE, related_name="leads")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="leads"
    )
    channel = models.CharField(max_length=16, choices=Channel.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["listing", "channel"])]

    def __str__(self):
        return f"{self.listing_id} · {self.channel} · {self.created_at:%Y-%m-%d}"


class ChatThread(models.Model):
    listing = models.ForeignKey(
        "listings.Listing", on_delete=models.CASCADE, related_name="chat_threads"
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_threads_as_buyer"
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_threads_as_seller"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("listing", "buyer")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"Chat #{self.id} · listing {self.listing_id}"


class ChatMessage(models.Model):
    thread = models.ForeignKey(ChatThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.thread_id} · {self.sender_id}: {self.text[:30]}"
