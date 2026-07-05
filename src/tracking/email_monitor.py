from src.config import GM_CREDENTIALS_PATH, GM_TOKEN_PATH
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from pathlib import Path
import base64

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def _get_service():
    creds = None
    if GM_TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(GM_TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GM_CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        GM_TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(GM_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def check_for_replies(sender_filter: str = "") -> list[dict]:
    service = _get_service()
    query = "in:inbox is:unread"
    if sender_filter:
        query += f" from:({sender_filter})"
    results = service.users().messages().list(userId="me", q=query).execute()
    messages = results.get("messages", [])
    replies = []
    for msg in messages[:20]:
        details = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = {h["name"]: h["value"] for h in details["payload"]["headers"]}
        subject = headers.get("Subject", "")
        sender = headers.get("From", "")
        snippet = details.get("snippet", "")
        replies.append({
            "id": msg["id"],
            "subject": subject,
            "from": sender,
            "snippet": snippet,
        })
    return replies


def mark_as_read(message_id: str) -> None:
    service = _get_service()
    service.users().messages().modify(
        userId="me",
        id=message_id,
        body={"removeLabelIds": ["UNREAD"]},
    ).execute()
