from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import OTPCode, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ["-created_at"]
    list_display = ["phone", "name", "role", "city", "verified_phone", "is_staff", "created_at"]
    list_filter = ["role", "verified_phone", "is_staff", "city"]
    search_fields = ["phone", "name", "telegram_username"]
    fieldsets = (
        (None, {"fields": ("phone", "password")}),
        ("Shaxsiy", {"fields": ("name", "email", "avatar", "city", "role", "intents")}),
        (
            "Telegram",
            {"fields": ("telegram_id", "telegram_username", "notify_telegram", "notify_push")},
        ),
        (
            "Ruxsatlar",
            {"fields": ("verified_phone", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Sanalar", {"fields": ("last_login", "created_at")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("phone", "password1", "password2", "role")}),
    )
    readonly_fields = ["created_at"]


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ["phone", "code", "purpose", "is_used", "created_at", "expires_at"]
    list_filter = ["purpose", "is_used"]
    search_fields = ["phone"]
