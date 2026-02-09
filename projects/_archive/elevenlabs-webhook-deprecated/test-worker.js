// Minimal test webhook - logs everything
const BOT_TOKEN = "8436264291:AAFdQqsTT7EehEaWJWly2-73AtmpFT8-9Ww";

async function sendTelegram(chatId, message) {
  try {
    await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text: message,
        parse_mode: "Markdown"
      })
    });
  } catch (e) {
    console.error("Telegram send failed:", e);
  }
}

export default {
  async fetch(request, env) {
    try {
      const method = request.method;
      const url = request.url;
      const headers = Object.fromEntries(request.headers);
      
      let body = null;
      if (method === "POST") {
        const text = await request.text();
        body = text;
        try {
          body = JSON.parse(text);
        } catch (e) {
          // Keep as text if not JSON
        }
      }
      
      // Send everything to Telegram
      const message = `🔍 **Webhook Called!**\n\n**Method:** ${method}\n**URL:** ${url}\n**Headers:**\n\`\`\`json\n${JSON.stringify(headers, null, 2).slice(0, 1000)}\n\`\`\`\n**Body:**\n\`\`\`json\n${JSON.stringify(body, null, 2).slice(0, 2000)}\n\`\`\``;
      
      await sendTelegram("8574735426", message);
      
      // Return the correct format
      return new Response(JSON.stringify({
        type: "conversation_initiation_client_data",
        custom_llm_extra_body: {},
        conversation_config_override: {
          agent: {
            first_message: "Hey test, what's up?"
          }
        },
        dynamic_variables: {},
        source_info: {
          source: "test_webhook",
          version: "1.0.0"
        }
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    } catch (error) {
      await sendTelegram("8574735426", `❌ **Webhook Error:**\n${error.message}\n${error.stack}`);
      return new Response(JSON.stringify({ error: error.message }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
  }
};
