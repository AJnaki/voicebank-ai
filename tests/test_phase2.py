import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.models.call_session import CallSession
from app.services.adapters.mock_adapter import MockBankAdapter
from app.handlers.balance_handler import get_balance_response
from app.handlers.transaction_handler import get_transactions_response
from app.handlers.card_handler import handle_card_block, handle_card_dispute
from app.handlers.fd_handler import get_fd_response
from app.services.adapters.base import (
    BalanceResponse, Transaction, LoanResponse,
    CardResponse, PaymentResponse, FixedDepositResponse, ChequeResponse,
)


def _session() -> CallSession:
    s = CallSession(call_sid="CA-P2-TEST", bank_name="Test Bank")
    s.user_id = 1
    s.user_name = "John Smith"
    s.account_number = "****4821"
    s.auth.fully_authenticated = True
    return s


# ── Adapter ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_mock_adapter_balance():
    adapter = MockBankAdapter()
    result = await adapter.get_balance(1)
    assert result.available_balance == 12450.75
    assert result.currency == "USD"


@pytest.mark.asyncio
async def test_mock_adapter_transactions_limit():
    adapter = MockBankAdapter()
    txs = await adapter.get_transactions(1, limit=3)
    assert len(txs) == 3
    assert txs[0].description == "Amazon Purchase"


@pytest.mark.asyncio
async def test_mock_adapter_fixed_deposit():
    adapter = MockBankAdapter()
    fd = await adapter.get_fixed_deposit(1)
    assert fd.principal == 10000.00
    assert fd.interest_rate == 5.25


@pytest.mark.asyncio
async def test_mock_adapter_cheque_cleared():
    adapter = MockBankAdapter()
    result = await adapter.get_cheque_status(1, "004521")
    assert result.status == "cleared"
    assert result.amount == 1200.00


@pytest.mark.asyncio
async def test_mock_adapter_cheque_not_found():
    adapter = MockBankAdapter()
    result = await adapter.get_cheque_status(1, "999999")
    assert result.status == "not_found"


@pytest.mark.asyncio
async def test_mock_adapter_card_block():
    adapter = MockBankAdapter()
    result = await adapter.block_card(1)
    assert result.success is True
    assert result.card_last_four == "4821"


@pytest.mark.asyncio
async def test_mock_adapter_dispute():
    adapter = MockBankAdapter()
    result = await adapter.dispute_transaction(1, "Amazon", 89.99)
    assert result.success is True
    assert result.reference.startswith("DISP-")


@pytest.mark.asyncio
async def test_mock_adapter_transfer():
    adapter = MockBankAdapter()
    result = await adapter.transfer_funds(1, "savings", 200.0)
    assert result.success is True
    assert result.reference.startswith("TXN-")


# ── Handlers ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_balance_handler_equal_balances():
    with patch("app.handlers.balance_handler.bank_api.get_balance", new_callable=AsyncMock) as mock:
        mock.return_value = BalanceResponse(5000.0, 5000.0, "USD", "****1234")
        text = await get_balance_response(_session())
    assert "five thousand" in text.lower() or "5,000" in text
    assert "anything else" in text.lower()


@pytest.mark.asyncio
async def test_balance_handler_pending_transactions():
    with patch("app.handlers.balance_handler.bank_api.get_balance", new_callable=AsyncMock) as mock:
        mock.return_value = BalanceResponse(5000.0, 5200.0, "USD", "****1234")
        text = await get_balance_response(_session())
    assert "available" in text.lower()
    assert "total" in text.lower()


@pytest.mark.asyncio
async def test_transaction_handler_formats_correctly():
    txs = [
        Transaction("2026-05-05", "Amazon", -89.99, "Shopping"),
        Transaction("2026-05-04", "Salary", 3500.0, "Income"),
        Transaction("2026-05-03", "Netflix", -15.99, "Entertainment"),
    ]
    with patch("app.handlers.transaction_handler.bank_api.get_transactions", new_callable=AsyncMock) as mock:
        mock.return_value = txs
        text = await get_transactions_response(_session(), limit=3)
    assert "Amazon" in text
    assert "Salary" in text
    assert "debit" in text.lower() or "credit" in text.lower()


@pytest.mark.asyncio
async def test_card_block_handler():
    with patch("app.handlers.card_handler.bank_api.block_card", new_callable=AsyncMock) as mock:
        mock.return_value = CardResponse(True, "4821", "Card blocked")
        text = await handle_card_block(_session())
    assert "frozen" in text.lower() or "blocked" in text.lower()
    assert "4821" in text


@pytest.mark.asyncio
async def test_card_dispute_handler():
    with patch("app.handlers.card_handler.bank_api.dispute_transaction", new_callable=AsyncMock) as mock:
        mock.return_value = PaymentResponse(True, "DISP-ABC123", "Logged")
        text = await handle_card_dispute(_session(), "Amazon", 99.99)
    assert "DISP-ABC123" in text
    assert "fraud" in text.lower() or "dispute" in text.lower()


@pytest.mark.asyncio
async def test_fd_handler():
    with patch("app.handlers.fd_handler.bank_api.get_fixed_deposit", new_callable=AsyncMock) as mock:
        mock.return_value = FixedDepositResponse(
            "FD-001", 10000.0, 5.25, "2027-01-15", 11102.50, "USD"
        )
        text = await get_fd_response(_session())
    assert "10,000" in text or "ten thousand" in text.lower()
    assert "5.25" in text
    assert "2027-01-15" in text


# ── OTP service ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_otp_generate_and_verify():
    from app.services.otp_service import generate_otp, verify_otp

    mock_redis = AsyncMock()
    mock_redis.setex = AsyncMock()
    mock_redis.get = AsyncMock(return_value="123456")
    mock_redis.delete = AsyncMock()

    with patch("app.services.otp_service.get_redis", return_value=mock_redis):
        otp = await generate_otp("CA-OTP-TEST")
        assert len(otp) == 6
        assert otp.isdigit()

        mock_redis.get.return_value = otp
        valid = await verify_otp("CA-OTP-TEST", otp)
        assert valid is True


@pytest.mark.asyncio
async def test_otp_wrong_code_rejected():
    from app.services.otp_service import verify_otp

    mock_redis = AsyncMock()
    mock_redis.get = AsyncMock(return_value="123456")

    with patch("app.services.otp_service.get_redis", return_value=mock_redis):
        valid = await verify_otp("CA-OTP-TEST", "000000")
        assert valid is False


# ── CallSession pending state ─────────────────────────────────────────────────

def test_session_set_and_clear_pending():
    session = _session()
    session.set_pending("fund_transfer", destination="savings", amount=500.0)
    assert session.pending_action == "fund_transfer"
    assert session.pending_data["amount"] == 500.0

    session.clear_pending()
    assert session.pending_action is None
    assert session.pending_data == {}


# ── Statement PDF ─────────────────────────────────────────────────────────────

def test_statement_pdf_generates_bytes():
    from app.services.statement_service import generate_statement_pdf
    txs = [
        Transaction("2026-05-05", "Amazon", -89.99, "Shopping"),
        Transaction("2026-05-04", "Salary", 3500.0, "Income"),
    ]
    pdf = generate_statement_pdf("John Smith", "****4821", "Test Bank", txs, "May 2026")
    assert isinstance(pdf, bytes)
    assert len(pdf) > 1000
    assert pdf[:4] == b"%PDF"
