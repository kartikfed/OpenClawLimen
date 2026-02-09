# VAPI Post-Call Webhook

Cloudflare Worker that receives VAPI end-of-call reports and sends them to Limen via Telegram for memory processing.

## Setup

1. Deploy the worker:
   ```bash
   cd ~/.openclaw/workspace/vapi-webhook
   npx wrangler deploy
   ```

2. Copy the deployed URL (e.g., `https://vapi-webhook.krishnankartik70.workers.dev`)

3. Configure in VAPI Dashboard:
   - Go to your Assistant settings
   - Find "Server URL" or "Webhook URL"
   - Paste the Cloudflare Worker URL
   - Ensure `end-of-call-report` events are enabled

## How It Works

1. Call ends (inbound or outbound)
2. VAPI sends `end-of-call-report` to this webhook
3. Worker extracts: caller/recipient, duration, transcript, summary
4. Worker sends formatted message to Telegram (Kartik's chat)
5. Limen receives the message and processes it:
   - Checks if contact is known or new
   - Updates MEMORY.md if needed
   - Logs call in daily memory file
   - Updates knowledge graph

## Known Contacts

The worker maintains a list of known contacts to flag unknown callers:
- Kartik: +13015256653
- Jordan: +12409884978
- Rishik: +17326475138
- Shimon: +15854654046
- PV: +13015006661
- Sanjay: +13013233653

Add new contacts to `KNOWN_CONTACTS` in worker.js when documenting them.

## Testing

Use wrangler dev for local testing:
```bash
npx wrangler dev
```

Then send a test POST request to the local server.
