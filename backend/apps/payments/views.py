import base64
import binascii

from django.conf import settings
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from . import click_gateway, payme_gateway


class PaymeWebhookView(APIView):
    """Single JSON-RPC 2.0 endpoint Payme POSTs all six merchant-API methods to."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        if not self._authorized(request):
            return Response(
                {"error": {"code": -32504, "message": "Insufficient privilege"}}, status=200
            )

        body = request.data
        method = body.get("method")
        handler = payme_gateway.DISPATCH.get(method)
        if not handler:
            return Response(
                {"error": {"code": -32601, "message": "Method not found"}, "id": body.get("id")}
            )

        result = handler(body.get("params", {}))
        result["id"] = body.get("id")
        return Response(result)

    @staticmethod
    def _authorized(request) -> bool:
        header = request.headers.get("Authorization", "")
        if not header.startswith("Basic "):
            return False
        try:
            decoded = base64.b64decode(header[6:]).decode()
        except (binascii.Error, UnicodeDecodeError):
            return False
        _, _, key = decoded.partition(":")
        return key in (settings.PAYME_SECRET_KEY, settings.PAYME_TEST_KEY) and bool(key)


class ClickPrepareView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(click_gateway.prepare(request.data))


class ClickCompleteView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        return Response(click_gateway.complete(request.data))
