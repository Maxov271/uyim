from django.contrib import admin

from .models import City, District, Mahalla


class MahallaInline(admin.TabularInline):
    model = Mahalla
    extra = 1


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "lat", "lng", "zoom"]
    search_fields = ["id", "name"]


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "city", "lat", "lng"]
    list_filter = ["city"]
    search_fields = ["id", "name"]
    inlines = [MahallaInline]


@admin.register(Mahalla)
class MahallaAdmin(admin.ModelAdmin):
    list_display = ["name", "district"]
    list_filter = ["district__city", "district"]
    search_fields = ["name"]
