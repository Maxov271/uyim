from django.contrib import admin

from .models import Developer, Project


class ProjectInline(admin.TabularInline):
    model = Project
    extra = 0
    fields = ["name", "district", "stage", "completion_label", "price_from_usd"]


@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ["name", "city", "founded_year"]
    inlines = [ProjectInline]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "developer", "district", "stage", "price_from_usd", "installment_available"]
    list_filter = ["stage", "installment_available", "city"]
