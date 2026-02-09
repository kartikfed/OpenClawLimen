# Vapi Voice - Quick Start

## TL;DR

**Call this number:** +12705170156

It will greet you by name (if known) and you can:
- Chat naturally
- Ask about kitchen inventory
- Tell it to add/update items
- Search your memory
- Read specific files (if you're Kartik)

## Status Check

```bash
# Are servers running?
ps aux | grep -E "server-v2.js|server.py" | grep -v grep

# Are tunnels up?
curl http://localhost:4040/api/tunnels

# Health checks
curl http://localhost:3000/health
curl http://localhost:8090/health
```

## Restart Everything

```bash
# Kill old processes (if needed)
pkill -f "server-v2.js"
pkill -f "vapi.*server.py"

# Start webhook
cd ~/.openclaw/workspace/projects/vapi-webhook
node server-v2.js > /tmp/vapi-webhook.log 2>&1 &

# Start tools (if port 8090 free)
cd ~/.openclaw/workspace/projects/vapi-tools
python3 server.py > /tmp/vapi-tools.log 2>&1 &

# Check logs
tail -f /tmp/vapi-webhook.log
tail -f /tmp/vapi-tools.log
```

## Test Without Calling

```bash
# Simulate Kartik calling
curl -X POST http://localhost:3000/webhook/vapi \
  -H "Content-Type: application/json" \
  -d '{"message": {"type": "assistant-request", "call": {"customer": {"number": "+13015256653"}}}}' | jq .

# Test kitchen inventory
curl -X POST http://localhost:8090/tools/kitchen-inventory \
  -H "Content-Type: application/json" \
  -d '{"message": {"toolCallList": [{"id": "test", "function": {"name": "get_kitchen_inventory", "arguments": {"location": "all"}}}]}}' | jq .
```

## Phone Number

**Main:** +12705170156

## Known Callers

- **Kartik** (+13015256653) → Full access
- **Jordan** (+12409884978) → Kitchen only
- **Rishabh** (+19082470812) → Chat only
- **Arjun** (+14102945178) → Chat only

## Files

- **Webhook**: `projects/vapi-webhook/server-v2.js`
- **Tools**: `projects/vapi-tools/server.py`
- **All Tools**: `projects/vapi-tools/ALL_TOOLS_VAPI.json`
- **Deployment**: `projects/vapi-integration/DEPLOYMENT.md`

## Monitoring

- Ngrok web UI: http://localhost:4040
- Vapi dashboard: https://dashboard.vapi.ai
- Webhook logs: `/tmp/vapi-webhook.log`
- Tools logs: `/tmp/vapi-tools.log`

---

**Just call it.** That's the whole point. 📞
