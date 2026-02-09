# Voice Agent Integration Evaluation: ElevenLabs vs Deepgram

**Created:** 2026-02-07 19:11 EST  
**Purpose:** Comprehensive evaluation prompt for external agent review

## Context
I'm building a voice agent that uses OpenClaw (custom LLM with tool calling) as the brain. The agent needs to:
1. Answer phone calls (inbound via Twilio)
2. Make phone calls (outbound)
3. Recognize callers by phone number and greet them by name
4. Execute tools (read calendar, check kitchen inventory, send emails, etc.)
5. Handle natural conversation with minimal latency

## Current Setup (ElevenLabs)
- **Platform:** ElevenLabs Agents (Conversational AI)
- **LLM:** Custom LLM endpoint pointing to OpenClaw at `https://[ngrok]/v1/chat/completions`
- **Phone Integration:** Twilio → ElevenLabs
- **Phone Number:** +12705170156
- **Time Invested:** 8+ hours today (Feb 7, 2026)

## Problems Encountered

### 1. Random Disconnects / Unreliable Calls
- Sometimes works for extended conversations (2-3 minutes)
- Other times hangs up after greeting or during tool execution
- Error message: "An application error has occurred. Welcome to Verizon Wireless..."

### 2. RTP Timeout Issue (Root Cause Hypothesis)
- Twilio has 12-second RTP silence timeout
- When OpenClaw + tool execution takes >12s, audio stream drops
- Call disconnects
- We emailed ElevenLabs support requesting timeout increase (no response yet, 1-3 day wait)

### 3. Caller-Specific Greeting Challenges

**Goal:** Greet callers by name based on their phone number

**Attempts:**
- **Attempt 1:** Dynamic variables in first_message (`{{caller_name}}`) → Variables didn't interpolate, said literally "Hey caller name"
- **Attempt 2:** Liquid conditional syntax in first_message → ElevenLabs parsed as malformed variables
- **Attempt 3:** Full SDK response format in webhook → "Application error"
- **Attempt 4:** Conversation initiation webhook with minimal response → **Greeting worked!** BUT broke agent's ability to continue conversation after greeting
- **Attempt 5:** System prompt with caller detection → Not tested (low confidence it would work)

**Finding:** Webhook for caller greetings works but breaks normal agent behavior. Calls would greet correctly then immediately disconnect or stop responding.

### 4. Twilio Integration Confusion
- Initial agent created via UI, unclear if properly configured
- Recreated agent via API following official guide (proper custom LLM setup)
- Phone number assignment via API successful
- BUT: Twilio webhook was pointing to old endpoint (`https://api.us.elevenlabs.io/twilio/inbound_call`)
- Attempted manual webhook update to `/v1/convai/twilio/register-call` → Failed with auth errors
- **Realization:** ElevenLabs needs to configure Twilio webhooks automatically through their UI, not manually

### 5. Agent Configuration State Unknown
Current agent (`agent_8101kgx80j30efb826q61vq9mvt4`):
- Created via API ✅
- Custom LLM configured ✅
- Phone number assigned ✅
- Twilio webhook... unclear ❓

---

## What We Tried (Chronological)

**5:50 PM** - Started debugging caller-specific greetings  
**6:00 PM** - Tested 4 different webhook response formats (all failed)  
**6:11 PM** - Found working minimal webhook response (greetings work, agent breaks)  
**6:21 PM** - SUCCESS: Greetings work! But agent can't handle follow-up questions  
**6:27 PM** - Kartik tests: greeting works, but asking about kitchen inventory → hang up  
**6:30 PM** - Jordan also reports "it's broken"  
**6:36 PM** - Researched Deepgram as alternative  
**6:42 PM** - Found official ElevenLabs + OpenClaw integration guide  
**6:46 PM** - Recreated agent via API following official guide (proper setup)  
**6:50 PM** - Reassigned phone number to new agent via API  
**6:56 PM** - Discovered Twilio webhook pointing to old endpoint  
**6:59 PM** - Manual Twilio webhook update failed (auth errors)  
**7:09 PM** - Still experiencing random disconnects, considering Deepgram

---

## Deepgram Voice Agent API (Alternative)

### What It Is
- Launched ~3 days ago (very new)
- Full voice orchestration: STT + LLM + TTS in one API
- YOU run the server (Python/Node)
- WebSocket connection: Twilio ↔ Your Server ↔ Deepgram

### Claimed Advantages
1. **Custom LLM Support:** Bring your own (OpenClaw) via `think.provider.url`
2. **Caller ID Customization:** Trivial because you control the server code:
   ```python
   caller_id = start.get("from")
   config["agent"]["greeting"] = f"Hey {name}!"
   ```
3. **Tool Calling:** Native function support
4. **Pricing:** ~$4.50/hr (vs ElevenLabs ~$5.90/hr)
5. **Free Credits:** $200 (vs ElevenLabs $1)
6. **Reliability Claims:** 
   - "Unified architecture" (vs ElevenLabs separate components)
   - VAQI benchmark: 29.3% better than ElevenLabs (source unclear)
   - Sub-300ms latency (unverified)

### Trade-offs
**Pros:**
- Full control over orchestration
- Caller customization is simple (you write the code)
- Potentially more reliable (but too new to confirm)

**Cons:**
- YOU run the server (12-16 hour setup estimate)
- Very new (3 days old) = unproven at scale
- WebSocket + Twilio integration still required
- **RTP timeout likely still exists** (same Twilio infrastructure)

---

## Key Questions for Evaluation

1. **Is ElevenLabs salvageable?**
   - Can we get Twilio webhook configured properly?
   - Will support respond in time with RTP timeout fix?
   - Is there a simpler config we're missing?

2. **Does Deepgram actually solve the core problems?**
   - Will it avoid random disconnects?
   - Does "unified architecture" really help with timeouts?
   - Is 12-16 hour setup realistic?

3. **RTP Timeout Reality Check**
   - Is this a Twilio infrastructure limit that affects BOTH platforms?
   - Or is ElevenLabs implementation specifically problematic?
   - Can Deepgram's faster processing keep queries under 12s?

4. **Sunk Cost Analysis**
   - ElevenLabs: 8 hours invested, limited progress, waiting on support
   - Deepgram: 0 hours invested, fresh start, full control
   - Which is better use of next 12-16 hours?

5. **Feature Parity**
   - Can Deepgram do everything ElevenLabs does?
   - Are there hidden limitations we'll hit?
   - What about voice quality/naturalness?

---

## What I Need from You

**Provide an unbiased, technical evaluation addressing:**

1. **Root cause analysis:** Are we actually hitting Twilio RTP timeout, or is something else wrong with our ElevenLabs setup?

2. **ElevenLabs path forward:** What specific steps could get ElevenLabs working reliably? Be concrete.

3. **Deepgram realistic assessment:** Will it actually solve our problems or just introduce new ones? Challenge the marketing claims.

4. **RTP timeout reality:** Does this affect both platforms equally? Can either actually solve it?

5. **Decision framework:** Given 8 hours invested in ElevenLabs with limited success, is switching to Deepgram (12-16 hour fresh start) the better path?

6. **Missing information:** What key details am I not considering? What should I test/verify before deciding?

**Be brutally honest.** Don't just recommend the shiny new thing. If ElevenLabs can work with 2-3 more hours of effort, say so. If both solutions will hit the same timeout wall, say so.

## Technical Details
- **OpenClaw endpoint:** `https://karole-legislatorial-raveningly.ngrok-free.dev/v1/chat/completions`
- **Model:** Claude Sonnet 4.5 via OpenClaw
- **Tools:** Kitchen inventory, calendar, email, etc.
- **Current agent:** `agent_8101kgx80j30efb826q61vq9mvt4` (ElevenLabs)
- **Twilio credentials:** Available
- **Deepgram API key:** Not yet obtained ($200 free credits available)

---

**Your recommendation will determine whether I spend the next 12-16 hours rebuilding on Deepgram or continuing to debug ElevenLabs.**
