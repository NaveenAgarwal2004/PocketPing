"""Google Sheets connection â€” authenticates and exposes the worksheet."""

import re
import gspread
from google.oauth2.service_account import Credentials
from config import CREDS_FILE, SHEET_ID, SCOPES

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc    = gspread.authorize(creds)
_wb   = gc.open_by_key(SHEET_ID)

# Master data tab name â€” must match DATA_SHEET in Code.gs
DATA_TAB = "All Expenses"

def _is_monthly(title: str) -> bool:
    """Returns True for auto-created tabs like 'Jun 2026', 'Jul 2026'."""
    return bool(re.match(r"[A-Z][a-z]{2} \d{4}", title))

try:
    sheet = _wb.worksheet(DATA_TAB)
except gspread.exceptions.WorksheetNotFound:
    # Fallback: first tab that isn't Summary or a monthly tab
    sheet = next(
        (ws for ws in _wb.worksheets()
         if ws.title != "Summary" and not _is_monthly(ws.title)),
        _wb.worksheets()[0]
    )
