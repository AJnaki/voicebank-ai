from app.models.call_session import CallSession
from app.services.bank_api import bank_api
from app.db.redis_client import save_session


async def handle_card_block(session: CallSession) -> str:
    result = await bank_api.block_card(session.user_id, reason="caller_request")
    if result.success:
        return (
            f"I've immediately frozen your card ending in {result.card_last_four}. "
            f"No new transactions can be processed. "
            f"Would you like to report it as lost or stolen, or is there anything else I can help with?"
        )
    return "I wasn't able to block your card right now. Please call back or visit a branch immediately."


async def handle_card_unblock_request(session: CallSession) -> str:
    session.set_pending("card_unblock")
    await save_session(session)
    return (
        "I can unblock your card. For security, please confirm: "
        "say yes to unblock your card, or no to cancel."
    )


async def handle_card_unblock_confirm(session: CallSession) -> str:
    result = await bank_api.unblock_card(session.user_id)
    session.clear_pending()
    await save_session(session)
    if result.success:
        return (
            f"Your card ending in {result.card_last_four} has been unblocked. "
            f"You can now use it for transactions. Anything else?"
        )
    return "I wasn't able to unblock your card right now. Please contact support."


async def handle_card_dispute(session: CallSession, description: str = "", amount: float = 0.0) -> str:
    result = await bank_api.dispute_transaction(session.user_id, description, amount)
    if result.success:
        return (
            f"I've logged a dispute with reference number {result.reference}. "
            f"Our fraud team will review it and contact you within 24 to 48 hours. "
            f"Would you also like me to block your card as a precaution?"
        )
    return "I wasn't able to log the dispute right now. Please call back or visit a branch."
