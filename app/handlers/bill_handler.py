from app.models.call_session import CallSession
from app.services.bank_api import bank_api
from app.services.otp_service import generate_otp
from app.services.sms_service import send_otp_sms
from app.db.redis_client import save_session
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


async def initiate_bill_payment(
    session: CallSession,
    biller: str,
    amount: float,
    db: AsyncSession,
) -> tuple[str, bool]:
    """Returns (response_text, requires_otp)."""
    user = await db.get(User, session.user_id)
    otp = await generate_otp(session.call_sid)
    await send_otp_sms(user.phone_number, otp, session.bank_name)
    session.set_pending("bill_payment", biller=biller, amount=amount)
    await save_session(session)
    return (
        f"I've sent a verification code to your mobile. "
        f"Please enter it on your keypad to confirm paying {amount:.0f} dollars to {biller}."
    ), True


async def complete_bill_payment(session: CallSession) -> str:
    biller = session.pending_data.get("biller", "the biller")
    amount = session.pending_data.get("amount", 0)
    result = await bank_api.pay_bill(session.user_id, biller, amount)
    session.clear_pending()
    await save_session(session)
    if result.success:
        return (
            f"Payment of {amount:.0f} dollars to {biller} was successful. "
            f"Reference: {result.reference}. Anything else?"
        )
    return "The payment could not be processed. Please try again later."
