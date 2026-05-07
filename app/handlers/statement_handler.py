from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.call_session import CallSession
from app.models.user import User
from app.services.bank_api import bank_api
from app.services.statement_service import generate_statement_pdf
from app.services.email_service import send_statement_email
import asyncio


async def handle_statement_request(session: CallSession, db: AsyncSession) -> str:
    user = await db.get(User, session.user_id)
    if not user or not user.email:
        return (
            "I don't have an email address on file for your account. "
            "Please visit a branch to update your contact details. Anything else?"
        )

    now = datetime.now()
    month_label = now.strftime("%B %Y")
    transactions = await bank_api.get_statement_transactions(session.user_id, now.month, now.year)

    loop = asyncio.get_event_loop()
    pdf_bytes = await loop.run_in_executor(
        None,
        generate_statement_pdf,
        user.full_name,
        session.account_number,
        session.bank_name,
        transactions,
        month_label,
    )

    success, masked_email = await send_statement_email(
        user.email, user.full_name, pdf_bytes, month_label
    )

    if success:
        return (
            f"I've emailed your {month_label} statement to {masked_email}. "
            f"You should receive it within a few minutes. Anything else?"
        )
    return (
        "I wasn't able to send the statement right now. "
        "Please try again later or visit a branch. Anything else I can help with?"
    )
