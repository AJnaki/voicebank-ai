import asyncio
from datetime import datetime, timezone
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator

from app.config import get_settings
from app.db.database import get_db
from app.db.redis_client import delete_session, load_session, save_session
from app.handlers.agent_handler import prepare_agent_handoff
from app.handlers.auth_handler import handle_name, handle_pin, record_biometric_score
from app.handlers.bill_handler import complete_bill_payment
from app.handlers.card_handler import handle_card_unblock_confirm
from app.handlers.intent_handler import route_intent
from app.handlers.transfer_handler import complete_transfer
from app.models.call_log import CallLog
from app.models.call_session import CallSession
from app.services import azure_speaker
from app.services.elevenlabs_service import tts_url
from app.services.otp_service import verify_otp
from app.services.twilio_service import (
    ask_intent_twiml,
    ask_pin_twiml,
    error_twiml,
    incoming_call_twiml,
    play_and_gather_twiml,
    say_and_hang_up_twiml,
    transfer_to_agent_twiml,
)

settings = get_settings()
router = APIRouter(prefix="/webhook/call", tags=["twilio"])


def _xml(content: str) -> Response:
    return Response(content=content, media_type="application/xml")


async def _validate_twilio(request: Request) -> bool:
    if not settings.is_production:
        return True
    validator = RequestValidator(settings.twilio_auth_token)
    signature = request.headers.get("X-Twilio-Signature", "")
    form = dict(await request.form())
    return validator.validate(str(request.url), form, signature)


# ── 1. Incoming call ──────────────────────────────────────────────────────────

@router.post("/incoming")
async def incoming_call(
    request: Request,
    CallSid: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
):
    if not await _validate_twilio(request):
        return _xml(error_twiml("Unauthorized request."))

    log = CallLog(call_sid=CallSid)
    db.add(log)
    await db.commit()

    greeting = (
        f"Welcome to {settings.bank_name}. I'm your virtual assistant. "
        f"To get started, please say your first and last name."
    )
    audio = await tts_url(greeting)
    action = f"{settings.public_base_url}/webhook/call/auth/name"
    return _xml(incoming_call_twiml(audio, action))


# ── 2. Name collection ────────────────────────────────────────────────────────

@router.post("/auth/name")
async def auth_name(
    request: Request,
    CallSid: Annotated[str, Form()],
    SpeechResult: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    spoken = (SpeechResult or "").strip()
    if not spoken:
        audio = await tts_url("I didn't catch that. Please say your first and last name.")
        action = f"{settings.public_base_url}/webhook/call/auth/name"
        return _xml(incoming_call_twiml(audio, action))

    session, outcome = await handle_name(spoken, CallSid, db)

    if outcome == "not_found":
        audio = await tts_url(
            "I couldn't find that name in our system. Please try again, "
            "or press zero to speak with an agent."
        )
        action = f"{settings.public_base_url}/webhook/call/auth/name"
        return _xml(incoming_call_twiml(audio, action))

    if outcome == "found_medium":
        last_four = session.account_number[-4:]
        prompt = (
            f"I found {session.user_name} with an account ending in {last_four}. "
            f"Is that you? Please say yes or no."
        )
        audio = await tts_url(prompt)
        action = f"{settings.public_base_url}/webhook/call/auth/confirm-name?call_sid={CallSid}"
        return _xml(incoming_call_twiml(audio, action))

    audio = await tts_url(
        f"Thank you, {session.user_name.split()[0]}. "
        f"Please enter your six-digit PIN using your keypad."
    )
    action = f"{settings.public_base_url}/webhook/call/auth/pin"
    return _xml(ask_pin_twiml(audio, action, num_digits=6))


@router.post("/auth/confirm-name")
async def confirm_name(
    request: Request,
    call_sid: str,
    SpeechResult: Annotated[Optional[str], Form()] = None,
):
    answer = (SpeechResult or "").strip().lower()
    session = await load_session(call_sid)

    if session is None or "no" in answer:
        audio = await tts_url("I'm sorry about that. Please say your first and last name again.")
        action = f"{settings.public_base_url}/webhook/call/auth/name"
        return _xml(incoming_call_twiml(audio, action))

    audio = await tts_url("Great. Please enter your six-digit PIN using your keypad.")
    action = f"{settings.public_base_url}/webhook/call/auth/pin"
    return _xml(ask_pin_twiml(audio, action, num_digits=6))


# ── 3. PIN verification ───────────────────────────────────────────────────────

@router.post("/auth/pin")
async def auth_pin(
    request: Request,
    CallSid: Annotated[str, Form()],
    Digits: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    session = await load_session(CallSid)
    if session is None:
        return _xml(error_twiml("Session expired. Please call back."))

    digits = (Digits or "").strip()
    if not digits:
        audio = await tts_url("I didn't receive your PIN. Please enter your six-digit PIN.")
        action = f"{settings.public_base_url}/webhook/call/auth/pin"
        return _xml(ask_pin_twiml(audio, action))

    outcome, session = await handle_pin(digits, session, db)

    if outcome == "locked":
        audio = await tts_url(
            "Your account has been locked due to too many incorrect PIN attempts. "
            "I'm connecting you to a team member who can help."
        )
        return _xml(transfer_to_agent_twiml(audio, settings.agent_transfer_number))

    if outcome == "wrong":
        remaining = 3 - session.auth.pin_attempts
        audio = await tts_url(
            f"Incorrect PIN. You have {remaining} "
            f"{'attempt' if remaining == 1 else 'attempts'} remaining. Please try again."
        )
        action = f"{settings.public_base_url}/webhook/call/auth/pin"
        return _xml(ask_pin_twiml(audio, action))

    asyncio.create_task(_run_biometric_async(session))

    first_name = session.user_name.split()[0]
    welcome = (
        f"Welcome back, {first_name}! How can I help you today? "
        f"You can ask about your balance, recent transactions, statements, "
        f"bill payments, card management, loan status, or anything else. "
        f"Or say 'talk to someone' to reach an agent."
    )
    audio = await tts_url(welcome)
    action = f"{settings.public_base_url}/webhook/call/intent"
    return _xml(ask_intent_twiml(audio, action))


async def _run_biometric_async(session: CallSession) -> None:
    from app.models.user import User
    from app.db.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        user = await db.get(User, session.user_id)
        if user and user.voice_profile_id:
            score = await azure_speaker.verify(user.voice_profile_id, b"")
            if score >= 0:
                await record_biometric_score(score, session)


# ── 4. Intent handling ────────────────────────────────────────────────────────

@router.post("/intent")
async def handle_intent(
    request: Request,
    CallSid: Annotated[str, Form()],
    SpeechResult: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    session = await load_session(CallSid)
    if session is None or not session.auth.fully_authenticated:
        return _xml(error_twiml("Session not found. Please call back."))

    transcript = (SpeechResult or "").strip()
    if not transcript:
        audio = await tts_url(
            "I didn't catch that. How can I help you? You can ask about "
            "your balance, transactions, or say 'talk to someone' for an agent."
        )
        action = f"{settings.public_base_url}/webhook/call/intent"
        return _xml(ask_intent_twiml(audio, action))

    response_text, should_escalate, requires_otp = await route_intent(transcript, session, db)

    if should_escalate:
        await prepare_agent_handoff(session, reason="caller_request")
        transfer_msg = f"{response_text} Please hold while I connect you."
        audio = await tts_url(transfer_msg)
        return _xml(transfer_to_agent_twiml(audio, settings.agent_transfer_number))

    if requires_otp:
        audio = await tts_url(response_text)
        action = f"{settings.public_base_url}/webhook/call/otp"
        return _xml(ask_pin_twiml(audio, action, num_digits=6))

    audio = await tts_url(response_text)
    action = f"{settings.public_base_url}/webhook/call/intent"
    return _xml(play_and_gather_twiml(audio, action))


# ── 5. OTP verification ───────────────────────────────────────────────────────

@router.post("/otp")
async def verify_otp_endpoint(
    CallSid: Annotated[str, Form()],
    Digits: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    session = await load_session(CallSid)
    if session is None or not session.pending_action:
        return _xml(error_twiml("Session error. Please call back."))

    digits = (Digits or "").strip()
    valid = await verify_otp(CallSid, digits)

    if not valid:
        audio = await tts_url(
            "That code didn't match. Please try again, "
            "or say 'cancel' to go back to the main menu."
        )
        action = f"{settings.public_base_url}/webhook/call/otp"
        return _xml(ask_pin_twiml(audio, action, num_digits=6))

    pending = session.pending_action
    if pending == "fund_transfer":
        response_text = await complete_transfer(session)
    elif pending == "bill_payment":
        response_text = await complete_bill_payment(session)
    else:
        response_text = "Action completed successfully. Anything else I can help with?"
        session.clear_pending()
        await save_session(session)

    audio = await tts_url(response_text)
    action = f"{settings.public_base_url}/webhook/call/intent"
    return _xml(play_and_gather_twiml(audio, action))


# ── 6. Voice confirmation (yes/no) ────────────────────────────────────────────

@router.post("/confirm")
async def voice_confirm(
    CallSid: Annotated[str, Form()],
    SpeechResult: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db),
):
    session = await load_session(CallSid)
    if session is None or not session.pending_action:
        return _xml(error_twiml("Session error. Please call back."))

    answer = (SpeechResult or "").strip().lower()
    confirmed = "yes" in answer or "yeah" in answer or "correct" in answer

    pending = session.pending_action

    if not confirmed:
        session.clear_pending()
        await save_session(session)
        audio = await tts_url("No problem, I've cancelled that. Is there anything else I can help you with?")
        action = f"{settings.public_base_url}/webhook/call/intent"
        return _xml(play_and_gather_twiml(audio, action))

    if pending == "card_unblock":
        response_text = await handle_card_unblock_confirm(session)
    else:
        response_text = "Done. Is there anything else I can help you with?"
        session.clear_pending()
        await save_session(session)

    audio = await tts_url(response_text)
    action = f"{settings.public_base_url}/webhook/call/intent"
    return _xml(play_and_gather_twiml(audio, action))


# ── 7. Call status (end of call) ─────────────────────────────────────────────

@router.post("/status")
async def call_status(
    CallSid: Annotated[str, Form()],
    CallStatus: Annotated[str, Form()],
    db: AsyncSession = Depends(get_db),
):
    if CallStatus not in ("completed", "busy", "failed", "no-answer", "canceled"):
        return Response(status_code=204)

    session = await load_session(CallSid)

    from sqlalchemy import select
    result = await db.execute(select(CallLog).where(CallLog.call_sid == CallSid))
    log = result.scalar_one_or_none()

    if log and session:
        log.ended_at = datetime.now(timezone.utc)
        log.user_id = session.user_id
        log.auth_result = {
            "name_verified": session.auth.name_verified,
            "pin_verified": session.auth.pin_verified,
            "biometric_score": session.auth.biometric_score,
            "risk_level": session.auth.risk_level,
        }
        log.transcript = [t.model_dump() for t in session.transcript]
        log.intent_log = session.intent_log
        log.biometric_score = session.auth.biometric_score
        db.add(log)
        await db.commit()

    await delete_session(CallSid)
    return Response(status_code=204)
