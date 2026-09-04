from django.contrib import admin

from .models import Compare, Favorite, SavedSearch


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ["user", "listing", "created_at"]


@admin.register(Compare)
class CompareAdmin(admin.ModelAdmin):
    list_display = ["user", "listing", "created_at"]


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ["user", "title", "is_active", "notify_telegram", "last_run_at"]
    list_filter = ["is_active", "notify_telegram"]
