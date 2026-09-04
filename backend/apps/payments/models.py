from django.db import models


class BoostOrder(models.Model):
    class Package(models.TextChoices):
        TOP = "top", "TOP joylashuv"
        HOT = "hot", "HOT belgisi"
        TG_PUSH = "tg_push", "Telegram push"
        BANNER = "banner", "Banner reklama"

    class Provider(models.TextChoices):
        PAYME = "payme", "Payme"
        CLICK = "click", "Click"

    class Status(models.TextChoices):
        PENDING = "pending", "To'lov kutilmoqda"
        PAID = "paid", "To'landi"
        CANCELLED = "cancelled", "Bekor qilindi"

    listing = models.ForeignKey("listings.Listing", on_delete=models.CASCADE, related_name="boost_orders")
    package = models.CharField(max_length=16, choices=Package.choices)
    provider = models.CharField(max_length=16, choices=Provider.choices, default=Provider.PAYME)
    price_uzs = models.PositiveIntegerField()
    payment_id = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    @property
    def payment_url(self) -> str:
        from .services import build_payment_url

        return build_payment_url(self)

    def __str__(self):
        return f"#{self.id} · {self.listing_id} · {self.package} · {self.price_uzs} so'm"


class PaymeTransaction(models.Model):
    class State(models.IntegerChoices):
        CREATED = 1, "Yaratildi"
        PERFORMED = 2, "Bajarildi"
        CANCELLED_AFTER_CREATE = -1, "Bekor (yaratilgandan keyin)"
        CANCELLED_AFTER_PERFORM = -2, "Bekor (bajarilgandan keyin)"

    order = models.ForeignKey(BoostOrder, on_delete=models.CASCADE, related_name="payme_transactions")
    paycom_transaction_id = models.CharField(max_length=32, unique=True)
    amount = models.PositiveIntegerField(help_text="tiyin")
    state = models.SmallIntegerField(choices=State.choices, default=State.CREATED)
    reason = models.PositiveSmallIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    performed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


class ClickTransaction(models.Model):
    order = models.ForeignKey(BoostOrder, on_delete=models.CASCADE, related_name="click_transactions")
    click_trans_id = models.CharField(max_length=32)
    click_paydoc_id = models.CharField(max_length=32, blank=True)
    amount = models.PositiveIntegerField(help_text="so'm")
    prepared = models.BooleanField(default=False)
    confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
