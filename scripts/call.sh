#!/usr/bin/env bash
set -euo pipefail

# Usage: call.sh <phone_number> [reason]
# Examples:
#   call.sh +13015256653 "Morning check-in, 2 meetings today"
#   call.sh +15551234567 "Following up on the interview"
#   call.sh +13015256653  (defaults to "Just calling to check in")

# Vapi credentials
ASSISTANT_ID="91c28dfc-dbf9-4787-901f-d69830842039"
PHONE_NUMBER_ID="ddc9b182-5ce1-48dd-ba0e-a0cb4f255744"
TO_NUMBER="${1:?Usage: call.sh <phone_number> [reason]}"
REASON="${2:-Just calling to check in}"

# Read API key from secrets
SECRETS_DIR="$HOME/.openclaw/workspace/secrets"
API_KEY=$(cat "$SECRETS_DIR/vapi-api-key.txt" 2>/dev/null || echo "")

if [ -z "$API_KEY" ]; then
  echo "Error: Vapi API key not found at $SECRETS_DIR/vapi-api-key.txt" >&2
  exit 1
fi

# Make the outbound call via Vapi
# Note: Reason is passed as metadata but assistant won't see it directly
# Consider adding assistantOverrides with a system message if needed
curl -s -X POST "https://api.vapi.ai/call" \
  -H "Authorization: Bearer ${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"assistantId\": \"${ASSISTANT_ID}\",
    \"phoneNumberId\": \"${PHONE_NUMBER_ID}\",
    \"customer\": {
      \"number\": \"${TO_NUMBER}\"
    },
    \"metadata\": {
      \"reason\": \"${REASON}\"
    }
  }"
