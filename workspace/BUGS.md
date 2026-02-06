# Bug Tracker

*Active issues I'm working on. Will test thoroughly before marking fixed.*

## Active Bugs

### 🔴 HIGH: Voice calls not responding after greeting
- **Status:** Investigating
- **Symptoms:** Call connects, greeting plays, but agent doesn't respond to user speech
- **Root cause:** Unknown - LLM returns 200 OK but responses aren't spoken
- **Attempts:**
  1. Fixed streaming format (pipe → getReader) - partial fix
  2. Webhook format simplification - greeting works now
  3. Disabled webhook temporarily for reliability
- **Next steps:** 
  - Test custom LLM proxy thoroughly
  - Check if ElevenLabs expects specific SSE format
  - Review cascade timeout settings
- **Testing:** Must complete 3 successful back-and-forth calls before marking fixed

### 🟡 MEDIUM: Dynamic greeting webhook not working
- **Status:** Blocked by voice call bug
- **Symptoms:** Webhook returns correct data but calls fail
- **Root cause:** Possibly related to main voice call issue
- **Next steps:** Fix voice calls first, then re-enable webhook
- **Testing:** 5 successful calls with dynamic greetings

### 🟡 MEDIUM: Cron jobs not executing on schedule
- **Status:** Investigating
- **Symptoms:** Jobs are scheduled (nextRunAtMs set correctly) but don't execute
- **Affected:** Morning call (9:30 AM), Name exploration (9:45 AM), likely others
- **Root cause:** `wakeMode: "next-heartbeat"` — jobs queue until heartbeat triggers
- **Attempts:**
  1. Converting from "every" to "cron" schedule type - didn't help
  2. Adding mandatory state.json updates to payloads - didn't help execution
- **Next steps:**
  - Check if wakeMode should be changed to something else
  - Test if manual `cron run` works
  - Consider if heartbeats are too infrequent
- **Testing:** 3 consecutive scheduled jobs fire on time

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
