#!/usr/bin/env bash
set -euo pipefail

# Usage: call.sh <phone_number> [reason]
# Examples:
#   call.sh +13015256653 "Morning check-in, 2 meetings today"
#   call.sh +15551234567 "Following up on the interview"
#   call.sh +13015256653  (defaults to "Just calling to check in")

AGENT_ID="agent_4501kgr1djxgf3sak8002w63d7cq"
PHONE_NUMBER_ID="phnum_1101kgr1tn61ed29g113a7122236"
TO_NUMBER="${1:?Usage: call.sh <phone_number> [reason]}"
REASON="${2:-Just calling to check in}"

API_KEY="${ELEVENLABS_API_KEY:-sk_REDACTED}"

# Marker file for webhook to detect outbound calls
OUTBOUND_MARKER="$HOME/.openclaw/workspace/scripts/.outbound_active"

# Step 1: Set outbound marker (webhook will read this)
echo "{\"to_number\": \"${TO_NUMBER}\", \"reason\": \"${REASON}\", \"timestamp\": \"$(date -Iseconds)\"}" > "$OUTBOUND_MARKER"

# Step 2: Make the outbound call
curl -s -X POST "https://api.elevenlabs.io/v1/convai/twilio/outbound-call" \
  -H "xi-api-key: ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"${AGENT_ID}\",
    \"agent_phone_number_id\": \"${PHONE_NUMBER_ID}\",
    \"to_number\": \"${TO_NUMBER}\"
  }"

# Step 3: Clean up marker after a delay (in case webhook doesn't fire)
(
  sleep 30
  rm -f "$OUTBOUND_MARKER" 2>/dev/null
) &
