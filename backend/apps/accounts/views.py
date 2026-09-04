from django.conf import settings
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.exceptions import error_response
from apps.core.throttling import OTPRequestThrottle

from .models import OTPCode, User
from .serializers import MeSerializer, OTPRequestSerializer, OTPVerifySerializer
from .sms import send_otp_sms


class OTPRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    throttle_classes = [OTPRequestThrottle]

    def post(self, request):
        serializer = OTPRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = User.objects.normalize_phone(serializer.validated_data["phone"])

        static_code = settings.OTP_DEBUG_STATIC_CODE if settings.DEBUG else None
        otp = OTPCode.issue(phone, settings.OTP_TTL_SECONDS, static_code=static_code)
        send_otp_sms(phone, otp.code)

        data = {"phone": phone, "ttl": settings.OTP_TTL_SECONDS}
        if settings.DEBUG:
            data["debug_code"] = otp.code
        return Response(data, status=status.HTTP_200_OK)


class OTPVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = User.objects.normalize_phone(serializer.validated_data["phone"])
        code = serializer.validated_data["code"]

        otp = (
            OTPCode.objects.filter(phone=phone, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if not otp or not otp.is_valid():
            return error_response(
                "otp_expired", "Kod eskirgan, qaytadan so'rang", "Код истёк, запросите заново", 400
            )
        if otp.code != code:
            otp.attempts += 1
            otp.save(update_fields=["attempts"])
            return error_response(
                "otp_invalid", "Kod noto'g'ri", "Неверный код", 400
            )

        otp.is_used = True
        otp.save(update_fields=["is_used"])

        user, created = User.objects.get_or_create(
            phone=phone,
            defaults={"role": serializer.validated_data.get("role", User.Role.BUYER)},
        )
        if not user.verified_phone:
            user.verified_phone = True
            user.save(update_fields=["verified_phone"])

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "is_new": created,
                "user": MeSerializer(user).data,
            }
        )


class TelegramLoginView(APIView):
    """Telegram Login Widget verification — https://core.telegram.org/widgets/login.

    Validates the HMAC-SHA256 hash Telegram signs the payload with using the bot token,
    then links/creates the account by telegram_id.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        import hashlib
        import hmac

        payload = dict(request.data)
        received_hash = payload.pop("hash", None)
        if not settings.TELEGRAM_BOT_TOKEN:
            return error_response(
                "telegram_not_configured",
                "Telegram orqali kirish hozircha sozlanmagan",
                "Вход через Telegram пока не настроен",
                503,
            )
        check_string = "\n".join(f"{k}={payload[k]}" for k in sorted(payload) if payload[k] is not None)
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        computed_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()
        if not received_hash or not hmac.compare_digest(computed_hash, received_hash):
            return error_response(
                "telegram_auth_invalid", "Telegram imzosi noto'g'ri", "Неверная подпись Telegram", 400
            )

        telegram_id = int(payload["id"])
        user, _ = User.objects.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "phone": f"tg:{telegram_id}",
                "name": " ".join(filter(None, [payload.get("first_name"), payload.get("last_name")])),
                "telegram_username": payload.get("username", ""),
            },
        )
        refresh = RefreshToken.for_user(user)
        return Response(
            {"access": str(refresh.access_token), "refresh": str(refresh), "user": MeSerializer(user).data}
        )


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
