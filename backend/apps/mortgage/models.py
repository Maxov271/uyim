from django.conf import settings
from django.db import models


class Bank(models.Model):
    id = models.SlugField(primary_key=True, max_length=32)
    name = models.CharField(max_length=120)
    rate = models.DecimalField("Yillik foiz, %", max_digits=5, decimal_places=2)
    min_down_pct = models.PositiveSmallIntegerField("Min. boshlang'ich to'lov, %")
    max_term_years = models.PositiveSmallIntegerField("Max. muddat, yil")
    note = models.CharField(max_length=200, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["rate"]

    def __str__(self):
        return self.name


class MortgageApplication(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Yangi"
        REVIEW = "review", "Ko'rib chiqilmoqda"
        APPROVED = "approved", "Tasdiqlangan"
        REJECTED = "rejected", "Rad etilgan"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mortgage_applications"
    )
    listing = models.ForeignKey(
        "listings.Listing", null=True, blank=True, on_delete=models.SET_NULL, related_name="mortgage_applications"
    )
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, related_name="applications")
    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    down_pct = models.PositiveSmallIntegerField()
    years = models.PositiveSmallIntegerField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} · {self.bank_id} · {self.price_usd}$"
