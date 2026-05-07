import asyncio
from anthropic import AsyncAnthropic
from app.config import get_settings
from app.models.call_session import CallSession
from app.services.sms_service import _send_sync

settings = get_settings()
_client = None


def _get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=settings.ai_engine_api_key)
    return _client


async def generate_summary(session: CallSession) -> str:
    """Generate a short SMS-friendly call summary using the AI Engine."""
    if not session.intent_log:
        return ""

    intent_text = ", ".join(session.intent_log)
    prompt = (
        f"Summarize this bank call in 3-5 bullet points for an SMS. "
        f"Intents handled: {intent_text}. "
        f"Keep it under 300 characters total. "
        f"Use ✓ for completed actions. Plain text only, no markdown."
    )

    client = _get_client()
    response = await client.messages.create(
        model=settings.ai_model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


async def send_post_call_sms(session: CallSession, phone: str) -> bool:
    """Generate and send the post-call SMS summary."""
    from datetime import datetime
    summary = await generate_summary(session)
    if not summary:
        return False

    now = datetime.now().strftime("%b %d, %Y %I:%M %p")
    body = (
        f"{session.bank_name}\n"
        f"{'─' * 22}\n"
        f"Call summary ({now})\n\n"
        f"{summary}\n\n"
        f"Questions? Call us anytime."
    )

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_sync, phone, body)


async def generate_agent_briefing(session: CallSession) -> str:
    """Generate a briefing for the live agent co-pilot screen."""
    transcript_text = "\n".join(
        f"{t.role.upper()}: {t.text}" for t in session.transcript[-10:]
    )
    prompt = (
        f"A caller has been transferred to a live agent. Write a 3-sentence briefing "
        f"the agent can read in 10 seconds.\n\n"
        f"Caller: {session.user_name}\n"
        f"Account: {session.account_number}\n"
        f"Intents: {', '.join(session.intent_log)}\n"
        f"Last sentiment: {session.sentiment_log[-1] if session.sentiment_log else 'neutral'}\n\n"
        f"Recent transcript:\n{transcript_text}"
    )

    client = _get_client()
    response = await client.messages.create(
        model=settings.ai_model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()
