from twilio.twiml.voice_response import VoiceResponse, Gather, Play


def incoming_call_twiml(greeting_url: str, gather_action: str) -> str:
    """Plays greeting audio and gathers the caller's spoken name."""
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=gather_action,
        speech_timeout="3",
        timeout=10,
        language="en-US",
    )
    gather.play(greeting_url)
    response.append(gather)
    response.redirect(gather_action + "?timeout=1")
    return str(response)


def ask_pin_twiml(prompt_url: str, gather_action: str, num_digits: int = 6) -> str:
    """Plays prompt audio and gathers DTMF PIN digits."""
    response = VoiceResponse()
    gather = Gather(
        input="dtmf",
        action=gather_action,
        num_digits=num_digits,
        timeout=15,
        finish_on_key="",
    )
    gather.play(prompt_url)
    response.append(gather)
    return str(response)


def ask_intent_twiml(prompt_url: str, gather_action: str) -> str:
    """Plays a prompt and gathers the caller's spoken intent."""
    response = VoiceResponse()
    gather = Gather(
        input="speech",
        action=gather_action,
        speech_timeout="2",
        timeout=8,
        language="en-US",
    )
    gather.play(prompt_url)
    response.append(gather)
    response.redirect(gather_action + "?timeout=1")
    return str(response)


def play_and_gather_twiml(audio_url: str, gather_action: str) -> str:
    """General: play a response then immediately listen for the next utterance."""
    return ask_intent_twiml(audio_url, gather_action)


def transfer_to_agent_twiml(audio_url: str, agent_number: str) -> str:
    """Plays hold message then dials the agent number."""
    response = VoiceResponse()
    response.play(audio_url)
    response.dial(agent_number)
    return str(response)


def say_and_hang_up_twiml(audio_url: str) -> str:
    """Plays farewell audio then ends the call."""
    response = VoiceResponse()
    response.play(audio_url)
    response.hangup()
    return str(response)


def error_twiml(message: str = "Something went wrong. Please call back.") -> str:
    response = VoiceResponse()
    response.say(message, voice="alice")
    response.hangup()
    return str(response)
