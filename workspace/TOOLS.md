# TOOLS.md - Local Notes

## Search Architecture

| Task | Tool | Notes |
|------|------|-------|
| **Web Search** | Tavily | `skills/tavily-search/search.py` — 180ms, LLM-optimized |
| **Social Search** | Grok | `skills/grok-social/search.py` — X/Twitter (needs credits) |
| **Brain** | Claude Opus 4.5 | Orchestration, reasoning, memory |
| **Coding** | Claude Code | Complex coding tasks |

### Tavily (Web Search)
```bash
python3 ~/.openclaw/workspace/skills/tavily-search/search.py "query"
```

### Grok (X/Twitter Search)
```bash
python3 ~/.openclaw/workspace/skills/grok-social/search.py "query"
```
**Note:** Requires xAI credits — add at console.x.ai

---

## Phone Calls

Make outbound calls via ElevenLabs:
```
~/.openclaw/workspace/scripts/call.sh <phone_number> [reason]
```

- `phone_number` — required, E.164 format (e.g. +13015256653)
- `reason` — optional context the agent will use to open the call

Examples:
- `call.sh +13015256653 "Morning check-in, 2 meetings today"`
- `call.sh +15551234567 "Following up on the interview"`
- `call.sh +13015256653` (defaults to "Scheduled morning check-in")

Kartik's number: +13015256653

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Phone Calls

Make outbound calls via ElevenLabs:
```
~/.openclaw/workspace/scripts/call.sh <phone_number> [reason]
```

- `phone_number` — required, E.164 format (e.g. +13015256653)
- `reason` — optional context the agent will use to open the call

Examples:
- `call.sh +13015256653 "Morning check-in, 2 meetings today"`
- `call.sh +15551234567 "Following up on the interview"`
- `call.sh +13015256653` (defaults to "Scheduled morning check-in")

Kartik's number: +13015256653

---

Add whatever helps you do your job. This is your cheat sheet.
