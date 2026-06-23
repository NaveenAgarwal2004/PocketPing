"""Application configuration — env vars, constants, logging setup."""

import logging
import os

# ── Logging (configure before other modules import) ──────────────────────
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ── Environment ──────────────────────────────────────────────────────────
BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
SHEET_ID: str = os.environ["GOOGLE_SHEET_ID"]
CREDS_FILE: str = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
ALLOWED_USER_IDS: set[str] = set(os.environ.get("ALLOWED_USER_IDS", "").split(","))
PORT: int = int(os.environ.get("PORT", 10000))

# ── Google API Scopes ────────────────────────────────────────────────────
SCOPES: list[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Category keywords ────────────────────────────────────────────────────
CATEGORIES: dict[str, list[str]] = {
    "Transport": ["uber", "ola", "auto", "bike", "taxi", "cab", "rapido", "rickshaw"],
    "Metro": ["metro", "dmrc", "card recharge", "metro recharge"],
    "Food": [
        "food",
        "lunch",
        "dinner",
        "breakfast",
        "chai",
        "tea",
        "coffee",
        "juice",
        "snack",
        "biryani",
        "pizza",
        "restaurant",
        "dhaba",
        "swiggy",
        "zomato",
        "thali",
        "roti",
    ],
    "Bills": [
        "bill",
        "electricity",
        "light bill",
        "water bill",
        "recharge",
        "internet",
        "wifi",
        "broadband",
        "gas",
    ],
    "Home": [
        "repair",
        "maintenance",
        "plumber",
        "electrician",
        "carpenter",
        "paint",
        "home",
        "furniture",
        "rent",
    ],
    "Entertainment": [
        "movie",
        "cinema",
        "pvr",
        "inox",
        "netflix",
        "hotstar",
        "concert",
        "show",
        "game",
    ],
    "Shopping": [
        "shopping",
        "clothes",
        "shirt",
        "shoes",
        "amazon",
        "flipkart",
        "myntra",
        "meesho",
        "kirana",
        "grocery",
    ],
    "Health": [
        "medicine",
        "doctor",
        "pharmacy",
        "hospital",
        "clinic",
        "chemist",
        "medical",
        "test",
    ],
    "Other": [],
}

# ── Account display names ────────────────────────────────────────────────
ACCOUNT_DISPLAY: dict[str, str] = {
    "bob": "BOB",
    "indusind": "IndusInd",
    "cash": "Cash",
    "upi": "UPI",
    "gpay": "GPay",
    "phonepe": "PhonePe",
    "paytm": "Paytm",
    "other": "Other",
}
