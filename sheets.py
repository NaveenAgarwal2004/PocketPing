"""Google Sheets connection — authenticates and exposes the worksheet.

get_sheet() resolves fresh on every call — avoids stale connections
when the bot starts before the data tab exists.
"""

import re
import gspread
from google.oauth2.service_account import Credentials
from config import CREDS_FILE, SHEET_ID, SCOPES

DATA_TAB = "All Expenses"  # must match DATA_SHEET in Code.gs

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc    = gspread.authorize(creds)
_wb   = gc.open_by_key(SHEET_ID)


def _is_monthly(title: str) -> bool:
    """Returns True for auto-created tabs like 'Jun 2026', 'Jul 2026'."""
    return bool(re.match(r"[A-Z][a-z]{2} \d{4}", title))


def get_sheet() -> gspread.Worksheet:
    """Always resolve fresh — never returns Summary or a monthly tab."""
    try:
        return _wb.worksheet(DATA_TAB)
    except gspread.exceptions.WorksheetNotFound:
        for ws in _wb.worksheets():
            if ws.title != "Summary" and not _is_monthly(ws.title):
                return ws
        raise RuntimeError(
            f"Data worksheet '{DATA_TAB}' not found. "
            "Rename your data tab to 'All Expenses' and redeploy."
        )


# Kept for legacy imports — handlers.py now uses get_sheet() directly
sheet = get_sheet()