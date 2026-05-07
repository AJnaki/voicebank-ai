from app.models.call_session import CallSession
from app.services.bank_api import bank_api


async def get_fd_response(session: CallSession) -> str:
    fd = await bank_api.get_fixed_deposit(session.user_id)
    return (
        f"Your fixed deposit of {fd.principal:,.0f} {fd.currency} earns interest at "
        f"{fd.interest_rate} percent per annum. "
        f"It matures on {fd.maturity_date} with a maturity amount of "
        f"{fd.maturity_amount:,.2f} {fd.currency}. Anything else?"
    )
