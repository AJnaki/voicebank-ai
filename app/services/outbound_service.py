import asyncio
from twilio.rest import Client
from app.config import get_settings

settings = get_settings()

_client = None


def _get_client() -> Client:
    global _client
    if _client is None:
        _client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    return _client


def _make_call_sync(to: str, twiml_url: str) -> str:
    client = _get_client()
    call = client.calls.create(
        to=to,
        from_=settings.twilio_phone_number,
        url=twiml_url,
        status_callback=f"{settings.public_base_url}/webhook/call/status",
        status_callback_method="POST",
    )
    return call.sid


async def make_call(to: str, twiml_url: str) -> str:
    """Initiate an outbound call. Returns call SID."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _make_call_sync, to, twiml_url)


async def trigger_fraud_alert(to: str, user_name: str, amount: float, merchant: str) -> str:
    url = (
        f"{settings.public_base_url}/outbound/fraud-alert"
        f"?name={user_name}&amount={amount}&merchant={merchant}"
    )
    return await make_call(to, url)


async def trigger_low_balance_alert(to: str, user_name: str, balance: float) -> str:
    url = (
        f"{settings.public_base_url}/outbound/low-balance"
        f"?name={user_name}&balance={balance}"
    )
    return await make_call(to, url)


async def trigger_loan_reminder(to: str, user_name: str, emi: float, due_date: str) -> str:
    url = (
        f"{settings.public_base_url}/outbound/loan-reminder"
        f"?name={user_name}&emi={emi}&due_date={due_date}"
    )
    return await make_call(to, url)
