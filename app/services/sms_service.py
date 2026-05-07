from twilio.rest import Client
from app.config import get_settings
import asyncio

settings = get_settings()

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def _send_sync(to: str, body: str) -> bool:
    client = _get_client()
    msg = client.messages.create(
        to=to,
        from_=settings.twilio_phone_number,
        body=body,
    )
    return msg.sid is not None


async def send_mini_statement(to: str, bank_name: str, transactions: list) -> bool:
    lines = [f"{bank_name} — Mini Statement", "─" * 28]
    for i, t in enumerate(transactions[:5], 1):
        sign = "-" if t.amount < 0 else "+"
        lines.append(f"{i}. {t.date}  {t.description[:18]:<18} {sign}${abs(t.amount):.2f}")
    lines.append("─" * 28)
    lines.append("Helpline: call your bank number")
    body = "\n".join(lines)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_sync, to, body)


async def send_otp_sms(to: str, otp: str, bank_name: str) -> bool:
    body = (
        f"{bank_name}: Your one-time verification code is {otp}. "
        f"Valid for 5 minutes. Do not share this code with anyone."
    )
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _send_sync, to, body)
