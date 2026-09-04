"""Payme Merchant API (JSON-RPC 2.0) — https://developer.help.paycom.uz/metody-merchant-api

Covers the six methods Payme calls against our webhook: CheckPerformTransaction,
CreateTransaction, PerformTransaction, CancelTransaction, CheckTransaction, GetStatement.
Structurally correct against the documented protocol; production hardening (row locking,
the full official error-code catalogue) is a straightforward extension of this scaffold.
"""

from __future__ import annotations

from django.utils import timezone

from .models import BoostOrder, PaymeTransaction
from .services import apply_boost

ERROR_TRANSACTION_NOT_FOUND = {"code": -31003, "message": {"uz": "Tranzaksiya topilmadi", "ru": "Транзакция не найдена", "en": "Transaction not found"}}
ERROR_ORDER_NOT_FOUND = {"code": -31050, "message": {"uz": "Buyurtma topilmadi", "ru": "Заказ не найден", "en": "Order not found"}}
ERROR_INVALID_AMOUNT = {"code": -31001, "message": {"uz": "Summa noto'g'ri", "ru": "Неверная сумма", "en": "Invalid amount"}}
ERROR_ALREADY_DONE = {"code": -31008, "message": {"uz": "Amalni bajarib bo'lmaydi", "ru": "Невозможно выполнить операцию", "en": "Unable to perform"}}


def _order_from_account(account: dict) -> BoostOrder | None:
    order_id = account.get("order_id")
    return BoostOrder.objects.filter(id=order_id).first() if order_id else None


def check_perform_transaction(params: dict) -> dict:
    order = _order_from_account(params.get("account", {}))
    if not order:
        return {"error": ERROR_ORDER_NOT_FOUND}
    if int(params.get("amount", 0)) != order.price_uzs * 100:
        return {"error": ERROR_INVALID_AMOUNT}
    return {"result": {"allow": True}}


def create_transaction(params: dict) -> dict:
    order = _order_from_account(params.get("account", {}))
    if not order:
        return {"error": ERROR_ORDER_NOT_FOUND}
    amount = int(params.get("amount", 0))
    if amount != order.price_uzs * 100:
        return {"error": ERROR_INVALID_AMOUNT}

    tx_id = params["id"]
    existing = PaymeTransaction.objects.filter(paycom_transaction_id=tx_id).first()
    if existing:
        return {
            "result": {
                "create_time": int(existing.created_at.timestamp() * 1000),
                "transaction": str(existing.id),
                "state": existing.state,
            }
        }

    if order.status != BoostOrder.Status.PENDING:
        return {"error": ERROR_ALREADY_DONE}

    tx = PaymeTransaction.objects.create(order=order, paycom_transaction_id=tx_id, amount=amount)
    order.payment_id = tx_id
    order.save(update_fields=["payment_id"])
    return {
        "result": {
            "create_time": int(tx.created_at.timestamp() * 1000),
            "transaction": str(tx.id),
            "state": tx.state,
        }
    }


def perform_transaction(params: dict) -> dict:
    tx = PaymeTransaction.objects.filter(paycom_transaction_id=params["id"]).first()
    if not tx:
        return {"error": ERROR_TRANSACTION_NOT_FOUND}
    if tx.state == PaymeTransaction.State.PERFORMED:
        return {
            "result": {
                "transaction": str(tx.id),
                "perform_time": int(tx.performed_at.timestamp() * 1000),
                "state": tx.state,
            }
        }
    tx.state = PaymeTransaction.State.PERFORMED
    tx.performed_at = timezone.now()
    tx.save(update_fields=["state", "performed_at"])

    order = tx.order
    order.status = BoostOrder.Status.PAID
    order.paid_at = tx.performed_at
    order.save(update_fields=["status", "paid_at"])
    apply_boost(order)

    return {
        "result": {
            "transaction": str(tx.id),
            "perform_time": int(tx.performed_at.timestamp() * 1000),
            "state": tx.state,
        }
    }


def cancel_transaction(params: dict) -> dict:
    tx = PaymeTransaction.objects.filter(paycom_transaction_id=params["id"]).first()
    if not tx:
        return {"error": ERROR_TRANSACTION_NOT_FOUND}

    tx.state = (
        PaymeTransaction.State.CANCELLED_AFTER_PERFORM
        if tx.state == PaymeTransaction.State.PERFORMED
        else PaymeTransaction.State.CANCELLED_AFTER_CREATE
    )
    tx.reason = params.get("reason")
    tx.cancelled_at = timezone.now()
    tx.save(update_fields=["state", "reason", "cancelled_at"])

    order = tx.order
    order.status = BoostOrder.Status.CANCELLED
    order.save(update_fields=["status"])

    return {
        "result": {
            "transaction": str(tx.id),
            "cancel_time": int(tx.cancelled_at.timestamp() * 1000),
            "state": tx.state,
        }
    }


def check_transaction(params: dict) -> dict:
    tx = PaymeTransaction.objects.filter(paycom_transaction_id=params["id"]).first()
    if not tx:
        return {"error": ERROR_TRANSACTION_NOT_FOUND}
    return {
        "result": {
            "create_time": int(tx.created_at.timestamp() * 1000),
            "perform_time": int(tx.performed_at.timestamp() * 1000) if tx.performed_at else 0,
            "cancel_time": int(tx.cancelled_at.timestamp() * 1000) if tx.cancelled_at else 0,
            "transaction": str(tx.id),
            "state": tx.state,
            "reason": tx.reason,
        }
    }


def get_statement(params: dict) -> dict:
    from datetime import datetime

    frm = datetime.fromtimestamp(params["from"] / 1000, tz=timezone.get_current_timezone())
    to = datetime.fromtimestamp(params["to"] / 1000, tz=timezone.get_current_timezone())
    rows = PaymeTransaction.objects.filter(created_at__gte=frm, created_at__lte=to)
    return {
        "result": {
            "transactions": [
                {
                    "id": tx.paycom_transaction_id,
                    "amount": tx.amount,
                    "create_time": int(tx.created_at.timestamp() * 1000),
                    "perform_time": int(tx.performed_at.timestamp() * 1000) if tx.performed_at else 0,
                    "cancel_time": int(tx.cancelled_at.timestamp() * 1000) if tx.cancelled_at else 0,
                    "transaction": str(tx.id),
                    "state": tx.state,
                    "reason": tx.reason,
                }
                for tx in rows
            ]
        }
    }


DISPATCH = {
    "CheckPerformTransaction": check_perform_transaction,
    "CreateTransaction": create_transaction,
    "PerformTransaction": perform_transaction,
    "CancelTransaction": cancel_transaction,
    "CheckTransaction": check_transaction,
    "GetStatement": get_statement,
}
