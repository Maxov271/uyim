from django.conf import settings
from django.db import models


class Agency(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="agency"
    )
    name = models.CharField(max_length=150)
    logo = models.ImageField(upload_to="agency_logos/", null=True, blank=True)
    inn = models.CharField("STIR/INN", max_length=20, blank=True)
    license_doc = models.FileField(upload_to="agency_licenses/", null=True, blank=True)
    verified = models.BooleanField(default=False)
    years = models.PositiveSmallIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    founded_at = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Agencies"
        ordering = ["-verified", "-rating"]

    def __str__(self):
        return self.name

    @property
    def active_listings_count(self) -> int:
        return self.user.listings.filter(status="active").count()
