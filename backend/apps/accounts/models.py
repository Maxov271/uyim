import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("Telefon raqami majburiy")
        phone = self.normalize_phone(phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.MODERATOR)
        return self._create_user(phone, password, **extra_fields)

    @staticmethod
    def normalize_phone(phone: str) -> str:
        digits = "".join(ch for ch in phone if ch.isdigit())
        if not digits.startswith("998") and len(digits) == 9:
            digits = "998" + digits
        return "+" + digits


class User(AbstractUser):
    class Role(models.TextChoices):
        BUYER = "buyer", "Xaridor"
        OWNER = "owner", "Uy egasi"
        AGENCY = "agency", "Agentlik"
        DEVELOPER = "developer", "Quruvchi"
        MODERATOR = "moderator", "Moderator"

    username = None
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=16, choices=Role.choices, default=Role.BUYER)
    city = models.ForeignKey(
        "geo.City", null=True, blank=True, on_delete=models.SET_NULL, related_name="users"
    )
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_username = models.CharField(max_length=64, blank=True)
    verified_phone = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    intents = models.JSONField(default=list, blank=True)  # ["sale","rent",...] onboarding chips
    notify_telegram = models.BooleanField(default=True)
    notify_push = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.name or self.phone


class OTPCode(models.Model):
    class Purpose(models.TextChoices):
        LOGIN = "login", "Kirish"

    phone = models.CharField(max_length=20, db_index=True)
    code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=16, choices=Purpose.choices, default=Purpose.LOGIN)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["phone", "is_used"])]

    @classmethod
    def issue(cls, phone: str, ttl_seconds: int, static_code: str | None = None) -> "OTPCode":
        code = static_code or f"{random.randint(0, 9999):04d}"
        return cls.objects.create(
            phone=phone, code=code, expires_at=timezone.now() + timedelta(seconds=ttl_seconds)
        )

    def is_valid(self) -> bool:
        return not self.is_used and self.expires_at >= timezone.now()

    def __str__(self):
        return f"{self.phone} · {self.code}"
