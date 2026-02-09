# Bug Tracker

*Active issues I'm working on. Will test thoroughly before marking fixed.*

## Active Bugs

### 🔴 IN PROGRESS: Knowledge graph animations choppy
- **Status:** Claude Code investigating (2026-02-06 2:32 PM)
- **Symptoms:** Jerky/choppy movement despite physics tweaks
- **Agent:** Claude Code session `quiet-pine` working on deep fix
- **My attempts:** Changed d3AlphaDecay/velocityDecay - didn't fully resolve

### 🔴 IN PROGRESS: Node detail pane still too small
- **Status:** Claude Code investigating (2026-02-06 2:32 PM)
- **Symptoms:** Pane still appears same size despite w-[520px] change
- **Agent:** Claude Code session `quiet-pine` investigating
- **My attempts:** Changed to w-[520px] - may not have applied

### 🔴 IN PROGRESS: Legend not in correct position
- **Status:** Claude Code investigating (2026-02-06 2:32 PM)
- **Symptoms:** Legend not visible without scrolling
- **Agent:** Claude Code session `quiet-pine` fixing
- **My attempts:** Moved to top-24 - may not have applied

### 🔴 IN PROGRESS: Orbit controls for sphere navigation
- **Status:** Claude Code investigating (2026-02-06 2:32 PM)
- **Agent:** Claude Code session `quiet-pine` verifying

### ✅ FIXED: Voice calls not responding after greeting
- **Status:** Fixed (2026-02-06 10:38 AM)
- **Root cause:** `turn_timeout` was 7 seconds, but custom LLM responses were taking up to 7.25s
- **Fix:** Increased `turn_timeout` from 7.0 to 15.0 seconds in ElevenLabs agent config
- **Verification:** Test call had 8 turns, 75 seconds of successful back-and-forth conversation

### 🟢 LOW: Dynamic greeting webhook not enabled
- **Status:** Ready to enable (voice calls now working)
- **Symptoms:** N/A - intentionally disabled pending voice fix
- **Next steps:** Re-enable webhook now that voice calls work
- **Testing:** 5 successful calls with dynamic greetings

### ✅ FIXED: Cron jobs not executing on schedule
- **Status:** Fixed (2026-02-06 10:27 AM)
- **Root cause:** Jobs WERE running! But `delivery.mode: "none"` meant no announcements
- **Fix:** Changed all exploration jobs to `delivery.mode: "announce"` to Telegram
- **Verification:** Name Exploration ran at 10:25 AM, updated files, state.json shows new timestamp

## Recently Fixed

*(Move bugs here with fix date and verification)*

---

## Fix Protocol

1. Identify root cause
2. Implement fix
3. Test thoroughly myself (specific test criteria per bug)
4. Update state.json with progress
5. Only notify Kartik when confident it's fixed
6. Monitor for regressions

*Last updated: 2026-02-06 09:46 AM*
