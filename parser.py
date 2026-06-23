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
    # 1. Normalize explicit currency symbols that get destroyed by punctuation removal
    text = text.replace('₹', ' ')
    text = text.replace('/-', ' ')

    # 2. Normalize punctuation
    text = re.sub(r'[-:_]', ' ', text)
    # Separate letters and numbers
    text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
    text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)
    
    # 3. Normalize word-based currency symbols AFTER separation
    text = re.sub(r'(?i)\b(?:rs|inr)\b', ' ', text)
    
    words = text.split()
    if not words:
        return None

    # 3. Extract ALL numeric candidates
    candidates = []
    for i, w in enumerate(words):
        if re.match(r'^\d+(?:\.\d+)?$', w):
            candidates.append((i, float(w), w))

    if not candidates:
        return None

    # 4. Choose most probable expense amount (Highest standalone number)
    best_candidate = max(candidates, key=lambda x: x[1])
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
    if not desc:
        return None

    return {
        "description": desc,
        "category":    detect_category(desc),
        "amount":      amount,
        "account":     account,
    }
