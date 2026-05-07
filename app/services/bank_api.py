from app.services.adapters.factory import get_bank_adapter

# Single shared adapter instance used by all handlers.
# To switch to a real bank API, update factory.py.
bank_api = get_bank_adapter()
