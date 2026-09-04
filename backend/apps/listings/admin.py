from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Listing, ListingPhoto, PriceHistory


class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 0
    fields = ["image", "order", "is_cover"]


class PriceHistoryInline(admin.TabularInline):
    model = PriceHistory
    extra = 0
    readonly_fields = ["price_usd", "changed_at"]
    can_delete = False


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = [
        "id", "title_or_type", "deal", "status", "price_usd", "district", "owner",
        "verified_owner", "top_badge", "hot_badge", "views", "created_at",
    ]
    list_filter = ["status", "deal", "type", "city", "district", "verified_owner"]
    search_fields = ["title", "description", "owner__phone", "owner__name", "mahalla"]
    autocomplete_fields = ["owner", "agency", "city", "district"]
    readonly_fields = ["views", "created_at", "updated_at", "published_at"]
    inlines = [ListingPhotoInline, PriceHistoryInline]
    actions = [
        "approve_listings", "reject_listings", "archive_listings",
        "mark_verified_owner", "boost_top_7d", "boost_hot_3d",
    ]

    @admin.display(description="Sarlavha")
    def title_or_type(self, obj):
        return obj.title or f"{obj.type} · {obj.rooms} xona"

    @admin.display(description="TOP", boolean=True)
    def top_badge(self, obj):
        return obj.is_top

    @admin.display(description="HOT", boolean=True)
    def hot_badge(self, obj):
        return obj.is_hot

    @admin.action(description="Tasdiqlash (moderatsiyadan → faol)")
    def approve_listings(self, request, queryset):
        updated = queryset.update(status=Listing.Status.ACTIVE)
        self.message_user(request, f"{updated} ta e'lon faollashtirildi")

    @admin.action(description="Rad etish")
    def reject_listings(self, request, queryset):
        updated = queryset.update(status=Listing.Status.REJECTED)
        self.message_user(request, f"{updated} ta e'lon rad etildi")

    @admin.action(description="Arxivlash")
    def archive_listings(self, request, queryset):
        updated = queryset.update(status=Listing.Status.ARCHIVED)
        self.message_user(request, f"{updated} ta e'lon arxivlandi")

    @admin.action(description="Tasdiqlangan egasi deb belgilash")
    def mark_verified_owner(self, request, queryset):
        queryset.update(verified_owner=True)

    @admin.action(description="TOP qilish (+7 kun)")
    def boost_top_7d(self, request, queryset):
        from datetime import timedelta

        queryset.update(top_until=timezone.now() + timedelta(days=7))

    @admin.action(description="HOT qilish (+3 kun)")
    def boost_hot_3d(self, request, queryset):
        from datetime import timedelta

        queryset.update(hot_until=timezone.now() + timedelta(days=3))


@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ["listing", "order", "is_cover", "preview"]

    @admin.display(description="Ko'rinish")
    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.image.url)
