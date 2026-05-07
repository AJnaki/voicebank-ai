from app.services.adapters.base import BankAPIAdapter
from app.services.adapters.mock_adapter import MockBankAdapter


def get_bank_adapter() -> BankAPIAdapter:
    """
    Returns the configured bank API adapter.
    Swap MockBankAdapter for a real adapter (e.g. FirstNationalAdapter)
    when connecting to a live core banking system.
    """
    return MockBankAdapter()
