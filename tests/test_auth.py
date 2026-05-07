import pytest
import bcrypt
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.call_session import CallSession, AuthState
from app.handlers.auth_handler import handle_pin, MAX_PIN_ATTEMPTS


def _make_user(pin: str = "123456", attempts: int = 0, locked: bool = False):
    user = MagicMock()
    user.id = 1
    user.first_name = "John"
    user.last_name = "Smith"
    user.full_name = "John Smith"
    user.account_number = "****4821"
    user.pin_hash = bcrypt.hashpw(pin.encode(), bcrypt.gensalt()).decode()
    user.pin_attempts = attempts
    user.is_locked = locked
    return user


def _make_session(user_id: int = 1) -> CallSession:
    session = CallSession(call_sid="CA123", bank_name="Test Bank")
    session.user_id = user_id
    session.user_name = "John Smith"
    session.account_number = "****4821"
    return session


@pytest.mark.asyncio
async def test_correct_pin_verifies_session():
    user = _make_user("123456")
    db = AsyncMock()
    db.get = AsyncMock(return_value=user)
    db.add = MagicMock()
    db.commit = AsyncMock()

    with patch("app.handlers.auth_handler.save_session", new_callable=AsyncMock):
        outcome, session = await handle_pin("123456", _make_session(), db)

    assert outcome == "verified"
    assert session.auth.pin_verified is True
    assert session.auth.fully_authenticated is True


@pytest.mark.asyncio
async def test_wrong_pin_increments_attempts():
    user = _make_user("123456", attempts=0)
    db = AsyncMock()
    db.get = AsyncMock(return_value=user)
    db.add = MagicMock()
    db.commit = AsyncMock()

    with patch("app.handlers.auth_handler.save_session", new_callable=AsyncMock):
        outcome, session = await handle_pin("000000", _make_session(), db)

    assert outcome == "wrong"
    assert user.pin_attempts == 1


@pytest.mark.asyncio
async def test_third_wrong_pin_locks_account():
    user = _make_user("123456", attempts=2)
    db = AsyncMock()
    db.get = AsyncMock(return_value=user)
    db.add = MagicMock()
    db.commit = AsyncMock()

    with patch("app.handlers.auth_handler.save_session", new_callable=AsyncMock):
        outcome, _ = await handle_pin("000000", _make_session(), db)

    assert outcome == "locked"
    assert user.is_locked is True


@pytest.mark.asyncio
async def test_already_locked_account():
    user = _make_user("123456", locked=True)
    db = AsyncMock()
    db.get = AsyncMock(return_value=user)

    with patch("app.handlers.auth_handler.save_session", new_callable=AsyncMock):
        outcome, _ = await handle_pin("123456", _make_session(), db)

    assert outcome == "locked"


def test_risk_level_low_when_all_verified():
    auth = AuthState(name_verified=True, pin_verified=True, biometric_score=90)
    assert auth.risk_level == "low"


def test_risk_level_medium_partial_biometric():
    auth = AuthState(name_verified=True, pin_verified=True, biometric_score=65)
    assert auth.risk_level == "low"  # 30+50+10 = 90 → still low


def test_risk_level_no_biometric():
    auth = AuthState(name_verified=True, pin_verified=True)
    assert auth.risk_level == "low"  # 30+50 = 80 → low


def test_risk_level_pin_only():
    auth = AuthState(name_verified=False, pin_verified=True)
    assert auth.risk_level == "high"  # 50 points < 60 threshold → high
