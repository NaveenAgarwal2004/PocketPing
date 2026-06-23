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
    # 1. Separate numbers from adjacent symbols/letters (EXCEPT dot to preserve decimals)
    text = re.sub(r"([a-zA-Z₹:_/-])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-zA-Z₹:_/-])", r"\1 \2", text)

    # 2. Remove currency symbols
    text = text.replace("₹", " ")
    text = text.replace("/-", " ")
    text = re.sub(r"(?i)\b(?:rs\.?|rs:|inr)\b", " ", text)

    # 3. Replace punctuation with space
    text = re.sub(r"[-:_]", " ", text)

    words = text.split()
    if not words:
        return None

    # 3. Extract ALL numeric candidates
    candidates = []
    for i, w in enumerate(words):
        if re.match(r"^\d+(?:\.\d+)?$", w):
            candidates.append((i, float(w), w))

    if not candidates:
        return None

    # 4. Choose most probable expense amount (Last standalone number)
    best_candidate = candidates[-1]
    amount_idx = best_candidate[0]
    amount = best_candidate[2]

    # Find the account: last standalone account keyword
    account = "Cash"
    account_idx = -1
    account_candidates = []

    for i, w in enumerate(words):
        if i == amount_idx:
            continue
        clean_w = w.lower()
        if clean_w in ACCOUNT_DISPLAY:
            account_candidates.append((i, clean_w))

    if account_candidates:
        account_idx, acc_kw = account_candidates[-1]
        account = ACCOUNT_DISPLAY[acc_kw]

    # Build description from remaining words
    desc_parts: list[str] = []
    for i, w in enumerate(words):
        if i == amount_idx:
            continue
        if i == account_idx:
            continue
        desc_parts.append(w)

    desc = " ".join(desc_parts).strip()

    # Normalize descriptions: remove surrounding punctuation and collapse spaces
    desc = desc.strip(" -:_,;")
    desc = re.sub(r"\s+", " ", desc).strip()

    if not desc:
        return None

    return {
        "description": desc,
        "category": detect_category(desc),
        "amount": amount,
        "account": account,
    }
