from django.conf import settings
from django.db import models


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    listing = models.ForeignKey("listings.Listing", on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "listing")]


class Compare(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="compares")
    listing = models.ForeignKey("listings.Listing", on_delete=models.CASCADE, related_name="compared_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "listing")]


class SavedSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_searches"
    )
    title = models.CharField(max_length=150, blank=True)
    query = models.JSONField(default=dict)
    notify_push = models.BooleanField(default=True)
    notify_telegram = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    last_result_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"SavedSearch #{self.id}"
