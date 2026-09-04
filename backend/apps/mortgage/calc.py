"""Same formula the frontend already implements client-side (frontend/assets/js/ui.js →
mortgage()) so calculator.html's live preview and the server-confirmed figure always match:
monthly = loan * i / (1 - (1+i)^-n), i = rate/100/12, n = years*12.
"""

from __future__ import annotations


def calc_mortgage(price: float, down_pct: float, years: int, rate: float) -> dict:
    down = price * down_pct / 100
    loan = price - down
    i = rate / 100 / 12
    n = years * 12
    monthly = loan / n if i == 0 else loan * i / (1 - (1 + i) ** -n)
    total = monthly * n
    return {
        "down": round(down, 2),
        "loan": round(loan, 2),
        "monthly": round(monthly, 2),
        "total": round(total, 2),
        "interest": round(total - loan, 2),
        "incomeNeeded": round(monthly / 0.5, 2),
    }
