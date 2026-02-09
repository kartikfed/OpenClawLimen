# Testing Guide

## Quick Start

### 1. Start the Server

```bash
cd ~/.openclaw/workspace/projects/voice-orchestrator
./start.sh
```

Server will start on http://localhost:8080

**Prerequisites checked by script:**
- ✅ .env file exists
- ✅ OpenClaw gateway running

## Expose via ngrok

In a separate terminal:

```bash
ngrok http 8080
```

You'll get a public URL like: `https://abc123.ngrok.io`

## Configure Twilio

1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number: `+12705170156`
3. Under "Voice Configuration" → "A CALL COMES IN":
   - Set to: **Webhook**
   - URL: `https://abc123.ngrok.io/twilio/inbound`
   - Method: **HTTP POST**
4. Save

## Test Call Flow

1. Call your Twilio number: `+12705170156`
2. You should hear: "Hey [name], what's up?"
3. Say something: "What's in the kitchen?"
4. Agent says: "Let me check that for you..."
5. (Sonnet thinks for 10-15 seconds)
6. Agent responds with actual answer

## Debugging

### Check server logs:
```bash
# Server output shows:
# - Inbound call received
# - WebSocket connected
# - Transcription results
# - OpenClaw queries
# - TTS generation
```

### Check Twilio debugger:
https://console.twilio.com/us1/monitor/logs/debugger

### Common issues:

**"Application error" on call:**
- Check ngrok URL is correct in Twilio
- Check server is running
- Check server logs for errors

**No audio/silent call:**
- Check Deepgram API key
- Check audio format conversion (μ-law)
- Check WebSocket connection

**Call drops after greeting:**
- This was the original problem!
- Should NOT happen with filler audio
- Check OpenClaw query timing

## What Success Looks Like

- ✅ Call connects
- ✅ Greeting plays immediately
- ✅ You can ask complex questions
- ✅ Filler audio plays while thinking
- ✅ Real answer comes through
- ✅ Call stays connected for long queries
- ✅ Multi-turn conversation works

## Next Steps

Once basic flow works:
1. Better filler audio (variety of phrases)
2. Audio format optimization
3. Error handling improvements
4. Outbound call support
5. Call logging/analytics
