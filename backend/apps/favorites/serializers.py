from rest_framework import serializers

from .models import SavedSearch


class SavedSearchSerializer(serializers.ModelSerializer):
    meta = serializers.SerializerMethodField()
    on = serializers.BooleanField(source="is_active")
    tg = serializers.BooleanField(source="notify_telegram")

    class Meta:
        model = SavedSearch
        fields = [
            "id", "title", "query", "notify_push", "tg", "on",
            "last_run_at", "last_result_count", "meta", "created_at",
        ]
        read_only_fields = ["id", "last_run_at", "last_result_count", "meta", "created_at"]

    def get_meta(self, obj):
        if not obj.last_run_at:
            return "Hali tekshirilmagan"
        if obj.last_result_count:
            return f"{obj.last_result_count} yangi e'lon"
        return "Yangilik yo'q"
