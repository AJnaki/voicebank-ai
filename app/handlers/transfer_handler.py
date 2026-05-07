from app.models.call_session import CallSession
from app.services.bank_api import bank_api
from app.services.otp_service import generate_otp
from app.services.sms_service import send_otp_sms
from app.db.redis_client import save_session
from app.config import get_settings
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

settings = get_settings()


async def initiate_transfer(
    session: CallSession,
    destination: str,
    amount: float,
    db: AsyncSession,
) -> tuple[str, bool]:
    """
    Returns (response_text, requires_otp).
    High-value transfers require OTP; low-value proceed directly.
    """
    if amount > settings.fund_transfer_otp_threshold:
        user = await db.get(User, session.user_id)
        otp = await generate_otp(session.call_sid)
        await send_otp_sms(user.phone_number, otp, session.bank_name)
        session.set_pending("fund_transfer", destination=destination, amount=amount)
        await save_session(session)
        return (
            f"For security, I've sent a six-digit code to your registered mobile number. "
            f"Please enter it on your keypad to confirm the transfer of "
            f"{amount:.0f} dollars to {destination}."
        ), True

    result = await bank_api.transfer_funds(session.user_id, destination, amount)
    if result.success:
        return (
            f"Done! {amount:.0f} dollars has been transferred to {destination}. "
            f"Your reference number is {result.reference}. Anything else?"
        ), False
    return "The transfer could not be completed. Please try again later.", False


async def complete_transfer(session: CallSession) -> str:
    destination = session.pending_data.get("destination", "your account")
    amount = session.pending_data.get("amount", 0)
    result = await bank_api.transfer_funds(session.user_id, destination, amount)
    session.clear_pending()
    await save_session(session)
    if result.success:
        return (
            f"Transfer complete. {amount:.0f} dollars sent to {destination}. "
            f"Reference: {result.reference}. Anything else?"
        )
    return "The transfer failed. Please try again or visit a branch."
