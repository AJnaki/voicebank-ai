import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.sentiment_service import detect_sentiment, should_offer_agent, ESCALATION_OFFER
from app.services.language_service import (
    detect_language_from_speech, get_twilio_language_code, SUPPORTED_LANGUAGES,
)
from app.models.call_session import CallSession


# ── Sentiment Detection ──────────────────────────────────────────────────────

def test_detect_sentiment_angry():
    assert detect_sentiment("This is ridiculous I am so angry") == "angry"

def test_detect_sentiment_frustrated():
    assert detect_sentiment("ugh this is so frustrating I hate waiting") == "frustrated"

def test_detect_sentiment_satisfied():
    assert detect_sentiment("thank you so much that was perfect") == "satisfied"

def test_detect_sentiment_confused():
    assert detect_sentiment("I don't understand what you mean") == "confused"

def test_detect_sentiment_neutral():
    assert detect_sentiment("check my balance") == "neutral"

def test_detect_sentiment_empty():
    assert detect_sentiment("") == "neutral"

def test_detect_sentiment_none():
    assert detect_sentiment(None) == "neutral"


# ── should_offer_agent ───────────────────────────────────────────────────────

def test_should_offer_agent_after_two_negative():
    log = ["satisfied", "angry", "frustrated"]
    assert should_offer_agent(log) is True

def test_should_offer_agent_not_triggered_single_negative():
    log = ["angry"]
    assert should_offer_agent(log) is False

def test_should_offer_agent_not_triggered_positive():
    log = ["satisfied", "neutral"]
    assert should_offer_agent(log) is False

def test_should_offer_agent_empty_log():
    assert should_offer_agent([]) is False

def test_escalation_offer_is_string():
    assert isinstance(ESCALATION_OFFER, str)
    assert len(ESCALATION_OFFER) > 10


# ── Language Detection ───────────────────────────────────────────────────────

def test_detect_language_english():
    lang = detect_language_from_speech("check my balance please", ["en", "es", "fr"])
    assert lang == "en"

def test_detect_language_spanish():
    lang = detect_language_from_speech("hola quiero ver mi saldo", ["en", "es", "fr"])
    assert lang == "es"

def test_detect_language_french():
    lang = detect_language_from_speech("bonjour je veux voir mon solde", ["en", "es", "fr"])
    assert lang == "fr"

def test_detect_language_fallback_empty():
    lang = detect_language_from_speech("", ["en", "es"])
    assert lang == "en"

def test_detect_language_disabled_lang_not_detected():
    # Spanish words present, but "es" not in enabled list → falls back to en
    lang = detect_language_from_speech("hola mi saldo", ["en", "fr"])
    assert lang == "en"

def test_supported_languages_contains_en():
    assert "en" in SUPPORTED_LANGUAGES

def test_supported_languages_contains_es():
    assert "es" in SUPPORTED_LANGUAGES

def test_get_twilio_language_code_en():
    assert get_twilio_language_code("en") == "en-US"

def test_get_twilio_language_code_es():
    assert get_twilio_language_code("es") == "es-MX"

def test_get_twilio_language_code_fr():
    assert get_twilio_language_code("fr") == "fr-FR"

def test_get_twilio_language_code_unknown_fallback():
    assert get_twilio_language_code("xx") == "en-US"


# ── CallSession Phase 3 Methods ──────────────────────────────────────────────

def test_session_log_sentiment():
    session = CallSession(call_sid="CA_s1", account_number="ACC001")
    session.log_sentiment("angry")
    session.log_sentiment("neutral")
    assert session.sentiment_log == ["angry", "neutral"]

def test_session_consecutive_negative_two():
    session = CallSession(call_sid="CA_s2", account_number="ACC001")
    session.log_sentiment("satisfied")
    session.log_sentiment("frustrated")
    session.log_sentiment("angry")
    assert session.consecutive_negative_sentiment() == 2

def test_session_consecutive_negative_broken_by_positive():
    session = CallSession(call_sid="CA_s3", account_number="ACC001")
    session.log_sentiment("angry")
    session.log_sentiment("satisfied")
    # trailing is satisfied → not negative
    assert session.consecutive_negative_sentiment() == 0

def test_session_consecutive_negative_empty():
    session = CallSession(call_sid="CA_s4", account_number="ACC001")
    assert session.consecutive_negative_sentiment() == 0

def test_session_escalated_flag_default_false():
    session = CallSession(call_sid="CA_s5", account_number="ACC001")
    assert session.escalated is False

def test_session_language_default():
    session = CallSession(call_sid="CA_s6", account_number="ACC001")
    assert session.language == "en"

def test_session_language_set():
    session = CallSession(call_sid="CA_s7", account_number="ACC001")
    session.language = "es"
    assert session.language == "es"


# ── Bank Config ──────────────────────────────────────────────────────────────

def test_bank_config_load_display_name():
    from app.models.bank_config import load_bank_config
    config = load_bank_config("bank_config/first_national.yml")
    assert config.display_name == "First National Bank"

def test_bank_config_features_sentiment_escalation():
    from app.models.bank_config import load_bank_config
    config = load_bank_config("bank_config/first_national.yml")
    assert config.features.sentiment_escalation is True

def test_bank_config_features_fund_transfer():
    from app.models.bank_config import load_bank_config
    config = load_bank_config("bank_config/first_national.yml")
    assert config.features.fund_transfer is True

def test_bank_config_languages():
    from app.models.bank_config import load_bank_config
    config = load_bank_config("bank_config/first_national.yml")
    assert "en" in config.languages_enabled

def test_bank_config_city_bank():
    from app.models.bank_config import load_bank_config
    config = load_bank_config("bank_config/city_bank.yml")
    assert config.display_name == "City Bank"
    assert "fr" in config.languages_enabled
