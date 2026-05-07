from app.models.call_session import CallSession
from app.services.bank_api import bank_api


async def get_transactions_response(session: CallSession, limit: int = 3) -> str:
    txs = await bank_api.get_transactions(session.user_id, limit=limit)

    if not txs:
        return "I don't see any recent transactions on your account. Is there anything else I can help you with?"

    parts = []
    for t in txs:
        action = "debit of" if t["amount"] < 0 else "credit of"
        amount = abs(t["amount"])
        parts.append(f"{t['description']}, {action} {amount:.2f} dollars, on {t['date']}")

    listing = "; ".join(parts)
    return (
        f"Your last {len(txs)} transactions are: {listing}. "
        f"Would you like me to email you a full statement, or is there anything else I can help with?"
    )
