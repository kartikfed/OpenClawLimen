# Telegram Voice App - ElevenLabs Integration

**Created:** 2026-02-07  
**Status:** In Progress  
**Purpose:** Full conversational AI accessible via Telegram Mini App

## Architecture

**Stack:**
- Telegram Mini App (Web App)
- ElevenLabs Conversational AI
- Identity context (SOUL.md, IDENTITY.md, USER.md)
- Tool integration (kitchen, calendar, etc.)

**Access Method:**
- Menu button in Telegram chat
- Single tap → voice interface opens
- Real-time conversation (not voice messages)

## Implementation Progress

### ✅ Completed
1. Web interface created (`index.html`)
2. Web server running (port 8081)
3. ngrok tunnel established
4. Basic UI with microphone button

### 🚧 In Progress
1. Set up Telegram menu button (need bot token)
2. Integrate ElevenLabs SDK
3. Load identity context
4. Configure tools

### 📋 TODO
1. ElevenLabs agent configuration
2. Tool definitions (kitchen, calendar)
3. Authentication/session management
4. Error handling
5. Audio permissions handling

## URLs

- **Web App:** https://limen-voice-app.ngrok.app (stable)
- **OpenClaw API:** https://limen-openclaw.ngrok.app (stable)
- **Local web:** http://localhost:8081
- **Local OpenClaw:** http://localhost:18789

## Advantages Over Twilio

1. **No telephony constraints** - No RTP timeout
2. **Natural conversation flow** - ElevenLabs handles barge-in
3. **Better UX** - More accessible than phone number
4. **Tool support** - Can use slow reasoning models
5. **Identity integration** - Full Limen personality

## Setup Instructions

### Configure Menu Button

Run this command with your bot token:

```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setChatMenuButton" \
  -H "Content-Type: application/json" \
  -d '{
    "menu_button": {
      "type": "web_app",
      "text": "🎙️ Talk",
      "web_app": {
        "url": "https://karole-legislatorial-raveningly.ngrok-free.dev"
      }
    }
  }'
```

### Start Servers

```bash
# Web server
cd ~/.openclaw/workspace/projects/telegram-voice-app
python3 -m http.server 8081

# ngrok
ngrok http 8081
```

## Files

- `index.html` - Web interface
- `README.md` - This file
- (future) `config.js` - ElevenLabs configuration
- (future) `tools.js` - Tool definitions

## Notes

- Keep existing Twilio code until this is validated
- Test on iOS Telegram app
- Compare conversation quality with Twilio version
- Clean up unused code after validation
