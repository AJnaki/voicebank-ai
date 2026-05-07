import uuid
from app.services.adapters.base import (
    BankAPIAdapter, BalanceResponse, Transaction, LoanResponse,
    CardResponse, PaymentResponse, TransferResponse,
    FixedDepositResponse, ChequeResponse,
)

MOCK_DATA: dict[int, dict] = {
    1: {
        "name": "John Smith",
        "email": "john.smith@email.com",
        "phone": "+15550001234",
        "account_number": "****4821",
        "balance": {"available": 12450.75, "total": 12600.00, "currency": "USD"},
        "transactions": [
            {"date": "2026-05-05", "description": "Amazon Purchase", "amount": -89.99, "category": "Shopping"},
            {"date": "2026-05-04", "description": "Salary Deposit", "amount": 3500.00, "category": "Income"},
            {"date": "2026-05-03", "description": "Netflix Subscription", "amount": -15.99, "category": "Entertainment"},
            {"date": "2026-05-02", "description": "Grocery Store", "amount": -123.45, "category": "Food"},
            {"date": "2026-05-01", "description": "Electric Bill", "amount": -85.00, "category": "Utilities"},
            {"date": "2026-04-30", "description": "ATM Withdrawal", "amount": -200.00, "category": "Cash"},
            {"date": "2026-04-29", "description": "Gas Station", "amount": -45.00, "category": "Transport"},
            {"date": "2026-04-28", "description": "Restaurant", "amount": -62.50, "category": "Food"},
        ],
        "card_last_four": "4821",
        "loan": {
            "loan_id": "LN-2024-0042",
            "outstanding_balance": 18500.00,
            "emi_amount": 350.00,
            "next_due_date": "2026-05-15",
            "months_remaining": 53,
        },
        "fixed_deposit": {
            "fd_id": "FD-2025-0019",
            "principal": 10000.00,
            "interest_rate": 5.25,
            "maturity_date": "2027-01-15",
            "maturity_amount": 11102.50,
            "currency": "USD",
        },
        "cheques": {
            "004521": {"status": "cleared", "amount": 1200.00, "date": "2026-05-03"},
            "004522": {"status": "pending", "amount": 500.00, "date": None},
            "004520": {"status": "bounced", "amount": 250.00, "date": "2026-04-28"},
        },
    }
}


def _account(user_id: int) -> dict:
    return MOCK_DATA.get(user_id, MOCK_DATA[1])


class MockBankAdapter(BankAPIAdapter):
    async def get_balance(self, user_id: int) -> BalanceResponse:
        acc = _account(user_id)
        return BalanceResponse(
            available_balance=acc["balance"]["available"],
            total_balance=acc["balance"]["total"],
            currency=acc["balance"]["currency"],
            account_number=acc["account_number"],
        )

    async def get_transactions(self, user_id: int, limit: int = 5) -> list[Transaction]:
        txs = _account(user_id)["transactions"][:limit]
        return [Transaction(**t) for t in txs]

    async def get_statement_transactions(
        self, user_id: int, month: int, year: int
    ) -> list[Transaction]:
        all_txs = _account(user_id)["transactions"]
        prefix = f"{year}-{month:02d}"
        filtered = [t for t in all_txs if t["date"].startswith(prefix)]
        return [Transaction(**t) for t in filtered] if filtered else [Transaction(**t) for t in all_txs]

    async def block_card(self, user_id: int, reason: str = "lost") -> CardResponse:
        last_four = _account(user_id)["card_last_four"]
        return CardResponse(success=True, card_last_four=last_four, message="Card blocked")

    async def unblock_card(self, user_id: int) -> CardResponse:
        last_four = _account(user_id)["card_last_four"]
        return CardResponse(success=True, card_last_four=last_four, message="Card unblocked")

    async def dispute_transaction(
        self, user_id: int, description: str, amount: float
    ) -> PaymentResponse:
        ref = f"DISP-{uuid.uuid4().hex[:8].upper()}"
        return PaymentResponse(success=True, reference=ref, message="Dispute logged")

    async def get_loan(self, user_id: int) -> LoanResponse:
        loan = _account(user_id)["loan"]
        return LoanResponse(**loan)

    async def pay_bill(self, user_id: int, biller: str, amount: float) -> PaymentResponse:
        ref = f"BILL-{uuid.uuid4().hex[:8].upper()}"
        return PaymentResponse(success=True, reference=ref, message=f"Paid {biller}")

    async def transfer_funds(
        self, user_id: int, destination: str, amount: float
    ) -> TransferResponse:
        ref = f"TXN-{uuid.uuid4().hex[:8].upper()}"
        return TransferResponse(success=True, reference=ref, message=f"Transferred to {destination}")

    async def get_fixed_deposit(self, user_id: int) -> FixedDepositResponse:
        fd = _account(user_id)["fixed_deposit"]
        return FixedDepositResponse(**fd)

    async def get_cheque_status(self, user_id: int, cheque_number: str) -> ChequeResponse:
        cheques = _account(user_id)["cheques"]
        if cheque_number not in cheques:
            return ChequeResponse(cheque_number=cheque_number, status="not_found", amount=None, date=None)
        c = cheques[cheque_number]
        return ChequeResponse(cheque_number=cheque_number, **c)
