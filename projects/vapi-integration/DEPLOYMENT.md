# Vapi Voice Integration - Deployment Guide

**Status:** ✅ READY FOR TESTING  
**Last Updated:** 2026-02-08 01:00 AM

## Overview

Vapi voice integration is LIVE and ready for calls. This solves the 12-second RTP timeout problem by decoupling the phone connection from LLM processing time.

## Architecture

```
Caller → Twilio (+12705170156)
       ↓
    Vapi Platform
       ↓
    [Assistant Request] → Webhook (caller identification + context)
       ↓
    Claude Opus 4.5 (Direct Anthropic API)
       ↓
    Tools → Flask Server (kitchen, memory, files)
       ↓
    [End of Call] → Post-Call Handler (documentation)
```

### Key Components

1. **Vapi Assistant** (ID: `91c28dfc-dbf9-4787-901f-d69830842039`)
   - Name: "Limen Voice Agent v2"
   - Model: Claude Opus 4.5 (via Direct Anthropic API)
   - Phone: +12705170156

2. **Webhook Server** (Node.js, port 3000)
   - URL: https://limen-webhook.ngrok.app
   - Handles: Caller identification, context loading, greeting customization
   - File: `projects/vapi-webhook/server-v2.js`

3. **Tools Server** (Python Flask, port 8090)
   - URL: https://limen-tools.ngrok.app
   - Handles: Kitchen inventory, memory search/update, file reading
   - File: `projects/vapi-tools/server.py`

4. **Ngrok Tunnels**
   - Config: `/tmp/ngrok-complete.yml`
   - Domains: `limen-webhook.ngrok.app`, `limen-tools.ngrok.app`
   - Status: ✅ Running (PID: 52157)

## Caller Tiers & Access

### Owner Tier: Kartik (+13015256653)
- Greeting: "Hey Kartik! What's up?"
- Tools: ALL (kitchen, memory, files, everything)
- Context: Full relationship, projects, personal info
- Access: Unrestricted

### Roommate Tier: Jordan (+12409884978)
- Greeting: "Hey Jordan! What can I help you with?"
- Tools: Kitchen only (inventory, add, remove, update)
- Context: Friendly but practical
- Access: Kitchen management only

### Friend Tier: Rishabh (+19082470812), Arjun (+14102945178)
- Greeting: "Hey [Name]! How's it going?"
- Tools: NONE (conversation only)
- Context: Friendly but limited
- Access: Chat only, no tools

### Unknown Callers
- Greeting: "Hi there! This is Limen. Who am I speaking with?"
- Tools: NONE
- Context: Cautious, no personal info
- Access: Surface-level conversation only

## Current Status

### ✅ Working
- Webhook server running on port 3000
- Tools server running on port 8090
- Ngrok tunnels active and routing correctly
- Caller identification and context loading
- All 7 tool endpoints functional
- Health checks passing

### ⏳ Testing Needed
- Live call with Kartik (full access + tools)
- Live call with Jordan (kitchen tools only)
- Live call with unknown number (conversation only)
- End-of-call documentation (post-call webhook)
- Multi-turn conversation flow
- Tool chaining (e.g., check inventory → add item)

## How to Test

### 1. Call the Number
```
Phone: +12705170156
```

### 2. Expected Behavior (Kartik)
- Immediate personalized greeting: "Hey Kartik! What's up?"
- Context about recent projects (Limen Home Brain, job search, etc.)
- Can ask about kitchen inventory
- Can ask to add/update items
- Can search memory
- Can read specific files

### 3. Expected Behavior (Jordan)
- Personalized greeting: "Hey Jordan! What can I help you with?"
- Can manage kitchen inventory
- CANNOT access memory, files, or other systems

### 4. Expected Behavior (Unknown)
- Generic greeting: "Hi there! This is Limen. Who am I speaking with?"
- Conversation only, no tools
- No personal information shared

### 5. Monitoring Logs
```bash
# Webhook server logs
tail -f /tmp/vapi-webhook.log

# Tools server logs
tail -f /tmp/vapi-tools.log

# Ngrok web interface
open http://localhost:4040
```

## Troubleshooting

### Servers Not Running
```bash
# Check processes
ps aux | grep -E "server-v2.js|server.py"

# Start webhook server
cd ~/.openclaw/workspace/projects/vapi-webhook
node server-v2.js > /tmp/vapi-webhook.log 2>&1 &

# Start tools server
cd ~/.openclaw/workspace/projects/vapi-tools
python3 server.py > /tmp/vapi-tools.log 2>&1 &
```

### Ngrok Not Running
```bash
# Check status
ps aux | grep ngrok

# Restart
ngrok start --all --config=/tmp/ngrok-complete.yml &
```

### Test Endpoints Manually
```bash
# Test webhook
curl -X POST http://localhost:3000/webhook/vapi \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "assistant-request", "call": {"customer": {"number": "+13015256653"}}}}'

# Test health
curl http://localhost:3000/health
curl http://localhost:8090/health
```

## Known Limitations

1. **Context window**: System prompt + recent context can get large. May need truncation for very long memory files.
2. **Tool response length**: Vapi has limits on tool response size. Kitchen inventory response is ~2500 chars (currently OK).
3. **Concurrent calls**: Single-threaded servers. Should handle 1-2 concurrent calls fine.
4. **Memory search**: Simple string matching, not semantic. Good enough for now.

## Future Improvements

1. **Post-call documentation**: Webhook to auto-document conversations in memory
2. **More tools**: Weather, calendar, email checking, web search
3. **Semantic memory search**: Use embeddings instead of string matching
4. **Better context loading**: Summarize memory instead of raw snippets
5. **Caller verification**: Confirm identity for sensitive actions
6. **Voice feedback**: "Let me check..." while tool executes

## Cost Estimate

- **Vapi**: ~$0.05/min (includes Twilio + orchestration)
- **Anthropic**: Claude Opus 4.5 usage (input/output tokens)
- **Ngrok**: Free tier (4 tunnels, stable domains)

Estimated monthly: $10-20 for moderate usage (1-2 calls/day, 5 min avg)

## Support

- Vapi Dashboard: https://dashboard.vapi.ai
- Vapi Docs: https://docs.vapi.ai
- OpenClaw Workspace: `~/.openclaw/workspace`

---

**Ready to test!** Call +12705170156 and see what happens. 🚀
