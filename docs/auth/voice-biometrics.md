# Voice Biometrics

## What Is Voice Biometrics?

Voice biometrics analyzes the unique physical and behavioral characteristics of a person's voice — vocal tract shape, pitch, cadence, accent — to verify identity. Like a fingerprint, no two people's voices are identical.

## Why Add It?

- PIN alone can be stolen or shared
- Voice print cannot be transferred
- It runs **passively during the call** — zero extra friction
- Builds a fraud risk score on every call
- Meets emerging financial compliance requirements (especially in EU)

## Azure Speaker Recognition

We use **Azure Cognitive Services — Speaker Recognition** (Verification mode).

### Enrollment

```python
# POST /speaker/verification/profile
{
    "locale": "en-US"
}
# Returns: profileId (linked to user in our DB)

# POST /speaker/verification/profile/{profileId}/enrollments
# Body: raw WAV audio (10+ seconds of speech)
# Returns: enrollment status, speech duration captured
```

### Verification (every call)

```python
# POST /speaker/verification/profile/{profileId}/verify
# Body: raw WAV audio (minimum 1 second)
# Returns:
{
    "result": "Accept",          # or "Reject"
    "score": 0.91,               # 0.0 - 1.0
    "recognitionModel": "recognitionModel005"
}
```

## Security Considerations

| Risk | Mitigation |
|---|---|
| Recorded voice replay attack | Azure uses liveness detection + challenge phrases |
| Voice print data breach | Stored at Azure, never in our DB (only profileId) |
| False rejection (legitimate caller) | Score threshold is lenient — flags, doesn't block |
| False acceptance (impersonator) | Still requires PIN — biometric is layer 3, not standalone |

## Compliance

- Voice prints stored within Azure's regional data centres (can specify EU or US)
- Deletion available: `DELETE /speaker/verification/profile/{profileId}`
- Caller consent obtained during enrollment (recorded)
- Data retention policy configurable per bank
