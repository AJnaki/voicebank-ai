from twilio.twiml.voice_response import VoiceResponse, Gather


def _play_or_say(container, url: str) -> None:
    """Use <Play> for real audio URLs, <Say> for 'say:' prefixed fallback."""
    if url.startswith("say:"):
        container.say(url[4:], voice="alice")
    else:
        container.play(url)


def incoming_call_twiml(greeting_url: str, gather_action: str) -> str:
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=gather_action,
        speech_timeout="3",
        timeout=10,
        language="en-US",
    )
    _play_or_say(gather, greeting_url)
    response.append(gather)
    response.redirect(gather_action + "?timeout=1")
    return str(response)


def ask_pin_twiml(prompt_url: str, gather_action: str, num_digits: int = 6) -> str:
    response = VoiceResponse()
    gather = Gather(
        input="dtmf",
        action=gather_action,
        num_digits=num_digits,
        timeout=15,
        finish_on_key="",
    )
    _play_or_say(gather, prompt_url)
    response.append(gather)
    return str(response)


def ask_intent_twiml(prompt_url: str, gather_action: str) -> str:
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=gather_action,
        speech_timeout="2",
        timeout=8,
        language="en-US",
    )
    _play_or_say(gather, prompt_url)
    response.append(gather)
    response.redirect(gather_action + "?timeout=1")
    return str(response)


def play_and_gather_twiml(audio_url: str, gather_action: str) -> str:
    return ask_intent_twiml(audio_url, gather_action)


def transfer_to_agent_twiml(audio_url: str, agent_number: str) -> str:
    response = VoiceResponse()
    _play_or_say(response, audio_url)
    response.dial(agent_number)
    return str(response)


def say_and_hang_up_twiml(audio_url: str) -> str:
    response = VoiceResponse()
    _play_or_say(response, audio_url)
    response.hangup()
    return str(response)


def error_twiml(message: str = "Something went wrong. Please call back.") -> str:
    response = VoiceResponse()
    response.say(message, voice="alice")
    response.hangup()
    return str(response)
