# Phase 2 — Core Banking Features

**Goal:** Replace the mock bank API with real core banking integration and build out all major banking intents with production-quality responses.

**Timeline:** 4–6 weeks  
**Status:** ⬜ Upcoming

---

## Deliverables

| # | Deliverable | Description |
|---|---|---|
| 2.1 | Real bank API integration | Connect to bank's core banking REST API |
| 2.2 | Balance enquiry | Live balance + available credit |
| 2.3 | Recent transactions | Last N transactions, filterable by date/merchant |
| 2.4 | Statement dispatch | Generate PDF, email to registered address |
| 2.5 | Bill payment | Pay utility bills, credit cards, scheduled payments |
| 2.6 | Card block / unblock | Instant card freeze + report lost/stolen |
| 2.7 | Card dispute | Log unauthorized transaction dispute |
| 2.8 | Loan status | Outstanding balance, EMI amount, next due date |
| 2.9 | Fund transfer | Transfer to own accounts or registered beneficiaries |
| 2.10 | Mini statement via SMS | Send last 5 transactions as SMS |
| 2.11 | Cheque status | Track cheque clearance |
| 2.12 | Fixed deposit enquiry | FD balance, maturity date, interest rate |

---

## Bank API Integration

Core banking systems vary by bank (Temenos, FIS, Finacle, custom REST). VoiceBank AI uses an **adapter pattern** — a bank-specific adapter maps our standard interface to whatever the bank's API provides.

```python
# Standard interface all adapters must implement:
class BankAPIAdapter:
    async def get_balance(self, account_id: str) -> BalanceResponse: ...
    async def get_transactions(self, account_id: str, limit: int) -> list[Transaction]: ...
    async def get_statement(self, account_id: str, month: int, year: int) -> StatementResponse: ...
    async def pay_bill(self, account_id: str, biller: str, amount: float) -> PaymentResponse: ...
    async def block_card(self, card_id: str, reason: str) -> CardResponse: ...
    async def get_loan_status(self, loan_id: str) -> LoanResponse: ...
    async def transfer_funds(self, from_id: str, to_id: str, amount: float) -> TransferResponse: ...
```

Each bank gets its own adapter class (`FirstNationalAdapter`, `CityBankAdapter`) that inherits from `BankAPIAdapter`.

---

## Response Quality Standards

All spoken responses must be:

- **Short** — max 2–3 sentences (caller can always ask for more)
- **Natural** — formatted for speech not text ("twelve thousand four hundred fifty dollars", not "$12,450")
- **Actionable** — always end with "Anything else I can help with?"

### Examples

**Balance:**
> *"Your available balance is twelve thousand four hundred fifty dollars and seventy-five cents. Your total account balance including pending transactions is twelve thousand six hundred dollars. Anything else?"*

**Recent Transactions:**
> *"Your last three transactions are: Amazon, eighty-nine dollars and ninety-nine cents on May fifth; a salary deposit of three thousand five hundred dollars on May fourth; and Netflix, fifteen dollars and ninety-nine cents on May third. Would you like me to email you a full statement?"*

**Card Block:**
> *"I've immediately frozen your card ending in four eight two one. No new transactions can be made. I've also flagged this for our fraud team. Would you like to report this as lost or stolen?"*

---

## Security Gates for Transactions

Some actions require additional confirmation even after auth:

| Action | Extra Gate |
|---|---|
| Fund transfer > $500 | OTP sent to registered mobile |
| Card unblock | Confirm: "Say yes to confirm you are unblocking your card" |
| Bill payment first-time biller | OTP confirmation |
| Change registered email/phone | Must go to live agent |

---

## PDF Statement Generation

```
Request received → Bank API returns transaction data
→ Python (reportlab/weasyprint) generates PDF
→ PDF uploaded to S3 with pre-signed URL (expires 24h)
→ Email sent via SendGrid to registered email address
→ Caller told: "I've emailed your statement to j***@gmail.com"
```

---

## Definition of Done

- [ ] All 12 banking intents connected to real (or staging) bank API
- [ ] Adapter pattern implemented and tested with 2+ bank API schemas
- [ ] PDF statement generation and email dispatch working
- [ ] OTP flow working for high-value transactions
- [ ] Card block takes effect within 5 seconds of call instruction
- [ ] Fund transfer tested with staging bank environment
- [ ] All spoken responses pass "natural speech" review
- [ ] Error handling: bank API down → graceful fallback message + agent offer
- [ ] End-to-end regression tests cover all 12 intents
