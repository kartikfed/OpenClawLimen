# OpenClaw Voice Orchestration Server

**Created:** 2026-02-07  
**Purpose:** Self-hosted voice agent that handles slow reasoning models (Claude Sonnet 4.5) over Twilio telephony

## The Problem

Managed voice platforms (ElevenLabs, Deepgram Voice Agent API) cannot handle slow reasoning models because they treat the LLM as a black box. When Claude Sonnet 4.5 takes 10-15 seconds to think through a complex query with tool calls, the Twilio WebSocket times out (~10s RTP silence) and kills the connection.

## The Solution

We control the orchestration server and inject "filler audio" immediately after the user stops speaking. While the filler plays ("Let me check that..."), Sonnet can think for as long as needed without Twilio timing out.

## Architecture

```
Twilio Phone Call
    ↓ (WebSocket)
Voice Orchestration Server (Python/FastAPI)
    ├─> Deepgram STT API (speech → text)
    ├─> Filler Audio Injection ("thinking...")
    ├─> OpenClaw API (Claude Sonnet 4.5 + tools)
    └─> Deepgram TTS API (text → speech)
```

## Features

- **Caller ID Recognition:** Greet callers by name based on phone number
- **Filler Audio:** Keep Twilio alive during long LLM thinking
- **Tool Calling:** Full OpenClaw tool support (calendar, email, kitchen, etc.)
- **Configurable:** Easy to add new callers, change greetings, adjust filler audio

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in credentials
3. Run: `python server/main.py`
4. Expose via ngrok: `ngrok http 8080`
5. Configure Twilio webhook to ngrok URL

## Configuration

- **Deepgram API Key:** STT + TTS (Nova-2 + Aura)
- **OpenClaw Endpoint:** http://localhost:18789/v1/chat/completions
- **Twilio Credentials:** For phone number management
- **Caller Database:** JSON file mapping phone numbers to names

## Development Timeline

**Estimated:** 16-23 hours  
**Started:** 2026-02-07 19:17 EST

## Credits

Architecture inspired by Gemini's analysis of Twilio RTP timeout issues with reasoning models.
