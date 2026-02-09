// VAPI Post-Call Webhook Handler
// Deploy to Cloudflare Workers
// Receives end-of-call reports from VAPI and triggers memory updates via Telegram

const BOT_TOKEN = "8436264291:AAFdQqsTT7EehEaWJWly2-73AtmpFT8-9Ww";
const LIMEN_CHAT_ID = "8574735426"; // Kartik's chat - Limen receives these

// Known contacts for context
const KNOWN_CONTACTS = {
  "+13015256653": { name: "Kartik", relationship: "owner" },
  "+12409884978": { name: "Jordan", relationship: "roommate" },
  "+17326475138": { name: "Rishik", relationship: "friend" },
  "+15854654046": { name: "Shimon", relationship: "former Microsoft coworker" },
  "+13015006661": { name: "PV", relationship: "Kartik's dad" },
  "+13013233653": { name: "Sanjay", relationship: "friend" },
};

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, {
        headers: {
          "Access-Control-Allow-Origin": "*",
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
        },
      });
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    try {
      const payload = await request.json();
      console.log("VAPI webhook received:", JSON.stringify(payload, null, 2));

      // VAPI sends different message types
      const messageType = payload.message?.type;

      // We only care about end-of-call-report
      if (messageType === "end-of-call-report") {
        return await handleEndOfCallReport(payload.message);
      }

      // For other events, just acknowledge
      console.log(`Ignoring event type: ${messageType}`);
      return new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      });

    } catch (error) {
      console.error("Webhook error:", error, error.stack);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" },
      });
    }
  },
};

async function handleEndOfCallReport(message) {
  // Extract call details
  const call = message.call || {};
  const direction = call.type || "unknown"; // "inboundPhoneCall" or "outboundPhoneCall"
  const customerNumber = call.customer?.number || "unknown";
  const durationSeconds = message.durationSeconds || 0;
  const endedReason = message.endedReason || "unknown";
  const transcript = message.transcript || "";
  const summary = message.summary || "";
  const messages = message.messages || [];

  // Format duration
  const minutes = Math.floor(durationSeconds / 60);
  const seconds = Math.round(durationSeconds % 60);
  const durationStr = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

  // Determine if this is a known or unknown contact
  const knownContact = KNOWN_CONTACTS[customerNumber];
  const isNewContact = !knownContact;
  const contactName = knownContact?.name || "Unknown";
  const contactRelationship = knownContact?.relationship || "";

  // Determine call direction label
  const directionLabel = direction.includes("inbound") ? "INBOUND" : "OUTBOUND";

  // Build the message for Limen to process
  let telegramMessage = `📞 **CALL ENDED - PROCESS FOR MEMORY**\n\n`;
  telegramMessage += `**Direction:** ${directionLabel}\n`;
  telegramMessage += `**Phone:** ${customerNumber}\n`;
  
  if (knownContact) {
    telegramMessage += `**Contact:** ${contactName} (${contactRelationship})\n`;
  } else {
    telegramMessage += `**Contact:** ⚠️ UNKNOWN - check if new person introduced themselves\n`;
  }
  
  telegramMessage += `**Duration:** ${durationStr}\n`;
  telegramMessage += `**Ended:** ${endedReason}\n\n`;

  // Add summary if available
  if (summary) {
    telegramMessage += `**Summary:**\n${summary}\n\n`;
  }

  // Add transcript (truncated if too long)
  if (transcript) {
    const maxTranscriptLength = 3000;
    let transcriptText = transcript;
    if (transcriptText.length > maxTranscriptLength) {
      transcriptText = transcriptText.slice(0, maxTranscriptLength) + "\n...[truncated]";
    }
    telegramMessage += `**Transcript:**\n${transcriptText}\n\n`;
  } else if (messages.length > 0) {
    // Build transcript from messages array
    const transcriptLines = messages
      .filter(m => m.role === "user" || m.role === "assistant")
      .map(m => `${m.role === "user" ? "Caller" : "Limen"}: ${m.content || m.message || ""}`)
      .slice(-20); // Last 20 exchanges
    
    if (transcriptLines.length > 0) {
      telegramMessage += `**Transcript (last ${transcriptLines.length} exchanges):**\n`;
      telegramMessage += transcriptLines.join("\n");
      telegramMessage += "\n\n";
    }
  }

  // Instructions for Limen
  telegramMessage += `---\n`;
  telegramMessage += `**ACTION REQUIRED:**\n`;
  if (isNewContact) {
    telegramMessage += `1. Check transcript for name/introduction\n`;
    telegramMessage += `2. If new person: Add to MEMORY.md Relationships section\n`;
  } else {
    telegramMessage += `1. Check if any new info about ${contactName} was shared\n`;
    telegramMessage += `2. Update their entry in MEMORY.md if relevant\n`;
  }
  telegramMessage += `3. Log call in memory/${new Date().toISOString().slice(0, 10)}.md\n`;
  telegramMessage += `4. Clear KG cache: rm -rf ~/.openclaw/workspace/.cache/knowledge-graph/*\n`;

  // Send to Telegram (which Limen receives)
  await sendTelegram(LIMEN_CHAT_ID, telegramMessage);

  console.log(`Processed ${directionLabel} call with ${contactName} (${customerNumber}), duration: ${durationStr}`);

  return new Response(JSON.stringify({ ok: true, processed: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}

async function sendTelegram(chatId, message) {
  try {
    // Telegram has a 4096 char limit, split if needed
    const maxLength = 4000;
    const chunks = [];
    
    if (message.length <= maxLength) {
      chunks.push(message);
    } else {
      // Split at newlines when possible
      let remaining = message;
      while (remaining.length > 0) {
        if (remaining.length <= maxLength) {
          chunks.push(remaining);
          break;
        }
        
        let splitIndex = remaining.lastIndexOf("\n", maxLength);
        if (splitIndex === -1 || splitIndex < maxLength / 2) {
          splitIndex = maxLength;
        }
        
        chunks.push(remaining.slice(0, splitIndex));
        remaining = remaining.slice(splitIndex);
      }
    }

    for (const chunk of chunks) {
      const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          chat_id: chatId,
          text: chunk,
          parse_mode: "Markdown",
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Telegram send failed:", errorText);
        
        // If markdown fails, try without parse_mode
        if (errorText.includes("can't parse")) {
          await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              chat_id: chatId,
              text: chunk,
            }),
          });
        }
      }
    }
  } catch (error) {
    console.error("Telegram send error:", error);
  }
}
