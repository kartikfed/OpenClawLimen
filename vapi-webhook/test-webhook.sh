#!/usr/bin/env bash
# Test the VAPI webhook with a simulated end-of-call report

WEBHOOK_URL="${1:-https://vapi-webhook.krishnankartik70.workers.dev}"

echo "Sending test end-of-call-report to: $WEBHOOK_URL"

curl -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "message": {
      "type": "end-of-call-report",
      "call": {
        "type": "inboundPhoneCall",
        "customer": {
          "number": "+15551234567"
        }
      },
      "durationSeconds": 125,
      "endedReason": "customer-ended-call",
      "summary": "Test call from unknown number. Caller introduced themselves as Test Person and asked about the weather.",
      "transcript": "Limen: Hey there, what'\''s up?\nCaller: Hi, this is Test Person. I'\''m a friend of Kartik'\''s from college.\nLimen: Oh nice to meet you! What can I help you with?\nCaller: Just wanted to say hi and test the phone system.\nLimen: Cool, everything seems to be working great. Nice to meet you!\nCaller: Thanks, bye!\nLimen: Bye!"
    }
  }'

echo ""
echo "Check Telegram for the message!"
