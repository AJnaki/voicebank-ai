# Call Flow

## Inbound Call — Full Journey

```mermaid
flowchart TD
    A[📞 Customer Calls Bank Number] --> B[Twilio Receives Call]
    B --> C["🎙️ Greeting: Welcome to First National Bank.\nPlease say your first and last name."]
    C --> D[Deepgram transcribes name in real-time]
    D --> E{Name found\nin system?}
    E -- No --> F["Sorry, I couldn't find that name.\nPlease try again or press 0 for help."]
    F --> C
    E -- Yes --> G["Thank you, John. Please enter\nyour 6-digit PIN on the keypad."]
    G --> H[Twilio DTMF collects PIN]
    H --> I{PIN correct?}
    I -- No, 1st/2nd attempt --> J["Incorrect PIN. Please try again."]
    J --> G
    I -- No, 3rd attempt --> K[🔒 Account locked — transfer to agent]
    I -- Yes --> L[Azure: Run voice biometric check in background]
    L --> M{Voice match\nconfident?}
    M -- Low confidence --> N[Flag call for review — continue session]
    M -- High confidence --> O[✅ Fully authenticated]
    N --> O
    O --> P["Welcome back, John! How can I help you today?\nYou can ask about your balance, recent\ntransactions, statements, payments, or anything else."]
    P --> Q[Deepgram streams caller speech]
    Q --> R[AI Engine classifies intent]
    R --> S{Intent}
    S --> T[💰 Balance Check]
    S --> U[📋 Transactions]
    S --> V[📄 Statement]
    S --> W[💳 Card Block]
    S --> X[🏦 Loan Status]
    S --> Y[💸 Bill Payment]
    S --> Z[👤 Talk to Agent]
    S --> AA[🚨 Fraud Report]
    T & U & V & W & X & Y & AA --> BB[Fetch from Bank API]
    BB --> CC[ElevenLabs speaks response]
    CC --> DD{Anything\nelse?}
    DD -- Yes --> Q
    DD -- No --> EE[Goodbye + call ends]
    Z --> FF[Transfer to live agent\nwith full transcript summary]
```

## Authentication Detail

```mermaid
sequenceDiagram
    participant C as Caller
    participant T as Twilio
    participant B as Backend
    participant DB as PostgreSQL
    participant AZ as Azure Speaker ID

    C->>T: Dials bank number
    T->>B: Webhook: new call
    B->>T: Play greeting TTS
    T->>C: "Welcome to First National Bank. Please say your full name."
    C->>T: Speaks name
    T->>B: Audio stream
    B->>B: Deepgram transcribes → "John Smith"
    B->>DB: Lookup "John Smith"
    DB->>B: Found — user_id: 1042
    B->>T: Play "Thank you John, please enter your PIN"
    C->>T: Enters PIN via keypad
    T->>B: DTMF digits
    B->>DB: Verify PIN hash
    DB->>B: PIN valid ✓
    B->>AZ: Submit call audio for voice verification
    AZ->>B: Confidence score: 94% ✓
    B->>B: Session marked: fully_authenticated
    B->>T: Play personalized welcome
    T->>C: "Welcome back John! How can I help you today?"
```

## Intent Routing Keywords

| Intent | Example Phrases |
|---|---|
| Balance Check | "balance", "how much do I have", "account balance", "funds available" |
| Transactions | "transactions", "recent activity", "what did I spend", "last payments" |
| Statement | "statement", "monthly statement", "PDF", "email my statement" |
| Bill Payment | "pay bill", "pay electricity", "schedule payment", "make a payment" |
| Card Block | "block my card", "lost card", "stolen card", "freeze card", "card missing" |
| Loan Status | "loan", "EMI", "how much is left", "loan balance", "repayment" |
| Fraud Report | "unauthorized", "fraud", "I didn't make this", "dispute", "suspicious" |
| Live Agent | "agent", "human", "talk to someone", "real person", "representative" |
