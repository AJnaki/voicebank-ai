SUPPORTED_LANGUAGES: dict[str, dict] = {
    "en": {"name": "English", "twilio_code": "en-US", "greeting_suffix": ""},
    "es": {"name": "Spanish", "twilio_code": "es-MX", "greeting_suffix": " Para español, diga 'español'."},
    "fr": {"name": "French", "twilio_code": "fr-FR", "greeting_suffix": ""},
    "ar": {"name": "Arabic", "twilio_code": "ar-SA", "greeting_suffix": ""},
    "hi": {"name": "Hindi", "twilio_code": "hi-IN", "greeting_suffix": ""},
    "bn": {"name": "Bengali", "twilio_code": "bn-BD", "greeting_suffix": ""},
}

LANGUAGE_PROMPTS: dict[str, str] = {
    "es": "Responde siempre en español. Sé breve y natural como si hablaras por teléfono.",
    "fr": "Réponds toujours en français. Sois bref et naturel comme au téléphone.",
    "ar": "أجب دائمًا باللغة العربية. كن موجزًا وطبيعيًا كأنك تتحدث عبر الهاتف.",
    "hi": "हमेशा हिंदी में जवाब दें। संक्षिप्त और स्वाभाविक रहें जैसे फोन पर बात कर रहे हों।",
    "bn": "সবসময় বাংলায় উত্তর দিন। সংক্ষিপ্ত এবং স্বাভাবিক থাকুন যেন ফোনে কথা বলছেন।",
}


def get_twilio_language_code(lang: str) -> str:
    return SUPPORTED_LANGUAGES.get(lang, SUPPORTED_LANGUAGES["en"])["twilio_code"]


def get_language_instruction(lang: str) -> str:
    return LANGUAGE_PROMPTS.get(lang, "")


def detect_language_from_speech(speech_result: str, languages_enabled: list[str]) -> str:
    """
    Lightweight language detection from transcribed text.
    Returns ISO language code. Falls back to 'en'.
    In production, Deepgram streaming returns the detected language code directly.
    """
    spanish_words = {"hola", "por favor", "gracias", "ayuda", "saldo", "mi"}
    french_words = {"bonjour", "aide", "solde", "merci", "mon", "compte"}
    hindi_words = {"नमस्ते", "मेरा", "बैलेंस", "मदद", "कृपया"}

    text_lower = speech_result.lower()
    tokens = set(text_lower.split())

    if "es" in languages_enabled and tokens & spanish_words:
        return "es"
    if "fr" in languages_enabled and tokens & french_words:
        return "fr"
    if "hi" in languages_enabled and any(w in speech_result for w in hindi_words):
        return "hi"

    return "en"
