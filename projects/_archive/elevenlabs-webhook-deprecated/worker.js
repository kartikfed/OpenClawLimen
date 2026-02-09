// ElevenLabs Webhook Handler
// Deploy to Cloudflare Workers
// Handles: conversation_initiation (for dynamic greetings) + post_call_transcription (for summaries)

const BOT_TOKEN = "8436264291:AAFdQqsTT7EehEaWJWly2-73AtmpFT8-9Ww";

// Phone number → Telegram chat ID mapping
const PHONE_TO_TELEGRAM = {
  "+13015256653": "8574735426",  // Kartik
  "+12409884978": "8591201150",  // Jordan
};

// Phone number → Name mapping for Telegram
const PHONE_TO_NAME = {
  "+13015256653": "Kartik",
  "+12409884978": "Jordan",
};

// Phone number → Caller name for greetings
const PHONE_TO_GREETING_NAME = {
  "+13015256653": "Kartik",   // Kartik: "Hey Kartik, what's up?"
  "+12409884978": "Jordan",   // Jordan: "Hey Jordan, what's up?"
  "+17326475138": "Rishik",   // Rishik: "Hey Rishik, what's up?"
};

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("OK", { status: 200 });
    }

    try {
      const payload = await request.json();
      console.log("Received webhook:", JSON.stringify(payload, null, 2));
      
      // Handle conversation_initiation (has caller_id field, no type field)
      if (payload.caller_id) {
        console.log("Detected conversation_initiation webhook");
        return handleConversationInitiation(payload);
      }
      
      // Handle post_call_transcription (has type field)
      if (payload.type === "post_call_transcription") {
        return handlePostCallTranscription(payload);
      }
      
      // Unknown event type - log it
      console.log("Unknown webhook payload:", JSON.stringify(payload));
      return new Response("OK", { status: 200 });
    } catch (error) {
      console.error("Webhook error:", error, error.stack);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
};

function handleConversationInitiation(payload) {
  // caller_id is directly in the payload
  const callerId = payload.caller_id || "unknown";
  
  console.log(`Caller ID: ${callerId}`);
  
  // Map phone number to greeting
  const callerName = PHONE_TO_GREETING_NAME[callerId] || "there";
  const greeting = `Hey ${callerName}, what's up?`;
  
  console.log(`Final greeting: "${greeting}"`);
  
  // Return empty response to not break agent behavior
  // We'll use system prompt detection instead
  const response = {};
  
  console.log(`Returning empty response to preserve agent behavior`);
  
  return new Response(JSON.stringify(response), {
    status: 200,
    headers: { "Content-Type": "application/json" }
  });
}

async function handlePostCallTranscription(payload) {
  const data = payload.data;
  const transcript = data.transcript || [];
  const metadata = data.metadata || {};
  const analysis = data.analysis || {};
  
  // Get caller info from dynamic variables or metadata
  const dynamicVars = data.conversation_initiation_client_data?.dynamic_variables || {};
  const callerId = dynamicVars.system__caller_id || metadata.caller_id || "unknown";
  
  // Find Telegram chat for this caller
  const telegramChatId = PHONE_TO_TELEGRAM[callerId];
  const callerName = PHONE_TO_NAME[callerId] || "Unknown";
  
  // Build summary
  const duration = metadata.call_duration_secs || 0;
  const summary = analysis.transcript_summary || "";
  
  // Check if any actions were taken (tool calls)
  const hadToolCalls = transcript.some(t => t.tool_calls && t.tool_calls.length > 0);
  
  // Decide if we should send a Telegram message
  const shouldNotify = 
    hadToolCalls || 
    duration > 60 || 
    summary.toLowerCase().includes("remind") ||
    summary.toLowerCase().includes("task") ||
    summary.toLowerCase().includes("schedule") ||
    summary.toLowerCase().includes("send") ||
    summary.toLowerCase().includes("email");

  if (telegramChatId && shouldNotify) {
    const minutes = Math.floor(duration / 60);
    const seconds = duration % 60;
    const durationStr = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
    
    let message = `📞 **Call ended** (${durationStr})\n\n`;
    
    if (summary) {
      message += `**Summary:** ${summary.slice(0, 500)}`;
      if (summary.length > 500) message += "...";
    } else {
      // Build basic summary from transcript
      const userMessages = transcript
        .filter(t => t.role === "user")
        .map(t => t.message)
        .slice(-3);
      if (userMessages.length > 0) {
        message += `**You said:** ${userMessages.join(" → ").slice(0, 300)}`;
      }
    }

    if (hadToolCalls) {
      message += "\n\n✅ Actions were taken during this call.";
    }

    await sendTelegram(telegramChatId, message);
  }

  // Log for debugging (viewable in Cloudflare dashboard)
  console.log(`Call from ${callerName} (${callerId}), duration: ${duration}s, notified: ${shouldNotify}`);

  return new Response(JSON.stringify({ success: true }), {
    headers: { "Content-Type": "application/json" }
  });
}

async function sendTelegram(chatId, message) {
  try {
    const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: "Markdown"
      })
    });
    
    if (!response.ok) {
      console.error("Telegram send failed:", await response.text());
    }
  } catch (error) {
    console.error("Telegram send error:", error);
  }
}
