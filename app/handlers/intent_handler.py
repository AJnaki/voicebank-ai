from app.models.call_session import CallSession
from app.services.bank_api import bank_api
from app.services.ai_engine_service import classify_intent
from app.db.redis_client import save_session
from app.handlers.balance_handler import get_balance_response
from app.handlers.transaction_handler import get_transactions_response


STATIC_RESPONSES = {
    "statement": (
        "I'll send your latest statement to the email address registered on your account. "
        "You should receive it within a few minutes. Anything else?"
    ),
    "card_block": (
        "I've immediately frozen your card. No new transactions can be processed. "
        "Would you like to report it as lost or stolen? Say yes or no."
    ),
    "bill_payment": (
        "I can help with bill payments. Could you tell me the biller name and the amount you'd like to pay?"
    ),
    "fund_transfer": (
        "For security, fund transfers require a one-time password sent to your registered mobile number. "
        "Please call back or visit a branch to complete the transfer. Anything else I can help with?"
    ),
    "fraud_report": (
        "I'm logging a fraud alert on your account right now and flagging it for our fraud team. "
        "They'll contact you within 24 hours. Would you like me to block your card immediately as well?"
    ),
    "loan_status": None,  # fetched dynamically
}


async def route_intent(transcript: str, session: CallSession) -> tuple[str, bool]:
    """
    Returns (response_text, should_escalate).
    Fetches real data for balance/transactions/loan; uses static text for others.
    """
    balance_data = await bank_api.get_balance(session.user_id)
    transactions = await bank_api.get_transactions(session.user_id, limit=5)

    result = await classify_intent(
        transcript=transcript,
        session=session,
        balance=balance_data.available_balance,
        currency=balance_data.currency,
        transactions=transactions,
    )

    intent = result.get("intent", "unknown")
    escalate = result.get("escalate", False)

    session.log_intent(intent)
    session.add_turn("caller", transcript)
    await save_session(session)

    if escalate or intent == "live_agent":
        return result.get("response_text", "Connecting you to a team member now."), True

    if intent == "balance":
        text = await get_balance_response(session)
    elif intent == "transactions":
        text = await get_transactions_response(session)
    elif intent == "loan_status":
        loan = await bank_api.get_loan(session.user_id)
        text = (
            f"Your outstanding loan balance is {loan.outstanding_balance:,.0f} dollars. "
            f"Your next payment of {loan.emi_amount:.0f} dollars is due on {loan.next_due_date}. "
            f"You have {loan.months_remaining} months remaining. Anything else?"
        )
    else:
        text = STATIC_RESPONSES.get(intent) or result.get(
            "response_text",
            "I'm sorry, I didn't understand that. Could you rephrase what you need?",
        )

    session.add_turn("assistant", text)
    await save_session(session)
    return text, False
