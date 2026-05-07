import json
from typing import Optional

from app.config import get_settings
from app.models.call_session import CallSession

settings = get_settings()

SYSTEM_PROMPT = """You are the voice assistant for {bank_name}. The caller is {user_name} — fully authenticated.

Account: {account_number}
Available balance: {balance} {currency}

Recent transactions:
{transactions}

Classify the caller's intent, extract relevant parameters, and generate a short spoken response.

Return ONLY valid JSON — no markdown, no code fences:
{{
  "intent": "<see intents below>",
  "response_text": "<1-2 sentences, spoken aloud, numbers in words>",
  "escalate": <true|false>,
  "escalate_reason": "<reason or null>",
  "params": {{
    "amount": <number or null>,
    "destination": "<account name or null>",
    "biller": "<biller name or null>",
    "cheque_number": "<string or null>",
    "description": "<dispute description or null>"
  }}
}}

Available intents:
- balance           → check account balance
- transactions      → list recent transactions
- statement         → email PDF statement
- mini_statement    → send last 5 transactions via SMS
- bill_payment      → pay a bill (extract biller and amount from params)
- card_block        → freeze/block card
- card_unblock      → unblock/unfreeze card
- card_dispute      → report unauthorized transaction
- loan_status       → check loan balance, EMI, due date
- fund_transfer     → transfer funds (extract destination and amount from params)
- fd_enquiry        → fixed deposit balance and maturity info
- cheque_status     → cheque clearance status (extract cheque_number from params)
- live_agent        → caller wants a human agent
- unknown           → cannot classify

Rules:
- response_text is spoken aloud — keep it SHORT and conversational
- Numbers in words: "twelve hundred dollars" not "$1,200"
- For unknown: politely ask to rephrase
- Set escalate=true for live_agent or if caller sounds very distressed
- Extract numeric amounts from phrases like "two hundred dollars" → 200
- Never use markdown in response_text"""

_FALLBACK = {
    "intent": "unknown",
    "response_text": "I'm sorry, I didn't quite catch that. Could you rephrase what you need?",
    "escalate": False,
    "escalate_reason": None,
    "params": {},
}


def _build_prompt(transcript: str, session: CallSession, balance: float, currency: str, transactions: list) -> tuple[str, str]:
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
    return system, transcript


def _parse(raw: str) -> dict:
    try:
        data = json.loads(raw)
        if "params" not in data:
            data["params"] = {}
        return data
    except (json.JSONDecodeError, KeyError):
        return _FALLBACK


async def _call_groq(system: str, user: str) -> dict:
    from groq import AsyncGroq
    client = AsyncGroq(api_key=settings.groq_api_key)
    response = await client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=512,
        temperature=0.1,
    )
    return _parse(response.choices[0].message.content)


async def _call_anthropic(system: str, user: str) -> dict:
    from anthropic import AsyncAnthropic
    client = AsyncAnthropic(api_key=settings.ai_engine_api_key)
    response = await client.messages.create(
        model=settings.ai_model,
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return _parse(response.content[0].text)


async def classify_intent(
    transcript: str,
    session: CallSession,
    balance: float = 0.0,
    currency: str = "USD",
    transactions: Optional[list[dict]] = None,
) -> dict:
    system, user = _build_prompt(transcript, session, balance, currency, transactions or [])

    try:
        if settings.groq_api_key:
            return await _call_groq(system, user)
        if settings.ai_engine_api_key:
            return await _call_anthropic(system, user)
    except Exception:
        pass

    return _FALLBACK
