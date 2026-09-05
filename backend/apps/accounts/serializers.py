from rest_framework import serializers

from .models import OTPCode, User


class MeSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(slug_field="id", read_only=True)
    city_id = serializers.CharField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "name",
            "role",
            "city",
            "city_id",
            "telegram_id",
            "telegram_username",
            "verified_phone",
            "avatar",
            "intents",
            "notify_telegram",
            "notify_push",
            "created_at",
        ]
        read_only_fields = ["id", "phone", "verified_phone", "telegram_id", "created_at"]

    def update(self, instance, validated_data):
        city_id = validated_data.pop("city_id", serializers.empty)
        if city_id is not serializers.empty:
            from apps.geo.models import City

            instance.city = City.objects.filter(id=city_id).first() if city_id else None
        return super().update(instance, validated_data)


class OTPRequestSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    channel = serializers.ChoiceField(choices=OTPCode.Channel.choices, default=OTPCode.Channel.SMS)


class OTPVerifySerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    code = serializers.CharField(max_length=6)
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)
