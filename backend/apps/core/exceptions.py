"""Uniform error shape for the whole API: {code, message_uz, message_ru}
as required by CLAUDE_CODE_PROMPT.md §10.
"""

from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import exception_handler


_MESSAGES_RU = {
    "not_found": "Ресурс не найден",
    "permission_denied": "Доступ запрещён",
    "authentication_failed": "Ошибка аутентификации",
    "not_authenticated": "Требуется авторизация",
    "validation_error": "Данные введены неверно",
    "throttled": "Слишком много запросов, попробуйте позже",
    "parse_error": "Некорректный запрос",
    "method_not_allowed": "Метод не поддерживается",
    "server_error": "Внутренняя ошибка сервера",
}

_MESSAGES_UZ_DEFAULT = "Xatolik yuz berdi"


def _code_for(exc) -> str:
    name = exc.__class__.__name__
    mapping = {
        "NotFound": "not_found",
        "PermissionDenied": "permission_denied",
        "AuthenticationFailed": "authentication_failed",
        "NotAuthenticated": "not_authenticated",
        "ValidationError": "validation_error",
        "Throttled": "throttled",
        "ParseError": "parse_error",
        "MethodNotAllowed": "method_not_allowed",
    }
    return mapping.get(name, "server_error")


def uz_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    code = _code_for(exc)
    detail = response.data

    if isinstance(detail, dict) and "message_uz" in detail:
        # Already formatted by the view (e.g. a domain-specific error).
        return response

    message_uz = getattr(exc, "default_detail", None) or _MESSAGES_UZ_DEFAULT
    if isinstance(detail, dict):
        first = next(iter(detail.values()), None)
        if isinstance(first, list) and first:
            message_uz = str(first[0])
        elif isinstance(first, str):
            message_uz = first
    elif isinstance(detail, list) and detail:
        message_uz = str(detail[0])
    elif isinstance(detail, str):
        message_uz = detail

    response.data = {
        "code": code,
        "message_uz": str(message_uz),
        "message_ru": _MESSAGES_RU.get(code, "Произошла ошибка"),
    }
    return response


def error_response(code: str, message_uz: str, message_ru: str, status_code: int = 400) -> Response:
    return Response(
        {"code": code, "message_uz": message_uz, "message_ru": message_ru},
        status=status_code,
    )
