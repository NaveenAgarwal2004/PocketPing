"""Telegram bot handlers — /start, /help, /today, /last, /undo, and expense message handler."""

import logging
import time
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import ALLOWED_USER_IDS
from parser import parse_expense
from sheets import sheet
from analytics import format_today, format_last, format_success, format_help

logger = logging.getLogger(__name__)

_recent_updates: dict[int, float] = {}
_recent_expenses: dict[tuple, float] = {}

# Undo tracking: user_id -> {row_index, timestamp}
_last_expense: dict[int, dict] = {}

UNDO_WINDOW_SECONDS = 30


def is_allowed(uid: int) -> bool:
    """Check if user ID is in the allowed set."""
    return str(uid) in ALLOWED_USER_IDS


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command — show onboarding message."""
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(format_help())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command — show onboarding message."""
    if not is_allowed(update.effective_user.id):
        return
    await update.message.reply_text(format_help())


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /today command — show today's expense summary."""
    if not is_allowed(update.effective_user.id):
        return
    rows = sheet.get_all_values()
    await update.message.reply_text(format_today(rows))


async def cmd_last(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /last command — show last 5 expenses."""
    if not is_allowed(update.effective_user.id):
        return
    rows = sheet.get_all_values()
    await update.message.reply_text(format_last(rows))


async def cmd_undo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /undo command — remove last expense within 30s window."""
    if not is_allowed(update.effective_user.id):
        return

    uid = update.effective_user.id

    if uid not in _last_expense:
        await update.message.reply_text("No recent expense found.")
        return

    entry = _last_expense[uid]
    elapsed = time.time() - entry["timestamp"]

    if elapsed > UNDO_WINDOW_SECONDS:
        del _last_expense[uid]
        await update.message.reply_text("Undo window expired.")
        return

    try:
        sheet.delete_rows(entry["row_index"])
        del _last_expense[uid]
        await update.message.reply_text("↩️ Last expense removed.")
    except Exception as e:
        logger.error(f"Undo error: {e}")
        await update.message.reply_text("Error undoing expense. Try again.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle plaintext messages — parse and log expenses."""
    if not is_allowed(update.effective_user.id):
        return
    result = parse_expense(update.message.text)
    if not result:
        await update.message.reply_text("Couldn't parse that. Try: chai 20 cash")
        return

    now = time.time()

    if update.update_id in _recent_updates:
        if now - _recent_updates[update.update_id] <= 5.0:
            await update.message.reply_text("⚠️ Duplicate expense ignored.")
            return

    dup_key = (
        update.effective_user.id,
        result["description"].lower(),
        result["amount"],
        result["account"]
    )

    if dup_key in _recent_expenses:
        if now - _recent_expenses[dup_key] <= 5.0:
            await update.message.reply_text("⚠️ Duplicate expense ignored.")
            return

    _recent_updates[update.update_id] = now
    _recent_expenses[dup_key] = now

    # Cleanup memory only when it grows beyond 100
    if len(_recent_expenses) > 100:
        for k in list(_recent_expenses.keys()):
            if now - _recent_expenses[k] > 10.0:
                del _recent_expenses[k]

    if len(_recent_updates) > 100:
        for k in list(_recent_updates.keys()):
            if now - _recent_updates[k] > 10.0:
                del _recent_updates[k]

    timestamp_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    row = [timestamp_str, result["description"], result["category"],
           result["amount"], result["account"]]
    try:
        # Read rows BEFORE appending (for today's total calculation)
        rows = sheet.get_all_values()
        sheet.append_row(row, value_input_option="USER_ENTERED")

        # Track for undo: row_index is len(rows) + 1 (1-indexed, after append)
        row_index = len(rows) + 1
        _last_expense[update.effective_user.id] = {
            "row_index": row_index,
            "timestamp": now,
        }

        # Cleanup undo tracking when it grows beyond 50
        if len(_last_expense) > 50:
            stale_uids = [
                uid for uid, e in _last_expense.items()
                if now - e["timestamp"] > UNDO_WINDOW_SECONDS
            ]
            for uid in stale_uids:
                del _last_expense[uid]

        reply = format_success(result, timestamp_str, rows)
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"Sheet error: {e}")
        await update.message.reply_text("Error saving to sheet. Try again.")
