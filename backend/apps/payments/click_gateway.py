"""Click Merchant API — https://docs.click.uz/en/click-api-request/#merchant-api-request

Two-phase flow: Prepare (action=0) then Complete (action=1), each signed with an MD5 hash
of the request fields + our secret key.
"""

from __future__ import annotations

import hashlib

from django.conf import settings
from django.utils import timezone

from .models import BoostOrder, ClickTransaction
from .services import apply_boost

ERROR_OK = 0
ERROR_SIGN_FAILED = -1
ERROR_ORDER_NOT_FOUND = -5
ERROR_ALREADY_PAID = -4
ERROR_TRANSACTION_NOT_FOUND = -6


def _verify_sign(data: dict, action: str) -> bool:
    parts = [
        data.get("click_trans_id", ""),
        data.get("service_id", ""),
        settings.CLICK_SECRET_KEY,
        data.get("merchant_trans_id", ""),
    ]
    if action == "complete":
        parts.append(data.get("merchant_prepare_id", ""))
    parts += [data.get("amount", ""), data.get("action", ""), data.get("sign_time", "")]
    expected = hashlib.md5("".join(str(p) for p in parts).encode()).hexdigest()
    return expected == data.get("sign_string")


def prepare(data: dict) -> dict:
    if not _verify_sign(data, "prepare"):
        return {"error": ERROR_SIGN_FAILED, "error_note": "Sign xato"}

    order = BoostOrder.objects.filter(id=data.get("merchant_trans_id")).first()
    if not order:
        return {"error": ERROR_ORDER_NOT_FOUND, "error_note": "Buyurtma topilmadi"}

    tx, _ = ClickTransaction.objects.get_or_create(
        order=order,
        click_trans_id=data["click_trans_id"],
        defaults={"amount": data["amount"]},
    )
    tx.prepared = True
    tx.save(update_fields=["prepared"])

    return {
        "click_trans_id": data["click_trans_id"],
        "merchant_trans_id": data["merchant_trans_id"],
        "merchant_prepare_id": tx.id,
        "error": ERROR_OK,
        "error_note": "OK",
    }


def complete(data: dict) -> dict:
    if not _verify_sign(data, "complete"):
        return {"error": ERROR_SIGN_FAILED, "error_note": "Sign xato"}

    tx = ClickTransaction.objects.filter(id=data.get("merchant_prepare_id")).select_related("order").first()
    if not tx:
        return {"error": ERROR_TRANSACTION_NOT_FOUND, "error_note": "Tranzaksiya topilmadi"}
    if tx.confirmed:
        return {"error": ERROR_ALREADY_PAID, "error_note": "Allaqachon to'langan"}

    if str(data.get("error", ERROR_OK)) != str(ERROR_OK):
        return {
            "click_trans_id": data["click_trans_id"],
            "merchant_trans_id": data["merchant_trans_id"],
            "merchant_confirm_id": tx.id,
            "error": ERROR_OK,
            "error_note": "Cancelled by payer, no action taken",
        }

    tx.confirmed = True
    tx.click_paydoc_id = str(data.get("click_paydoc_id", ""))
    tx.save(update_fields=["confirmed", "click_paydoc_id"])

    order = tx.order
    order.status = BoostOrder.Status.PAID
    order.paid_at = timezone.now()
    order.save(update_fields=["status", "paid_at"])
    apply_boost(order)

    return {
        "click_trans_id": data["click_trans_id"],
        "merchant_trans_id": data["merchant_trans_id"],
        "merchant_confirm_id": tx.id,
        "error": ERROR_OK,
        "error_note": "OK",
    }
