import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.call_session import CallSession
from app.handlers.intent_handler import route_intent, STATIC_RESPONSES
from app.services.bank_api import BalanceResponse


def _session() -> CallSession:
    s = CallSession(call_sid="CA999", bank_name="Test Bank")
    s.user_id = 1
    s.user_name = "Jane Doe"
    s.account_number = "****1234"
    s.auth.fully_authenticated = True
    return s


@pytest.mark.asyncio
async def test_balance_intent_returns_balance():
    with (
        patch("app.handlers.intent_handler.bank_api.get_balance", new_callable=AsyncMock) as mock_bal,
        patch("app.handlers.intent_handler.bank_api.get_transactions", new_callable=AsyncMock) as mock_tx,
        patch("app.handlers.intent_handler.classify_intent", new_callable=AsyncMock) as mock_ai,
        patch("app.handlers.intent_handler.save_session", new_callable=AsyncMock),
        patch("app.handlers.balance_handler.bank_api.get_balance", new_callable=AsyncMock) as mock_bal2,
    ):
        mock_bal.return_value = BalanceResponse(5000.0, 5000.0, "USD", "****1234")
        mock_bal2.return_value = BalanceResponse(5000.0, 5000.0, "USD", "****1234")
        mock_tx.return_value = []
        mock_ai.return_value = {"intent": "balance", "response_text": "", "escalate": False}

        text, escalate = await route_intent("what's my balance", _session())

    assert escalate is False
    assert "five thousand" in text.lower() or "5,000" in text


@pytest.mark.asyncio
async def test_live_agent_escalates():
    with (
        patch("app.handlers.intent_handler.bank_api.get_balance", new_callable=AsyncMock) as mock_bal,
        patch("app.handlers.intent_handler.bank_api.get_transactions", new_callable=AsyncMock) as mock_tx,
        patch("app.handlers.intent_handler.classify_intent", new_callable=AsyncMock) as mock_ai,
        patch("app.handlers.intent_handler.save_session", new_callable=AsyncMock),
    ):
        mock_bal.return_value = BalanceResponse(0, 0, "USD", "****1234")
        mock_tx.return_value = []
        mock_ai.return_value = {
            "intent": "live_agent",
            "response_text": "Connecting you now.",
            "escalate": True,
            "escalate_reason": "caller_request",
        }

        text, escalate = await route_intent("talk to a person", _session())

    assert escalate is True


@pytest.mark.asyncio
async def test_card_block_uses_static_response():
    with (
        patch("app.handlers.intent_handler.bank_api.get_balance", new_callable=AsyncMock) as mock_bal,
        patch("app.handlers.intent_handler.bank_api.get_transactions", new_callable=AsyncMock) as mock_tx,
        patch("app.handlers.intent_handler.classify_intent", new_callable=AsyncMock) as mock_ai,
        patch("app.handlers.intent_handler.save_session", new_callable=AsyncMock),
    ):
        mock_bal.return_value = BalanceResponse(0, 0, "USD", "****1234")
        mock_tx.return_value = []
        mock_ai.return_value = {"intent": "card_block", "response_text": "", "escalate": False}

        text, escalate = await route_intent("block my card", _session())

    assert escalate is False
    assert "frozen" in text.lower() or "card" in text.lower()


@pytest.mark.asyncio
async def test_unknown_intent_not_escalated():
    with (
        patch("app.handlers.intent_handler.bank_api.get_balance", new_callable=AsyncMock) as mock_bal,
        patch("app.handlers.intent_handler.bank_api.get_transactions", new_callable=AsyncMock) as mock_tx,
        patch("app.handlers.intent_handler.classify_intent", new_callable=AsyncMock) as mock_ai,
        patch("app.handlers.intent_handler.save_session", new_callable=AsyncMock),
    ):
        mock_bal.return_value = BalanceResponse(0, 0, "USD", "****1234")
        mock_tx.return_value = []
        mock_ai.return_value = {
            "intent": "unknown",
            "response_text": "I didn't understand that.",
            "escalate": False,
        }

        text, escalate = await route_intent("xyzzy", _session())

    assert escalate is False
