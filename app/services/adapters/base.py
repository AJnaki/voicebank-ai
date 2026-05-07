from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class BalanceResponse:
    available_balance: float
    total_balance: float
    currency: str
    account_number: str


@dataclass
class Transaction:
    date: str
    description: str
    amount: float
    category: str


@dataclass
class LoanResponse:
    loan_id: str
    outstanding_balance: float
    emi_amount: float
    next_due_date: str
    months_remaining: int


@dataclass
class CardResponse:
    success: bool
    card_last_four: str
    message: str


@dataclass
class PaymentResponse:
    success: bool
    reference: str
    message: str


@dataclass
class TransferResponse:
    success: bool
    reference: str
    message: str


@dataclass
class FixedDepositResponse:
    fd_id: str
    principal: float
    interest_rate: float
    maturity_date: str
    maturity_amount: float
    currency: str


@dataclass
class ChequeResponse:
    cheque_number: str
    status: str        # "cleared", "pending", "bounced", "cancelled"
    amount: Optional[float]
    date: Optional[str]


class BankAPIAdapter(ABC):
    @abstractmethod
    async def get_balance(self, user_id: int) -> BalanceResponse: ...

    @abstractmethod
    async def get_transactions(self, user_id: int, limit: int = 5) -> list[Transaction]: ...

    @abstractmethod
    async def get_statement_transactions(
        self, user_id: int, month: int, year: int
    ) -> list[Transaction]: ...

    @abstractmethod
    async def block_card(self, user_id: int, reason: str = "lost") -> CardResponse: ...

    @abstractmethod
    async def unblock_card(self, user_id: int) -> CardResponse: ...

    @abstractmethod
    async def dispute_transaction(
        self, user_id: int, description: str, amount: float
    ) -> PaymentResponse: ...

    @abstractmethod
    async def get_loan(self, user_id: int) -> LoanResponse: ...

    @abstractmethod
    async def pay_bill(
        self, user_id: int, biller: str, amount: float
    ) -> PaymentResponse: ...

    @abstractmethod
    async def transfer_funds(
        self, user_id: int, destination: str, amount: float
    ) -> TransferResponse: ...

    @abstractmethod
    async def get_fixed_deposit(self, user_id: int) -> FixedDepositResponse: ...

    @abstractmethod
    async def get_cheque_status(
        self, user_id: int, cheque_number: str
    ) -> ChequeResponse: ...
