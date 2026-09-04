from django.contrib import admin

from .models import TelegramChannel, TelegramPost


@admin.register(TelegramChannel)
class TelegramChannelAdmin(admin.ModelAdmin):
    list_display = ["username", "district", "agency", "active"]
    list_filter = ["active", "district__city"]
    search_fields = ["username"]


@admin.register(TelegramPost)
class TelegramPostAdmin(admin.ModelAdmin):
    list_display = ["listing", "channel", "status", "posted_at"]
    list_filter = ["status", "channel"]
