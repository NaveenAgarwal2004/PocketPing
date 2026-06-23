"""
conftest.py — session-level env var injection and gspread/google mock.

Must run before any project module is imported, so it lives at the
package root and uses autouse fixtures.

Strategy:
  - Env vars are patched via os.environ before each test module imports
    config.py (which reads them at module level).
  - gspread and google.oauth2 are replaced with lightweight stubs so that
    sheets.py never touches the network.
  - All patches are applied before the first import of each module.
"""

import os
import sys
import types
from unittest.mock import MagicMock

import pytest


# ── Minimal env vars that config.py requires ─────────────────────────────
_ENV = {
    "TELEGRAM_BOT_TOKEN": "test-token-123",
    "GOOGLE_SHEET_ID":    "test-sheet-id",
    "GOOGLE_CREDS_FILE":  "credentials.json",
    "ALLOWED_USER_IDS":   "111,222",
    "PORT":               "8080",
}


def _install_google_stubs():
    """Inject fake google / gspread modules so sheets.py never hits network."""

    # --- google.oauth2.service_account stub ---
    mock_creds_instance = MagicMock()
    mock_sa_module = MagicMock()
    mock_sa_module.Credentials.from_service_account_file.return_value = mock_creds_instance

    google_pkg       = types.ModuleType("google")
    google_oauth2    = types.ModuleType("google.oauth2")
    google_oauth2_sa = mock_sa_module

    google_pkg.oauth2 = google_oauth2
    google_oauth2.service_account = google_oauth2_sa

    sys.modules["google"]                      = google_pkg
    sys.modules["google.oauth2"]               = google_oauth2
    sys.modules["google.oauth2.service_account"] = google_oauth2_sa

    # --- gspread stub ---
    mock_sheet        = MagicMock()
    mock_worksheet    = MagicMock()
    mock_worksheet.sheet1 = mock_sheet
    mock_gspread      = MagicMock()
    mock_gspread.authorize.return_value.open_by_key.return_value = mock_worksheet

    sys.modules["gspread"] = mock_gspread

    return mock_sheet  # expose for test assertions


# Install stubs and env vars once, before any project module is loaded.
_MOCK_SHEET = _install_google_stubs()

for k, v in _ENV.items():
    os.environ.setdefault(k, v)


@pytest.fixture
def mock_sheet():
    """Return the shared mock worksheet so tests can assert on it."""
    _MOCK_SHEET.reset_mock()
    return _MOCK_SHEET
