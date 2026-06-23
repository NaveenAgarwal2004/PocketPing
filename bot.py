import os
import re
import json
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import gspread
from google.oauth2.service_account import Credentials

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Config ────────────────────────────────────────────────────────────────────
BOT_TOKEN        = os.environ["TELEGRAM_BOT_TOKEN"]
SHEET_ID         = os.environ["GOOGLE_SHEET_ID"]
CREDS_FILE       = os.environ.get("GOOGLE_CREDS_FILE", "credentials.json")
ALLOWED_USER_IDS = set(os.environ.get("ALLOWED_USER_IDS", "").split(","))  # your Telegram user ID

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# ── Category keywords ─────────────────────────────────────────────────────────
CATEGORIES = {
    "Transport":     ["uber", "ola", "auto", "bike", "taxi", "cab", "rapido", "rickshaw"],
    "Metro":         ["metro", "dmrc", "card recharge", "metro recharge"],
    "Food":          ["food", "lunch", "dinner", "breakfast", "chai", "tea", "coffee",
                      "juice", "snack", "biryani", "pizza", "restaurant", "dhaba",
                      "swiggy", "zomato", "thali", "roti"],
    "Bills":         ["bill", "electricity", "light bill", "water bill", "recharge",
                      "internet", "wifi", "broadband", "gas"],
    "Home":          ["repair", "maintenance", "plumber", "electrician", "carpenter",
                      "paint", "home", "furniture", "rent"],
    "Entertainment": ["movie", "cinema", "pvr", "inox", "netflix", "hotstar",
                      "concert", "show", "game"],
    "Shopping":      ["shopping", "clothes", "shirt", "shoes", "amazon", "flipkart",
                      "myntra", "meesho", "kirana", "grocery"],
    "Health":        ["medicine", "doctor", "pharmacy", "hospital", "clinic",
                      "chemist", "medical", "test"],
    "Other":         [],
}

ACCOUNTS = ["bob", "indusind", "cash", "upi", "gpay", "phonepe", "paytm", "other"]


def guess_category(text: str) -> str:
    text_lower = text.lower()
    for cat, keywords in CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            return cat
    return "Other"


def guess_account(text: str) -> str:
    text_lower = text.lower()
    for acct in ACCOUNTS:
        if acct in text_lower:
            return acct.upper() if acct in ("bob", "upi") else acct.capitalize()
    return "Cash"


def parse_message(text: str):
    """
    Parses messages like:
      "lunch 80 cash"
      "uber 137.50 bob"
      "metro recharge 300 indusind"
      "add: chai 20 upi"
    Returns dict or None.
    """
    text = re.sub(r"^(add|log|record|exp)\s*:?\s*", "", text.strip(), flags=re.IGNORECASE)

    # Find the amount — a standalone number (integer or decimal)
    amount_match = re.search(r"\b(\d+(?:\.\d{1,2})?)\b", text)
    if not amount_match:
        return None

    amount = float(amount_match.group(1))
    remainder = (text[:amount_match.start()] + text[amount_match.end():]).strip()

    account  = guess_account(remainder)
    category = guess_category(remainder)

    # Clean account word from description
    clean_desc = re.sub(
        r"\b(bob|indusind|cash|upi|gpay|phonepe|paytm|other)\b",
        "", remainder, flags=re.IGNORECASE
    ).strip().title() or "Expense"

    return {
        "date":     datetime.now().strftime("%d-%m-%Y"),
        "desc":     clean_desc,
        "category": category,
        "amount":   amount,
        "account":  account,
    }


def get_sheet():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
    gc    = gspread.authorize(creds)
    sh    = gc.open_by_key(SHEET_ID)

    # Ensure "Expenses" worksheet exists with header
    try:
        ws = sh.worksheet("Expenses")
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title="Expenses", rows="1000", cols="6")
        ws.append_row(["Date", "Description", "Category", "Amount (₹)", "Account", "Logged At"])
        ws.format("A1:F1", {"textFormat": {"bold": True}})

    return ws


def append_row(entry: dict):
    ws = get_sheet()
    ws.append_row([
        entry["date"],
        entry["desc"],
        entry["category"],
        entry["amount"],
        entry["account"],
        datetime.now().strftime("%d-%m-%Y %H:%M"),
    ])


# ── Handlers ──────────────────────────────────────────────────────────────────

def is_allowed(update: Update) -> bool:
    if not ALLOWED_USER_IDS or ALLOWED_USER_IDS == {""}:
        return True  # no restriction set
    return str(update.effective_user.id) in ALLOWED_USER_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Naveen's Expense Bot*\n\n"
        "Just send me an expense in plain text:\n\n"
        "  `lunch 80 cash`\n"
        "  `uber 137 bob`\n"
        "  `metro recharge 300 indusind`\n"
        "  `medicine 250 upi`\n\n"
        "I'll figure out the category and log it to Google Sheets automatically.\n\n"
        "Commands:\n"
        "/today — today's total\n"
        "/help — show this message",
        parse_mode="Markdown"
    )


async def today_summary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        return
    try:
        ws      = get_sheet()
        records = ws.get_all_records()
        today   = datetime.now().strftime("%d-%m-%Y")
        todays  = [r for r in records if r.get("Date") == today]
        total   = sum(float(r.get("Amount (₹)", 0)) for r in todays)

        if not todays:
            await update.message.reply_text(f"No expenses logged today ({today}) yet.")
            return

        lines = [f"*Today's expenses ({today})*\n"]
        for r in todays:
            lines.append(f"  {r['Category']} · {r['Description']} — ₹{r['Amount (₹)']}")
        lines.append(f"\n*Total: ₹{total:,.2f}*")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Could not fetch today's data. Check logs.")


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_allowed(update):
        await update.message.reply_text("Sorry, you're not authorised to use this bot.")
        return

    text = update.message.text.strip()
    entry = parse_message(text)

    if not entry:
        await update.message.reply_text(
            "Couldn't parse that. Try: `chai 30 cash` or `uber 120 bob`",
            parse_mode="Markdown"
        )
        return

    try:
        append_row(entry)
        await update.message.reply_text(
            f"✓ Logged!\n"
            f"  {entry['date']}  |  {entry['desc']}\n"
            f"  {entry['category']}  ·  ₹{entry['amount']}  ·  {entry['account']}",
        )
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Failed to save. Check your credentials/sheet ID.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help",  start))
    app.add_handler(CommandHandler("today", today_summary))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
