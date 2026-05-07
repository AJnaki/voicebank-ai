from sqlalchemy.ext.asyncio import AsyncSession

from app.db.redis_client import save_session
from app.handlers.balance_handler import get_balance_response
from app.handlers.transaction_handler import get_transactions_response
from app.handlers.card_handler import handle_card_block, handle_card_dispute, handle_card_unblock_request
from app.handlers.fd_handler import get_fd_response
from app.handlers.transfer_handler import initiate_transfer
from app.handlers.bill_handler import initiate_bill_payment
from app.models.call_session import CallSession
from app.services.ai_engine_service import classify_intent
from app.services.bank_api import bank_api
from app.services.sms_service import send_mini_statement


async def route_intent(
    transcript: str, session: CallSession, db: AsyncSession
) -> tuple[str, bool, bool]:
    """
    Returns (response_text, should_escalate, requires_otp).
    requires_otp=True means the caller should be redirected to /webhook/call/otp.
    """
    balance_data = await bank_api.get_balance(session.user_id)
    transactions = await bank_api.get_transactions(session.user_id, limit=5)

    result = await classify_intent(
        transcript=transcript,
        session=session,
        balance=balance_data.available_balance,
        currency=balance_data.currency,
        transactions=[
            {"date": t.date, "description": t.description, "amount": t.amount}
            for t in transactions
        ],
    )

    intent = result.get("intent", "unknown")
    escalate = result.get("escalate", False)
    params = result.get("params", {})

    session.log_intent(intent)
    session.add_turn("caller", transcript)
    await save_session(session)

    if escalate or intent == "live_agent":
        return result.get("response_text", "Connecting you to a team member now."), True, False

    # ── Inline intents (no confirmation needed) ──────────────────────────────
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

    elif intent == "fd_enquiry":
        text = await get_fd_response(session)

    elif intent == "card_block":
        text = await handle_card_block(session)

    elif intent == "card_unblock":
        text = await handle_card_unblock_request(session)

    elif intent == "card_dispute":
        text = await handle_card_dispute(
            session,
            description=params.get("description", ""),
            amount=float(params.get("amount", 0)),
        )

    elif intent == "mini_statement":
        txs = await bank_api.get_transactions(session.user_id, limit=5)
        from app.models.user import User
        user = await db.get(User, session.user_id)
        if user and user.phone_number:
            await send_mini_statement(user.phone_number, session.bank_name, txs)
            text = (
                "I've sent your last five transactions as an SMS to your registered mobile number. "
                "Anything else I can help with?"
            )
        else:
            text = "I don't have a mobile number on file for your account."

    elif intent == "cheque_status":
        cheque_num = params.get("cheque_number", "")
        if not cheque_num:
            text = "Could you tell me the cheque number you'd like to check?"
        else:
            cheque = await bank_api.get_cheque_status(session.user_id, cheque_num)
            status_map = {
                "cleared": "has cleared successfully",
                "pending": "is still pending clearance",
                "bounced": "has bounced",
                "cancelled": "has been cancelled",
                "not_found": "could not be found in our records",
            }
            status_text = status_map.get(cheque.status, cheque.status)
            amount_text = f" for {cheque.amount:.2f} dollars" if cheque.amount else ""
            text = f"Cheque number {cheque_num}{amount_text} {status_text}. Anything else?"

    # ── OTP-gated intents ────────────────────────────────────────────────────
    elif intent == "fund_transfer":
        amount = float(params.get("amount", 0))
        destination = params.get("destination", "savings account")
        if amount <= 0:
            text = "How much would you like to transfer, and to which account?"
            session.add_turn("assistant", text)
            await save_session(session)
            return text, False, False
        text, needs_otp = await initiate_transfer(session, destination, amount, db)
        session.add_turn("assistant", text)
        await save_session(session)
        return text, False, needs_otp

    elif intent == "bill_payment":
        amount = float(params.get("amount", 0))
        biller = params.get("biller", "")
        if not biller or amount <= 0:
            text = "Which biller would you like to pay, and for how much?"
            session.add_turn("assistant", text)
            await save_session(session)
            return text, False, False
        text, needs_otp = await initiate_bill_payment(session, biller, amount, db)
        session.add_turn("assistant", text)
        await save_session(session)
        return text, False, needs_otp

    else:
        text = result.get(
            "response_text",
            "I'm sorry, I didn't understand that. Could you rephrase what you need?",
        )

    session.add_turn("assistant", text)
    await save_session(session)
    return text, False, False
