"""Google Sheets connection — authenticates and exposes the worksheet."""

import re

import gspread
from google.oauth2.service_account import Credentials

from config import CREDS_FILE, SHEET_ID, SCOPES

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc    = gspread.authorize(creds)
_wb   = gc.open_by_key(SHEET_ID)


def _is_monthly(title: str) -> bool:
    """Returns True for tab names like 'Jun 2026'."""
    return bool(re.match(r"[A-Z][a-z]{2} \d{4}", title))


# Always write to the tab explicitly named "Sheet1" regardless of tab order.
# Using .sheet1 breaks when Summary is moved to position 0 by the Apps Script.
try:
    sheet = _wb.worksheet("Sheet1")
except gspread.exceptions.WorksheetNotFound:
    # Fallback: first tab that isn't Summary or a monthly tab
    sheet = next(
        (ws for ws in _wb.worksheets()
         if ws.title != "Summary" and not _is_monthly(ws.title)),
        _wb.worksheets()[0]
    )
