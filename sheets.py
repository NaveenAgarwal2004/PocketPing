"""Google Sheets connection — authenticates and exposes the worksheet."""

import gspread
from google.oauth2.service_account import Credentials

from config import CREDS_FILE, SHEET_ID, SCOPES

creds = Credentials.from_service_account_file(CREDS_FILE, scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1
