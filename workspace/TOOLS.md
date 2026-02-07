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

## Spotify Control

**Skill:** `skills/spotify-control/SKILL.md`

### Play any song (headless, no browser window):
```bash
python3 ~/.openclaw/workspace/skills/spotify-control/spotify-play.py "song name artist"
```

### Quick controls:
```bash
# Play/pause
osascript -e 'tell application "Spotify" to playpause'

# Next/previous  
osascript -e 'tell application "Spotify" to next track'
osascript -e 'tell application "Spotify" to previous track'

# Current track
osascript -e 'tell application "Spotify" to return name of current track & " - " & artist of current track'

# Volume (0-100)
osascript -e 'tell application "Spotify" to set sound volume to 50'
```

### How it works:
- Uses Playwright headless Chrome to search Spotify
- Extracts track ID, plays via AppleScript
- No visible browser window, ~3 sec search time

### Future upgrade:
When Spotify re-enables dev apps, switch to `shpotify` for instant `spotify play "song"`

---

Add whatever helps you do your job. This is your cheat sheet.
