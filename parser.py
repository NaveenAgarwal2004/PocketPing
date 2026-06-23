"""Expense text parser — extracts description, amount, category, account."""

import re

from config import CATEGORIES, ACCOUNT_DISPLAY


def detect_category(text: str) -> str:
    """Match text against category keywords. Returns first match or 'Other'."""
    lower = text.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in lower:
                return cat
    return "Other"


def parse_expense(text: str) -> dict[str, str] | None:
    """Parse 'description amount [account]' into structured expense dict.

    Returns None if no amount found or description is empty.
    """
    text = text.strip()
    match = re.search(r'(\d+(?:\.\d+)?)', text)
    if not match:
        return None
    amount = match.group(1)
    rest = (text[:match.start()] + " " + text[match.end():]).strip()
    words = rest.split()
    account = "Cash"
    desc_parts: list[str] = []
    for w in words:
        if w.lower() in ACCOUNT_DISPLAY:
            account = ACCOUNT_DISPLAY[w.lower()]
        else:
            desc_parts.append(w)
    desc = " ".join(desc_parts).strip()
    if not desc:
        return None
    return {
        "description": desc.title(),
        "category":    detect_category(desc),
        "amount":      amount,
        "account":     account,
    }
