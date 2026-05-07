import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.redis_client import save_session
from app.models.call_session import CallSession
from app.models.user import User
from app.services.name_matcher import find_user_by_spoken_name

settings = get_settings()

MAX_PIN_ATTEMPTS = 3


async def handle_name(
    spoken_name: str, call_sid: str, db: AsyncSession
) -> tuple[CallSession, str]:
    """
    Match spoken name against the database.
    Returns (session, outcome) where outcome is:
      "found_high"    — confident match (≥90), proceed to PIN
      "found_medium"  — moderate match (75-89), ask confirming question
      "not_found"     — no match, ask to retry
    """
    session = CallSession(call_sid=call_sid, bank_name=settings.bank_name)
    session.add_turn("caller", spoken_name)

    user, score = await find_user_by_spoken_name(spoken_name, db)

    if user is None:
        return session, "not_found"

    session.user_id = user.id
    session.user_name = user.full_name
    session.account_number = user.account_number
    session.auth.name_verified = True

    await save_session(session)
    return session, "found_high" if score >= 90 else "found_medium"


async def handle_pin(
    digits: str, session: CallSession, db: AsyncSession
) -> tuple[str, CallSession]:
    """
    Verify the entered PIN digits.
    Returns outcome: "verified" | "wrong" | "locked"
    """
    user = await db.get(User, session.user_id)
    if user is None or user.is_locked:
        return "locked", session

    correct = bcrypt.checkpw(digits.encode(), user.pin_hash.encode())

    if correct:
        user.pin_attempts = 0
        db.add(user)
        await db.commit()

        session.auth.pin_verified = True
        session.auth.fully_authenticated = True
        await save_session(session)
        return "verified", session

    user.pin_attempts += 1
    if user.pin_attempts >= MAX_PIN_ATTEMPTS:
        user.is_locked = True
        db.add(user)
        await db.commit()
        return "locked", session

    session.auth.pin_attempts = user.pin_attempts
    db.add(user)
    await db.commit()
    await save_session(session)
    return "wrong", session


async def record_biometric_score(score: int, session: CallSession) -> None:
    session.auth.biometric_score = score
    session.auth.biometric_verified = score >= 70
    await save_session(session)
