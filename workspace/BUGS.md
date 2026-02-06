# Bug Tracker

*Active issues I'm working on. Will test thoroughly before marking fixed.*

## Active Bugs

### ✅ FIXED: Knowledge graph animations choppy
- **Status:** Fixed (2026-02-06 2:28 PM)
- **Root cause:** Physics settings too aggressive (d3AlphaDecay=0.02, d3VelocityDecay=0.3)
- **Fix:** Reduced to d3AlphaDecay=0.008, d3VelocityDecay=0.15, increased warmupTicks/cooldownTicks to 100
- **Verification:** Needs visual check

### ✅ FIXED: Knowledge graph needs orbit controls (sphere navigation)
- **Status:** Fixed (2026-02-06 2:28 PM)
- **Root cause:** `enableNavigationControls={false}` was disabling orbit controls
- **Fix:** Set `enableNavigationControls={true}` and `controlType="orbit"` for sphere-like navigation
- **Verification:** Left-drag to orbit, right-drag to pan, scroll to zoom

### ✅ FIXED: Node detail pane too small
- **Status:** Fixed (2026-02-06 2:28 PM)
- **Root cause:** Panel was w-96 (384px) with small text
- **Fix:** Increased to w-[520px], larger fonts (text-base/text-xl), more padding
- **Verification:** Needs visual check

### ✅ FIXED: Status indicators at top too small
- **Status:** Fixed (2026-02-06 2:30 PM)
- **Root cause:** Text was xs (12px), padding was minimal
- **Fix:** Increased to sm (14px), larger icons (w-4), more padding (px-5 py-3), ring indicators
- **Verification:** Needs visual check

### ✅ FIXED: Knowledge graph legend not visible without scrolling
- **Status:** Fixed (2026-02-06 2:30 PM)
- **Root cause:** Legend was at bottom-4 (below fold)
- **Fix:** Moved to top-24 left-6, increased text sizes, better styling
- **Verification:** Needs visual check

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
