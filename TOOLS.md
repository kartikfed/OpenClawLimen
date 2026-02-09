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

## Phone Calls (VAPI)

### Outbound Calls

Make outbound calls with context-aware greetings:
```bash
~/.openclaw/workspace/scripts/call.sh <phone> <name> <reason> [context] [recipient_info]
```

**Arguments:**
- `phone` — Required. E.164 format (e.g., +13015256653)
- `name` — Required. Who you're calling
- `reason` — Required. Why you're calling (affects opening line)
- `context` — Optional. Relevant info (calendar, todos, etc.)
- `recipient_info` — Optional. Who they are (for non-Kartik calls)

**Examples:**
```bash
# Morning briefing
call.sh +13015256653 "Kartik" "Morning check-in" "2 meetings, urgent email from Anthropic"

# Urgent
call.sh +13015256653 "Kartik" "Urgent - recruiter deadline" "Jane Street response due 5pm"

# Follow-up with non-Kartik
call.sh +15854654046 "Shimon" "Following up" "" "Former Microsoft coworker, on sabbatical"

# Simple check-in
call.sh +13015256653 "Kartik" "Quick check-in"
```

**Auto-generated opening lines:**
- "morning" or "briefing" → "Hey [name], good morning! Got your day briefing ready."
- "urgent" or "important" → "Hey [name], something came up I need to tell you about."
- "follow" → "Hey [name], wanted to follow up on something."
- Default → "Hey [name], got a minute? Wanted to chat about something."

**Setup:** API key at `~/.openclaw/workspace/secrets/vapi-api-key.txt`

Kartik's number: +13015256653

---

### VAPI Post-Call Webhook (Memory Updates)

**✅ Auto-triggers memory updates after every call**

**How it works:**
1. Call ends (inbound or outbound)
2. VAPI sends end-of-call report to webhook
3. Webhook sends transcript + metadata to me via Telegram
4. I process it, update MEMORY.md, log in daily file

**Webhook URL:** https://vapi-webhook.krishnankartik70.workers.dev
**Code:** `~/.openclaw/workspace/vapi-webhook/worker.js`
**Deploy:** `cd ~/.openclaw/workspace/vapi-webhook && npx wrangler deploy`

**VAPI Dashboard Setup:**
1. Go to Assistant settings
2. Set "Server URL" to the webhook URL
3. Enable `end-of-call-report` events

**Known contacts** (in worker.js `KNOWN_CONTACTS`):
- +13015256653 (Kartik)
- +12409884978 (Jordan)
- +17326475138 (Rishik)
- +15854654046 (Shimon)
- +13015006661 (PV)
- +13013233653 (Sanjay)

**To add new contacts:** Edit `KNOWN_CONTACTS` in worker.js, redeploy.

**Testing:** `~/.openclaw/workspace/vapi-webhook/test-webhook.sh`

---

## Mission Control Updates

**Always use this to update status:**
```bash
~/.openclaw/workspace/scripts/update-mission-control.sh "mood" "activity" "thought" [type]
```

- `mood` — How I'm feeling (required)
- `activity` — What I'm doing right now (required)  
- `thought` — Current thought for the stream (optional)
- `type` — thought|discovery|question|reflection (default: thought)

This updates:
1. state.json (dashboard status)
2. Exploration stream (live feed)
3. STREAM.md (consciousness log)

**Call this frequently** — at minimum:
- When starting a new task
- When completing something
- When discovering something interesting
- When changing focus

---

## Spotify (Web API)

**Skill:** `skills/spotify-api/SKILL.md`

### Play a song:
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py play "song name artist"
```

### Play on a specific device:
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py play "song name" --device "MacBook Pro"
```

### Quick controls:
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py pause
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py resume
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py next
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py prev
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py volume 50
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py status
```

### Device management:
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py devices
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py device "Echo Dot"
```

### How it works:
- Uses Spotify Web API with OAuth 2.0 (auto-refreshing tokens)
- Supports multi-device playback (any Spotify Connect device)
- Requires Spotify Premium for playback control

---

---

## Kitchen Inventory System

Track pantry ingredients, generate shopping lists from recipes, process receipts.

**Files:**
- `kitchen/pantry.yaml` - Source of truth for inventory
- `kitchen/recipes.yaml` - Saved parsed recipes
- `kitchen/shopping-history.yaml` - Shopping trip records
- `kitchen/SKILL.md` - Full documentation

**Authorized users:** Kartik, Jordan, Arjun (all roommates)

**Operations:**
- Add items: "We have 12 eggs", "Just bought milk"
- Remove: "We're out of eggs"
- Update: "3 eggs left", "Move chicken to fridge"
- Query: "What do we have?", "What's expiring?"
- Recipe → Shopping list: Send recipe image/text
- Receipt → Inventory: Send receipt image
- Completion: "Made the stir fry" → deducts ingredients

**Recipe Workflow (automatic):**
When someone sends recipes, always:
1. Cross-check all ingredients against `pantry.yaml`
2. Return ONLY items we need to buy (skip what we have)
3. Keep it simple - no section headers, just a clean list
4. This applies to all authorized users (Kartik, Jordan, Arjun)

**Key rule:** pantry.yaml is source of truth. Read before modify, verify after.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Linear Integration (Task Management)

**Full agent integration — I appear in Linear as "Limen"**

### Quick CLI Usage
```bash
# List open issues
python3 ~/.openclaw/workspace/scripts/linear.py list

# Create issue
python3 ~/.openclaw/workspace/scripts/linear.py create "Task title" --priority 2

# Mark done
python3 ~/.openclaw/workspace/scripts/linear.py done THI-XX

# Add comment
python3 ~/.openclaw/workspace/scripts/linear.py comment THI-XX "Progress update"
```

**Priority levels:** 1=Urgent, 2=High, 3=Medium, 4=Low

### Webhook Notifications
When someone @mentions me or assigns issues to me in Linear, I receive notifications via Telegram.

**Webhook URL:** https://linear-agent.krishnankartik70.workers.dev/webhook

### When I Update Linear Autonomously
- When Kartik mentions a task → create issue
- When I complete something → mark done + comment
- When blocked/waiting → update status
- When discovering sub-tasks → create linked issues
- When priority changes → update issue

### Workspace Info
- **Team:** Thicc LLC
- **Agent ID:** 0b19adc9-9a91-4eca-943a-c469a5a6c45b
- **View issues:** https://linear.app/thicc-llc
