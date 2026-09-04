from django.contrib import admin

from .models import ChatMessage, ChatThread, Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["listing", "channel", "user", "created_at"]
    list_filter = ["channel"]
    date_hierarchy = "created_at"


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["sender", "text", "created_at", "read_at"]


@admin.register(ChatThread)
class ChatThreadAdmin(admin.ModelAdmin):
    list_display = ["id", "listing", "buyer", "seller", "created_at"]
    inlines = [ChatMessageInline]
