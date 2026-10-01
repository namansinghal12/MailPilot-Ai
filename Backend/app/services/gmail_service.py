from __future__ import annotations

import base64
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings

GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
]


def create_gmail_credentials(refresh_token: str) -> Credentials:
    """
    Rebuild Google credentials from the user's stored refresh token.
    """

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        scopes=GMAIL_SCOPES,
    )

    # Obtain a fresh access token from Google's OAuth server.
    credentials.refresh(Request())

    return credentials


def create_gmail_service(refresh_token: str):
    """
    Create an authenticated Gmail API client.
    """

    credentials = create_gmail_credentials(refresh_token)

    return build(
        "gmail",
        "v1",
        credentials=credentials,
        cache_discovery=False,
    )


def get_header(headers: list[dict[str, str]], name: str) -> str:
    """
    Find a Gmail header such as From, To or Subject.
    """

    for header in headers:
        if header.get("name", "").lower() == name.lower():
            return header.get("value", "")

    return ""


def decode_body(data: str | None) -> str:
    """
    Decode Gmail's URL-safe base64 message body.
    """

    if not data:
        return ""

    try:
        decoded = base64.urlsafe_b64decode(
            data + "=" * (-len(data) % 4)
        )

        return decoded.decode(
            "utf-8",
            errors="replace",
        )

    except Exception:
        return ""


def extract_text_from_payload(payload: dict[str, Any]) -> str:
    """
    Recursively extract readable text from Gmail MIME parts.
    """

    mime_type = payload.get("mimeType", "")

    body = payload.get("body", {})
    data = body.get("data")

    if data and mime_type == "text/plain":
        return decode_body(data)

    parts = payload.get("parts", [])

    text_parts: list[str] = []

    for part in parts:
        text = extract_text_from_payload(part)

        if text:
            text_parts.append(text)

    if text_parts:
        return "\n\n".join(text_parts)

    # Fallback for HTML-only messages.
    if data and mime_type == "text/html":
        return decode_body(data)

    return ""


def parse_received_date(
    headers: list[dict[str, str]],
    internal_date: str | None,
) -> datetime:
    """
    Convert Gmail's date information into a timezone-aware datetime.
    """

    date_header = get_header(headers, "Date")

    if date_header:
        try:
            parsed = parsedate_to_datetime(date_header)

            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)

            return parsed.astimezone(timezone.utc)

        except Exception:
            pass

    if internal_date:
        try:
            timestamp = int(internal_date) / 1000

            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            )

        except Exception:
            pass

    return datetime.now(timezone.utc)


def list_messages(
    refresh_token: str,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """
    Get recent Gmail messages for the authenticated user.
    """

    service = create_gmail_service(refresh_token)

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results,
        )
        .execute()
    )

    return response.get("messages", [])


def get_message(
    refresh_token: str,
    message_id: str,
) -> dict[str, Any]:
    """
    Retrieve the full Gmail message.
    """

    service = create_gmail_service(refresh_token)

    return (
        service.users()
        .messages()
        .get(
            userId="me",
            id=message_id,
            format="full",
        )
        .execute()
    )


def parse_gmail_message(
    message: dict[str, Any],
) -> dict[str, Any]:
    """
    Convert Gmail's API response into MailPilot's email structure.
    """

    payload = message.get("payload", {})

    headers = payload.get("headers", [])

    sender = get_header(headers, "From")
    recipient = get_header(headers, "To")
    subject = get_header(headers, "Subject")

    body = extract_text_from_payload(payload)

    snippet = message.get("snippet", "")

    received_at = parse_received_date(
        headers,
        message.get("internalDate"),
    )

    # Parse "Name <email@example.com>" format.
    sender_name = sender
    sender_email = sender

    if "<" in sender and ">" in sender:
        sender_name = sender.split("<", 1)[0].strip().strip('"')
        sender_email = (
            sender.split("<", 1)[1]
            .split(">", 1)[0]
            .strip()
        )

    label_ids = message.get("labelIds", [])

    is_read = "UNREAD" not in label_ids
    is_starred = "STARRED" in label_ids
    is_archived = "INBOX" not in label_ids

    return {
        "id": message["id"],
        "sender_name": sender_name or sender_email,
        "sender_email": sender_email,
        "recipient": recipient,
        "subject": subject or "(No Subject)",
        "body": body or snippet,
        "snippet": snippet,
        "is_read": is_read,
        "is_starred": is_starred,
        "is_archived": is_archived,
        "received_at": received_at,
    }


def fetch_recent_emails(
    refresh_token: str,
    max_results: int = 20,
) -> list[dict[str, Any]]:
    """
    Fetch and parse recent real Gmail messages.
    """

    message_refs = list_messages(
        refresh_token=refresh_token,
        max_results=max_results,
    )

    emails: list[dict[str, Any]] = []

    for message_ref in message_refs:
        message_id = message_ref.get("id")

        if not message_id:
            continue

        message = get_message(
            refresh_token=refresh_token,
            message_id=message_id,
        )

        emails.append(
            parse_gmail_message(message)
        )

    return emails