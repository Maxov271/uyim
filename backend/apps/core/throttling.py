"""Rate limits from CLAUDE_CODE_PROMPT.md §10: search 60/min, OTP 3/10min, lead 10/soat."""

from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle, SimpleRateThrottle


class OTPRequestThrottle(SimpleRateThrottle):
    """3 requests / 10 minutes — DRF's rate-string grammar can't express a 10-minute window
    (it only understands whole second/min/hour/day units), so the duration is set directly.
    """

    scope = "otp_request"

    def parse_rate(self, rate):
        return 3, 600

    def get_cache_key(self, request, view):
        phone = (request.data or {}).get("phone") or self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": phone}


class SearchThrottle(AnonRateThrottle):
    scope = "search"
    rate = "60/min"


class LeadThrottle(ScopedRateThrottle):
    scope = "lead"
