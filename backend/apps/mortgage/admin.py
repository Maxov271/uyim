from django.contrib import admin

from .models import Bank, MortgageApplication


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "rate", "min_down_pct", "max_term_years", "active"]
    list_filter = ["active"]


@admin.register(MortgageApplication)
class MortgageApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "bank", "price_usd", "down_pct", "years", "status", "created_at"]
    list_filter = ["status", "bank"]
    actions = ["mark_approved", "mark_rejected"]

    @admin.action(description="Tasdiqlash")
    def mark_approved(self, request, queryset):
        queryset.update(status=MortgageApplication.Status.APPROVED)

    @admin.action(description="Rad etish")
    def mark_rejected(self, request, queryset):
        queryset.update(status=MortgageApplication.Status.REJECTED)
