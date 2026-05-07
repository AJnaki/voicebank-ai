# Webhooks

## Twilio Webhook Flow

Twilio drives the call by making HTTP POST requests to our backend at each step. Every endpoint returns TwiML (XML) that tells Twilio what to do next.

```
Twilio Event              →   Our Endpoint                →   Returns
─────────────────────────────────────────────────────────────────────
New inbound call          →   POST /webhook/call/incoming  →   TwiML: play greeting, gather speech
Caller spoke (name)       →   POST /webhook/call/auth/name →   TwiML: play PIN prompt, gather DTMF
Caller entered PIN        →   POST /webhook/call/auth/pin  →   TwiML: play welcome, gather intent
Caller spoke (intent)     →   POST /webhook/call/intent    →   TwiML: play response, gather next
Call ended/status change  →   POST /webhook/call/status    →   Log call, clean Redis session
```

## Webhook Security

All Twilio webhooks are signed. We validate every request:

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(TWILIO_AUTH_TOKEN)

async def twilio_webhook(request: Request):
    signature = request.headers.get("X-Twilio-Signature", "")
    body = await request.body()
    params = await request.form()
    
    valid = validator.validate(
        str(request.url),
        dict(params),
        signature
    )
    if not valid:
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
```

## TwiML Response Examples

### Greeting (incoming call)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Play>https://s3.amazonaws.com/voicebank/greetings/first-national-welcome.mp3</Play>
  <Gather input="speech" action="/webhook/call/auth/name" speechTimeout="3" language="en-US">
    <Say voice="Polly.Joanna">Please say your first and last name.</Say>
  </Gather>
</Response>
```

### PIN Collection (DTMF)
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Gather action="/webhook/call/auth/pin" numDigits="6" timeout="10">
    <Say voice="Polly.Joanna">Thank you, John. Please enter your 6-digit PIN using your keypad.</Say>
  </Gather>
</Response>
```

### Agent Transfer with Context
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Connecting you to a team member now. Please hold.</Say>
  <Dial>
    <Conference waitUrl="https://api.voicebank.ai/hold-music"
                statusCallback="https://api.voicebank.ai/webhook/conference/status">
      agent-room-CA1234567890
    </Conference>
  </Dial>
</Response>
```
