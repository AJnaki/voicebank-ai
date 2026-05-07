# Bank API Integration

## Adapter Pattern

Every bank has a different core banking API (Temenos, FIS, Finacle, or custom). VoiceBank AI uses an adapter pattern so the voice layer never changes — only the bank-specific adapter does.

```
VoiceBank AI Core
      │
      ▼
BankAPIAdapter (abstract interface)
      │
      ├── FirstNationalAdapter  → Temenos REST API
      ├── CityBankAdapter       → FIS JSON API
      └── RegionalBankAdapter   → Custom bank API
```

## Standard Interface

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date

@dataclass
class BalanceResponse:
    available_balance: float
    total_balance: float
    currency: str
    account_number: str

@dataclass
class Transaction:
    date: date
    description: str
    amount: float       # negative = debit, positive = credit
    category: str
    reference: str

@dataclass
class LoanResponse:
    loan_id: str
    outstanding_balance: float
    emi_amount: float
    next_due_date: date
    months_remaining: int

class BankAPIAdapter(ABC):
    @abstractmethod
    async def get_balance(self, account_id: str) -> BalanceResponse: ...
    
    @abstractmethod
    async def get_transactions(self, account_id: str, limit: int = 10) -> list[Transaction]: ...
    
    @abstractmethod
    async def get_statement_data(self, account_id: str, month: int, year: int) -> list[Transaction]: ...
    
    @abstractmethod
    async def block_card(self, card_id: str, reason: str) -> bool: ...
    
    @abstractmethod
    async def get_loan_status(self, loan_id: str) -> LoanResponse: ...
    
    @abstractmethod
    async def pay_bill(self, account_id: str, biller_id: str, amount: float) -> bool: ...
    
    @abstractmethod
    async def transfer_funds(self, from_account: str, to_account: str, amount: float) -> bool: ...
```

## Example Bank Adapter

```python
import httpx
from .base import BankAPIAdapter, BalanceResponse

class FirstNationalAdapter(BankAPIAdapter):
    def __init__(self, base_url: str, api_key: str):
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10.0
        )
    
    async def get_balance(self, account_id: str) -> BalanceResponse:
        resp = await self.client.get(f"/accounts/{account_id}/balance")
        resp.raise_for_status()
        data = resp.json()
        return BalanceResponse(
            available_balance=data["availableBalance"],
            total_balance=data["ledgerBalance"],
            currency=data["currency"],
            account_number=data["maskedAccountNumber"]
        )
```

## Error Handling

```python
# All handlers catch API errors gracefully:
try:
    balance = await bank_api.get_balance(session.account_id)
except httpx.TimeoutException:
    return "I'm having trouble reaching your account right now. Please try again in a moment, or I can connect you to an agent."
except httpx.HTTPStatusError as e:
    if e.response.status_code == 503:
        return "Our banking system is briefly unavailable. Shall I connect you to a live agent?"
    raise
```

## Rate Limiting & Caching

- Balance responses cached in Redis for 30 seconds per account
- Transactions cached for 60 seconds
- Cache invalidated immediately after any write operation (payment, transfer)
- Rate limit: max 10 API calls per call session
