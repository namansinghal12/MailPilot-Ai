import json
import re

from google import genai
from google.genai import types

from app.core.config import settings


MODEL_NAME = "gemini-3.8-flash"


def get_gemini_client():
    if not settings.GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY is not set in backend configuration (.env)."
        )

    return genai.Client(
        api_key=settings.GEMINI_API_KEY
    )


def ask_gemini(
    prompt: str,
    system_instruction: str | None = None,
) -> str:
    """
    Send a prompt to the real Google Gemini API.
    """

    client = get_gemini_client()

    config = None

    if system_instruction:
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
        )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )

    if response and response.text:
        return response.text.strip()

    raise ValueError(
        "Gemini returned an empty response."
    )


def generate_draft_reply(
    sender_name: str,
    sender_email: str,
    subject: str,
    body: str,
    user_name: str,
) -> str:
    """
    Generate a real AI draft reply for an email thread.
    """

    prompt = f"""
Draft a professional, concise, and helpful email reply.

SENDER: {sender_name} <{sender_email}>
SUBJECT: {subject}

EMAIL BODY:
{body}

SENDER OF REPLY: {user_name}

INSTRUCTIONS:
1. Address the sender by first name when appropriate.
2. Understand the actual email before drafting the response.
3. Provide a polite and relevant response.
4. Do not invent facts, commitments, dates, or actions.
5. Keep the response concise and natural.
6. Return only the email body.
7. Sign off with:

Best regards,
{user_name}
""".strip()

    return ask_gemini(prompt)


def analyze_email_with_ai(
    subject: str,
    body: str,
) -> dict:
    """
    Analyze a real email using Google Gemini AI.
    """

    prompt = f"""
Analyze the following email and return ONLY a valid JSON object.

Subject:
{subject}

Body:
{body}

Return exactly this structure:

{{
  "category": "Career" | "System" | "Design" | "Newsletters" | "Inbox",
  "priority": "urgent" | "high" | "medium" | "low",
  "key_takeaways": [
    "important point 1",
    "important point 2"
  ],
  "recommended_action": "What the user should do next",
  "sentiment": "positive" | "neutral" | "urgent" | "action_required"
}}
""".strip()

    raw_text = ask_gemini(prompt)

    match = re.search(
        r"\{.*\}",
        raw_text,
        re.DOTALL,
    )

    if not match:
        raise ValueError(
            "Gemini returned an invalid analysis response."
        )

    try:
        analysis = json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Gemini returned invalid JSON: {exc}"
        ) from exc

    return analysis