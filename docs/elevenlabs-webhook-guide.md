# ElevenLabs Conversation Initiation Webhook Guide

**Last Updated:** 2026-02-07  
**Status:** ✅ Working  
**Debugging Time:** ~1.5 hours  

## The Goal

Create caller-specific greetings for ElevenLabs voice agents using the conversation initiation webhook. When someone calls, the agent should immediately greet them by name based on their phone number.

## What We Wanted

- Kartik (+13015256653) calls → "Hey Kartik, what's up?"
- Jordan (+12409884978) calls → "Hey Jordan, what's up?"
- Unknown number calls → "Hey there, what's up?"

## The Challenge

ElevenLabs documentation is sparse on HTTP webhook formats. Most examples show WebSocket SDK usage, not HTTP webhook responses. The API reference doesn't clearly document what the webhook should return.

## What DOESN'T Work (Failed Attempts)

### ❌ Attempt 1: Template Variables in First Message

**What we tried:**
```
First Message: "Hey {{caller_name}}, what's up?"
```

**Webhook response:**
```json
{
  "dynamic_variables": {
    "caller_name": "Kartik"
  }
}
```

**Result:** First message said literally "Hey caller name, what's up?" - variables didn't interpolate.

**Why it failed:** Dynamic variables work in SDK/programmatic calls, not in webhook-driven first messages.

---

### ❌ Attempt 2: Liquid Conditionals

**What we tried:**
```
First Message: 
{{#if (eq system__caller_id "+13015256653")}}
Hey man, what's up?
{{else}}
Hey there, what's up?
{{/if}}
```

**Result:** ElevenLabs dashboard showed errors for malformed variable names: `_if_eq_system__caller_id__13...`

**Why it failed:** ElevenLabs doesn't support conditional logic in first_message field.

---

### ❌ Attempt 3: Full SDK Response Format

**What we tried:**
Based on SDK test files, we returned:
```json
{
  "type": "conversation_initiation_client_data",
  "custom_llm_extra_body": {},
  "conversation_config_override": {
    "agent": {
      "first_message": "Hey Kartik, what's up?"
    }
  },
  "dynamic_variables": {},
  "source_info": {
    "source": "webhook",
    "version": "1.0.0"
  }
}
```

**Result:** "An application error has occurred. Welcome to Verizon Wireless..."

**Why it failed:** HTTP webhook response format ≠ WebSocket client format. The SDK tests show what clients SEND to ElevenLabs, not what webhooks should RETURN.

---

### ❌ Attempt 4: Detecting Wrong Event Type

**What we tried:**
```javascript
if (payload.type === "conversation_initiation_client_data_request") {
  return handleConversationInitiation(payload);
}
```

**Result:** Webhook was called but handler never ran. No response sent.

**Why it failed:** The incoming HTTP request has NO `type` field. We were checking for a field that doesn't exist.

---

## ✅ What DOES Work (Final Solution)

### Incoming Webhook Request Format

ElevenLabs sends a POST request with this JSON body:

```json
{
  "caller_id": "+13015256653",
  "agent_id": "agent_4501kgr1djxgf3sak8002w63d7cq",
  "called_number": "+12785178156",
  "call_sid": "CA4678d33491f8e5e749l8e979c5e64...",
  "conversation_id": "conv_8201kgx69dv1s2ar9aw6gpowkxs8a"
}
```

**Key insight:** No `type` field. Detect this event by checking for `caller_id` field.

### Correct Webhook Response Format

Return this minimal JSON:

```json
{
  "conversation_config_override": {
    "agent": {
      "first_message": "Hey Kartik, what's up?"
    }
  }
}
```

**That's it.** No `type`, no `dynamic_variables`, no `source_info`, no `custom_llm_extra_body`.

### Working Implementation

```javascript
// Phone number → Name mapping
const PHONE_TO_GREETING_NAME = {
  "+13015256653": "Kartik",
  "+12409884978": "Jordan",
  "+17326475138": "Rishik",
};

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("OK", { status: 200 });
    }

    try {
      const payload = await request.json();
      
      // Detect conversation_initiation by presence of caller_id
      if (payload.caller_id) {
        return handleConversationInitiation(payload);
      }
      
      // Handle other webhook types...
      return new Response("OK", { status: 200 });
    } catch (error) {
      console.error("Webhook error:", error);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
};

function handleConversationInitiation(payload) {
  const callerId = payload.caller_id || "unknown";
  const callerName = PHONE_TO_GREETING_NAME[callerId] || "there";
  const greeting = `Hey ${callerName}, what's up?`;
  
  const response = {
    conversation_config_override: {
      agent: {
        first_message: greeting
      }
    }
  };
  
  return new Response(JSON.stringify(response), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
}
```

## ElevenLabs Dashboard Configuration

### 1. Enable Webhook in Agent Settings

Navigate to: **Agent Settings → Platform Settings → Security**

Enable:
- ✅ **First Message** (under "Overrides" section)

### 2. Configure Webhook URL

Navigate to: **Agent Settings → Platform Settings → Workspace Overrides**

Find: **"Conversation Initiation Client Data Webhook"**

Set:
- **Fetch initiation client data from a webhook:** ON
- **URL:** `https://your-webhook-url.com`
- **Request headers:** (leave empty)

### 3. First Message Field

In the main agent settings, set **First Message** to anything (e.g., "Hello!"). The webhook will override it dynamically.

## Debugging Tips

### 1. Deploy a Test Webhook First

Before implementing logic, deploy a webhook that logs everything:

```javascript
export default {
  async fetch(request) {
    const payload = await request.json();
    
    // Send to yourself (Telegram, email, etc.)
    console.log("Received:", JSON.stringify(payload, null, 2));
    
    // Return minimal valid response
    return new Response(JSON.stringify({
      conversation_config_override: {
        agent: { first_message: "Test greeting" }
      }
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  }
};
```

This shows you EXACTLY what ElevenLabs sends.

### 2. Test Locally with curl

```bash
curl -X POST https://your-webhook-url.com \
  -H "Content-Type: application/json" \
  -d '{"caller_id":"+13015256653","agent_id":"test"}'
```

Verify the response format is valid JSON and returns 200 OK.

### 3. Check Cloudflare Worker Logs

If using Cloudflare Workers:

```bash
npx wrangler tail --format pretty
```

Then make a test call and watch the logs in real-time.

### 4. Error Messages to Watch For

- **"An application error has occurred"** = Invalid response format or webhook returning error
- **"Welcome to Verizon Wireless, your call could not be completed as dialed"** = Call isn't reaching ElevenLabs at all (phone number issue, not webhook issue)
- **Agent waits for user to speak** = Webhook not configured OR not returning first_message

## What Can Be Overridden

Based on the ElevenLabs SDK types, the `conversation_config_override` object supports:

```typescript
{
  conversation_config_override: {
    agent: {
      prompt?: {
        prompt?: string,
        llm?: string  // e.g. "gpt-4o"
      },
      first_message?: string,
      language?: string  // e.g. "en"
    },
    tts?: {
      voice_id?: string,
      stability?: number,    // 0.0 to 1.0
      speed?: number,        // 0.7 to 1.2
      similarity_boost?: number  // 0.0 to 1.0
    },
    conversation?: {
      text_only?: boolean
    }
  }
}
```

We only tested `first_message`, but theoretically you could also override the system prompt, voice, or LLM model per caller.

## Common Mistakes

1. **Using SDK formats for webhooks** - SDK tests show WebSocket message formats, not HTTP responses
2. **Checking for `type` field** - Incoming HTTP webhooks don't have this
3. **Overcomplicating the response** - Minimal format works; extra fields cause errors
4. **Not enabling "First Message" override** - Must be enabled in Security settings
5. **Testing without a debug webhook first** - You're flying blind without seeing the actual payload

## Related Files

- **Webhook code:** `~/.openclaw/workspace/elevenlabs-webhook/worker.js`
- **Deployment config:** `~/.openclaw/workspace/elevenlabs-webhook/wrangler.toml`
- **Webhook URL:** https://elevenlabs-webhook.krishnankartik70.workers.dev
- **Current version:** f1274a9b-92e1-4f9e-8076-706189f4cc3c (2026-02-07)

## Future Enhancements

- **Add more phone numbers** - Just add to `PHONE_TO_GREETING_NAME` object
- **Time-based greetings** - "Good morning Kartik" vs "Good evening Kartik"
- **Context-aware greetings** - Pass info about upcoming meetings, todos, etc.
- **Dynamic prompt override** - Different system prompts per caller
- **Voice override** - Different voices per caller

## Lessons Learned

1. **Documentation gaps are common** - Don't trust docs alone, test everything
2. **Test webhooks save hours** - Deploy a logger first, then implement logic
3. **Minimal responses often work better** - Start simple, add complexity only if needed
4. **WebSocket ≠ HTTP** - Different protocols often have different formats
5. **Source code is truth** - When docs fail, read the SDK source and examples

## Success Metrics

- ✅ Caller-specific greetings working
- ✅ Unknown callers get fallback greeting
- ✅ No "application error" messages
- ✅ Immediate greeting on call connect (no wait for user speech)
- ⏱️ Total debugging time: 1.5 hours (acceptable for undocumented API)

---

**Need help?** This guide documents what worked as of 2026-02-07. If ElevenLabs changes their webhook format, start by deploying the test webhook to see what's different.
