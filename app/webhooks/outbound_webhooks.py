from fastapi import APIRouter, Request, Response
from app.services.elevenlabs_service import tts_url
from app.services.twilio_service import ask_intent_twiml, say_and_hang_up_twiml, transfer_to_agent_twiml
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/outbound", tags=["outbound"])


def _xml(content: str) -> Response:
    return Response(content=content, media_type="application/xml")


@router.post("/fraud-alert")
async def fraud_alert_call(request: Request, name: str = "", amount: float = 0, merchant: str = ""):
    greeting = (
        f"Hello, this is an automated security alert from {settings.bank_name}. "
        f"We detected a transaction of {amount:.0f} dollars at {merchant or 'an unfamiliar merchant'}. "
        f"If you made this transaction, say yes. If you did not make this transaction, say no."
    )
    audio = await tts_url(greeting)
    action = f"{settings.public_base_url}/outbound/fraud-alert/response"
    return _xml(ask_intent_twiml(audio, action))


@router.post("/fraud-alert/response")
async def fraud_alert_response(request: Request):
    form = dict(await request.form())
    speech = form.get("SpeechResult", "").lower()

    if "no" in speech:
        msg = (
            f"We are immediately blocking your card and alerting our fraud team. "
            f"A team member will call you within 2 hours. Stay safe. Goodbye."
        )
    else:
        msg = "Thank you for confirming. No action has been taken. Have a great day."

    audio = await tts_url(msg)
    return _xml(say_and_hang_up_twiml(audio))


@router.post("/low-balance")
async def low_balance_call(request: Request, name: str = "", balance: float = 0):
    greeting = (
        f"Hello {name}, this is {settings.bank_name}. "
        f"Your account balance has dropped to {balance:.0f} dollars. "
        f"Would you like to review your recent transactions or make a transfer? Say yes or no."
    )
    audio = await tts_url(greeting)
    action = f"{settings.public_base_url}/outbound/low-balance/response"
    return _xml(ask_intent_twiml(audio, action))


@router.post("/low-balance/response")
async def low_balance_response(request: Request):
    form = dict(await request.form())
    speech = form.get("SpeechResult", "").lower()

    if "yes" in speech:
        msg = "Connecting you to our virtual assistant now. Please hold."
        audio = await tts_url(msg)
        return _xml(transfer_to_agent_twiml(audio, settings.agent_transfer_number))

    audio = await tts_url("Understood. Call us anytime you need help. Goodbye.")
    return _xml(say_and_hang_up_twiml(audio))


@router.post("/loan-reminder")
async def loan_reminder_call(request: Request, name: str = "", emi: float = 0, due_date: str = ""):
    greeting = (
        f"Hello {name}, this is a reminder from {settings.bank_name}. "
        f"Your loan payment of {emi:.0f} dollars is due on {due_date}. "
        f"Would you like to make the payment now? Say yes or no."
    )
    audio = await tts_url(greeting)
    action = f"{settings.public_base_url}/outbound/loan-reminder/response"
    return _xml(ask_intent_twiml(audio, action))


@router.post("/loan-reminder/response")
async def loan_reminder_response(request: Request):
    form = dict(await request.form())
    speech = form.get("SpeechResult", "").lower()

    if "yes" in speech:
        msg = "Connecting you to our payment line now. Please hold."
        audio = await tts_url(msg)
        return _xml(transfer_to_agent_twiml(audio, settings.agent_transfer_number))

    audio = await tts_url("No problem. Your payment is due soon. Call us anytime. Goodbye.")
    return _xml(say_and_hang_up_twiml(audio))
