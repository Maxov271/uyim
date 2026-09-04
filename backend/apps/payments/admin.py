from django.contrib import admin

from .models import BoostOrder, ClickTransaction, PaymeTransaction


@admin.register(BoostOrder)
class BoostOrderAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "package", "provider", "price_uzs", "status", "created_at"]
    list_filter = ["package", "provider", "status"]


admin.site.register(PaymeTransaction)
admin.site.register(ClickTransaction)
