"""Analytics module — formats today summary, last expenses, and success messages.

All functions are pure: they accept data and return formatted strings.
No Telegram or Google Sheets imports — keeps this module testable in isolation.
"""

from datetime import datetime

CATEGORY_EMOJIS: dict[str, str] = {
    "Food": "🍔",
    "Transport": "🚕",
    "Metro": "🚇",
    "Health": "💊",
    "Bills": "💡",
    "Home": "🏠",
    "Entertainment": "🎬",
    "Shopping": "🛍️",
    "Other": "🏷️",
}


def get_emoji(category: str) -> str:
    """Return emoji for a category, defaulting to label tag."""
    return CATEGORY_EMOJIS.get(category, "🏷️")


def format_today(rows: list[list[str]]) -> str:
    """Build the /today summary from sheet rows.

    Filters rows matching today's date, groups by category,
    sorts descending by amount, and shows percentage contribution.

    Returns 'No expenses found.' if no matching rows.
    """
    today_str = datetime.now().strftime("%d-%m-%Y")

    totals_by_cat: dict[str, float] = {}
    total = 0.0
    count = 0

    for r in rows:
        if r and len(r) >= 4 and r[0].startswith(today_str):
            try:
                amt = float(r[3])
                cat = r[2]
                totals_by_cat[cat] = totals_by_cat.get(cat, 0.0) + amt
                total += amt
                count += 1
            except (ValueError, IndexError):
                pass

    if count == 0:
        return "No expenses found."

    # Sort categories by amount descending
    sorted_cats = sorted(totals_by_cat.items(), key=lambda x: x[1], reverse=True)

    lines = ["📅 Today\n"]
    for cat, amt in sorted_cats:
        emoji = get_emoji(cat)
        pct = int(round(amt / total * 100)) if total > 0 else 0
        lines.append(f"{emoji} {cat.ljust(15)} ₹{amt:.0f} ({pct}%)")

    lines.append("\n────────────────\n")
    lines.append(f"💰 Total            ₹{total:.0f}")
    lines.append(f"📝 Transactions     {count}")

    return "\n".join(lines)


def format_last(rows: list[list[str]]) -> str:
    """Build the /last summary from sheet rows.

    Excludes header row, takes last 5, shows newest first in compact format.

    Returns 'No expenses found.' if no data rows.
    """
    # Exclude header row if present
    if rows and len(rows[0]) >= 4 and rows[0][3] == "Amount":
        rows = rows[1:]

    if not rows:
        return "No expenses found."

    latest = rows[-5:]
    latest.reverse()

    lines = [f"🕒 Last {len(latest)} Expenses\n"]
    for r in latest:
        if len(r) >= 5:
            desc, cat, amt, acc = r[1], r[2], r[3], r[4]
            emoji = get_emoji(cat)
            lines.append(f"{emoji} {desc} • ₹{amt} • {acc}")

    return "\n".join(lines)


def format_success(
    result: dict[str, str], timestamp: str, rows: list[list[str]]
) -> str:
    """Build the success message after logging an expense.

    Includes today's running total and transaction count from sheet rows.
    """
    today_str = datetime.now().strftime("%d-%m-%Y")
    emoji = get_emoji(result["category"])

    total = 0.0
    count = 0
    for r in rows:
        if r and len(r) >= 4 and r[0].startswith(today_str):
            try:
                total += float(r[3])
                count += 1
            except (ValueError, IndexError):
                pass

    # Include the just-logged expense (it may not be in rows yet)
    try:
        total += float(result["amount"])
        count += 1
    except ValueError:
        pass

    lines = [
        "✅ Expense Logged\n",
        f"{emoji} {result['description']}\n",
        f"₹{result['amount']} • {result['account']}\n",
        "────────────────\n",
        f"📅 Today's Total : ₹{total:.0f}",
        f"📝 Transactions  : {count}",
    ]
    return "\n".join(lines)


def format_help() -> str:
    """Build the /start and /help onboarding message."""
    return (
        "👋 Expense Tracker\n\n"
        "Just send expenses naturally:\n\n"
        "• chai 20\n"
        "• chai20\n"
        "• ₹20 chai\n"
        "• uber 137 bob\n"
        "• food shared with rishabh 220 bob\n\n"
        "Commands\n\n"
        "📅 /today — today's summary\n"
        "🕒 /last  — last 5 expenses\n"
        "↩️ /undo  — undo last expense\n"
        "❓ /help  — this message"
    )
