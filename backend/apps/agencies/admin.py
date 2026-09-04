from django.contrib import admin

from .models import Agency


@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ["name", "user", "verified", "years", "rating", "active_listings_count"]
    list_filter = ["verified"]
    search_fields = ["name", "inn", "user__phone"]
    actions = ["mark_verified", "mark_unverified"]

    @admin.action(description="Ishonchli agentlik deb belgilash")
    def mark_verified(self, request, queryset):
        queryset.update(verified=True)

    @admin.action(description="Tasdiqni bekor qilish")
    def mark_unverified(self, request, queryset):
        queryset.update(verified=False)
