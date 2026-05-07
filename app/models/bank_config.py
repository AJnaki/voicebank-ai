from pathlib import Path
from typing import Optional
import yaml
from pydantic import BaseModel


class BankFeatures(BaseModel):
    fund_transfer: bool = True
    bill_payment: bool = True
    loan_enquiry: bool = True
    card_block: bool = True
    outbound_calls: bool = True
    sentiment_escalation: bool = True
    multi_language: bool = False
    post_call_sms: bool = True
    compliance_recording: bool = False


class BankConfig(BaseModel):
    bank_id: str
    display_name: str
    phone_number: str
    voice_id: str
    greeting: str
    language_default: str = "en"
    languages_enabled: list[str] = ["en"]
    pin_length: int = 6
    biometric_threshold: int = 70
    agent_transfer_number: str = "+10000000000"
    voice_ids: dict[str, str] = {}
    features: BankFeatures = BankFeatures()

    def voice_for_language(self, lang: str) -> str:
        return self.voice_ids.get(lang, self.voice_id)


def load_bank_config(path: str) -> BankConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    features = BankFeatures(**data.pop("features", {}))
    voice_ids = data.pop("voice_ids", {})
    return BankConfig(**data, features=features, voice_ids=voice_ids)


_cached: Optional[BankConfig] = None


def get_bank_config() -> BankConfig:
    global _cached
    if _cached is None:
        config_path = Path(__file__).parent.parent / "bank_config" / "first_national.yml"
        _cached = load_bank_config(str(config_path))
    return _cached
