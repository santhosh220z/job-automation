from src.config import GM_CREDENTIALS_PATH, SHEET_ID
from pathlib import Path
from datetime import datetime, timezone


def _get_client():
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(str(GM_CREDENTIALS_PATH), scopes=scopes)
    return gspread.authorize(creds)


def _ensure_sheet(client):
    sheet = client.open_by_key(SHEET_ID).sheet1
    header = sheet.row_values(1)
    expected = ["Timestamp", "Company", "Role", "URL", "Status", "Notes"]
    if header != expected:
        sheet.clear()
        sheet.append_row(expected)
    return sheet


def log_application(company: str, role: str, url: str, status: str = "Applied", notes: str = "") -> None:
    client = _get_client()
    sheet = _ensure_sheet(client)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    sheet.append_row([now, company, role, url, status, notes])


def update_status(url: str, new_status: str, notes: str = "") -> None:
    client = _get_client()
    sheet = _ensure_sheet(client)
    records = sheet.get_all_values()
    for i, row in enumerate(records[1:], start=2):
        if len(row) >= 4 and row[3] == url:
            sheet.update_cell(i, 5, new_status)
            if notes:
                existing = sheet.cell(i, 6).value or ""
                sheet.update_cell(i, 6, f"{existing}; {notes}" if existing else notes)
            break


def get_applications() -> list[dict]:
    client = _get_client()
    sheet = _ensure_sheet(client)
    records = sheet.get_all_records()
    return records
