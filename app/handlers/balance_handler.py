from app.models.call_session import CallSession
from app.services.bank_api import bank_api


async def get_balance_response(session: CallSession) -> str:
    balance = await bank_api.get_balance(session.user_id)

    def _amount_words(amount: float) -> str:
        dollars = int(amount)
        cents = round((amount - dollars) * 100)
        parts = []
        if dollars:
            parts.append(f"{dollars:,} dollars")
        if cents:
            parts.append(f"{cents} cents")
        return " and ".join(parts) if parts else "zero dollars"

    avail = _amount_words(balance.available_balance)
    total = _amount_words(balance.total_balance)

    if balance.available_balance == balance.total_balance:
        return (
            f"Your available balance is {avail}. "
            f"Is there anything else I can help you with?"
        )
    return (
        f"Your available balance is {avail}. "
        f"Your total balance including pending transactions is {total}. "
        f"Anything else I can help with?"
    )
