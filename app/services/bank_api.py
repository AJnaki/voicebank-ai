from dataclasses import dataclass


@dataclass
class BalanceResponse:
    available_balance: float
    total_balance: float
    currency: str
    account_number: str


@dataclass
class LoanResponse:
    loan_id: str
    outstanding_balance: float
    emi_amount: float
    next_due_date: str
    months_remaining: int


MOCK_ACCOUNTS: dict[int, dict] = {
    1: {
        "name": "John Smith",
        "account_number": "****4821",
        "balance": {"available": 12450.75, "total": 12600.00, "currency": "USD"},
        "transactions": [
            {"date": "2026-05-05", "description": "Amazon Purchase", "amount": -89.99, "category": "Shopping"},
            {"date": "2026-05-04", "description": "Salary Deposit", "amount": 3500.00, "category": "Income"},
            {"date": "2026-05-03", "description": "Netflix Subscription", "amount": -15.99, "category": "Entertainment"},
            {"date": "2026-05-02", "description": "Grocery Store", "amount": -123.45, "category": "Food"},
            {"date": "2026-05-01", "description": "Electric Bill", "amount": -85.00, "category": "Utilities"},
        ],
        "loan": {
            "loan_id": "LN-2024-0042",
            "outstanding_balance": 18500.00,
            "emi_amount": 350.00,
            "next_due_date": "2026-05-15",
            "months_remaining": 53,
        },
    }
}


class MockBankAPI:
    def _account(self, user_id: int) -> dict:
        return MOCK_ACCOUNTS.get(user_id, MOCK_ACCOUNTS[1])

    async def get_balance(self, user_id: int) -> BalanceResponse:
        acc = self._account(user_id)
        return BalanceResponse(
            available_balance=acc["balance"]["available"],
            total_balance=acc["balance"]["total"],
            currency=acc["balance"]["currency"],
            account_number=acc["account_number"],
        )

    async def get_transactions(self, user_id: int, limit: int = 5) -> list[dict]:
        return self._account(user_id)["transactions"][:limit]

    async def get_loan(self, user_id: int) -> LoanResponse:
        loan = self._account(user_id)["loan"]
        return LoanResponse(**loan)

    async def block_card(self, user_id: int) -> bool:
        return True

    async def pay_bill(self, user_id: int, biller: str, amount: float) -> bool:
        return True


bank_api = MockBankAPI()
