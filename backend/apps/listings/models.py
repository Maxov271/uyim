from django.conf import settings
from django.db import models


class Listing(models.Model):
    class Deal(models.TextChoices):
        SALE = "sale", "Sotib olish"
        NEW = "new", "Yangi binolar"
        RENT = "rent", "Uzoq muddat ijara"
        DAILY = "daily", "Kunlik ijara"
        COMMERCIAL = "commercial", "Tijorat"
        LAND = "land", "Yer uchastkasi"

    class PropType(models.TextChoices):
        APARTMENT = "Kvartira", "Kvartira"
        HOUSE = "Hovli uy", "Hovli uy"
        COMMERCIAL = "Tijorat", "Tijorat"
        LAND = "Yer uchastkasi", "Yer uchastkasi"
        OFFICE = "Ofis", "Ofis"
        WAREHOUSE = "Ombor", "Ombor"

    class Status(models.TextChoices):
        DRAFT = "draft", "Qoralama"
        MODERATION = "moderation", "Moderatsiyada"
        ACTIVE = "active", "Faol"
        ARCHIVED = "archived", "Arxivlangan"
        REJECTED = "rejected", "Rad etilgan"

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )
    agency = models.ForeignKey(
        "agencies.Agency", null=True, blank=True, on_delete=models.SET_NULL, related_name="listings"
    )

    deal = models.CharField(max_length=16, choices=Deal.choices)
    type = models.CharField(max_length=32, choices=PropType.choices)

    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    negotiable = models.BooleanField(default=False)
    mortgage_allowed = models.BooleanField(default=True)
    swap_allowed = models.BooleanField(default=False)

    rooms = models.PositiveSmallIntegerField(default=0)
    area = models.DecimalField(max_digits=8, decimal_places=1)
    floor = models.PositiveSmallIntegerField(default=0)
    floors = models.PositiveSmallIntegerField(default=0)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    condition = models.CharField(max_length=64, blank=True)

    city = models.ForeignKey("geo.City", on_delete=models.PROTECT, related_name="listings")
    district = models.ForeignKey("geo.District", on_delete=models.PROTECT, related_name="listings")
    mahalla = models.CharField(max_length=120, blank=True)

    lat = models.FloatField()
    lng = models.FloatField()
    address_hidden = models.BooleanField(default=True)

    metro_name = models.CharField(max_length=64, blank=True)
    metro_minutes = models.PositiveSmallIntegerField(null=True, blank=True)

    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    features = models.JSONField(default=list, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    rejection_reason = models.CharField(max_length=255, blank=True)
    verified_owner = models.BooleanField(default=False)
    cadastre_doc = models.FileField(upload_to="cadastre/", null=True, blank=True)

    top_until = models.DateTimeField(null=True, blank=True)
    hot_until = models.DateTimeField(null=True, blank=True)

    views = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "deal", "district"]),
            models.Index(fields=["status", "city"]),
        ]

    def __str__(self):
        return f"{self.get_deal_display()} · {self.type} · {self.price_usd}$"

    @property
    def is_top(self) -> bool:
        from django.utils import timezone

        return bool(self.top_until and self.top_until > timezone.now())

    @property
    def is_hot(self) -> bool:
        from django.utils import timezone

        return bool(self.hot_until and self.hot_until > timezone.now())

    @property
    def is_new_building(self) -> bool:
        return self.deal == self.Deal.NEW


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="photos")
    image = models.ImageField(upload_to="listings/%Y/%m/")
    order = models.PositiveSmallIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.listing_id} · foto #{self.order}"


class PriceHistory(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="price_history")
    price_usd = models.DecimalField(max_digits=12, decimal_places=2)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["changed_at"]
        verbose_name_plural = "Price histories"

    def __str__(self):
        return f"{self.listing_id} · {self.price_usd}$ · {self.changed_at:%Y-%m-%d}"
