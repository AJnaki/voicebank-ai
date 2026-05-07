import json
from typing import Optional

from anthropic import AsyncAnthropic

from app.config import get_settings
from app.models.call_session import CallSession

settings = get_settings()

_client: Optional[AsyncAnthropic] = None

SYSTEM_PROMPT = """You are the voice assistant for {bank_name}. The caller is {user_name} — fully authenticated.

Account: {account_number}
Available balance: {balance} {currency}

Recent transactions:
{transactions}

Classify the caller's intent and generate a short spoken response.

Return ONLY valid JSON — no markdown, no code fences:
{{
  "intent": "<balance|transactions|statement|bill_payment|card_block|loan_status|fund_transfer|fraud_report|live_agent|unknown>",
  "response_text": "<1-2 sentences, spoken aloud, numbers in words>",
  "escalate": <true|false>,
  "escalate_reason": "<reason or null>"
}}

Rules:
- response_text will be spoken — keep it SHORT and conversational
- Numbers in words: "twelve thousand four hundred dollars" not "$12,400"
- balance intent: state the available balance
- transactions intent: name the last 3 transactions briefly
- unknown intent: politely ask to rephrase
- live_agent: set escalate=true
- card_block: confirm the action and instruct caller to say yes/no
- Do not use markdown, bullet points, or special characters in response_text"""


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ai_engine_api_key)
    return _client


async def classify_intent(
    transcript: str,
    session: CallSession,
    balance: float = 0.0,
    currency: str = "USD",
    transactions: Optional[list[dict]] = None,
) -> dict:
    transactions = transactions or []
    tx_lines = "\n".join(
        f"- {t['date']}: {t['description']}, "
        f"{'debit' if t['amount'] < 0 else 'credit'} {abs(t['amount']):.2f}"
        for t in transactions[:5]
    ) or "No recent transactions on file."

    system = SYSTEM_PROMPT.format(
        bank_name=session.bank_name,
        user_name=session.user_name or "caller",
        account_number=session.account_number or "your account",
        balance=f"{balance:,.2f}",
        currency=currency,
        transactions=tx_lines,
    )

    client = _get_client()
    response = await client.messages.create(
        model=settings.ai_model,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": transcript}],
    )

    try:
        return json.loads(response.content[0].text)
    except (json.JSONDecodeError, IndexError, KeyError):
        return {
            "intent": "unknown",
            "response_text": "I'm sorry, I didn't quite catch that. Could you rephrase what you need?",
            "escalate": False,
            "escalate_reason": None,
        }
