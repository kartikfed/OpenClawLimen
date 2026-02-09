#!/usr/bin/env bash
# Usage: exploration-stream.sh <type> <content> [sessionId] [metadata_json]
# Types: thought, tool_call, tool_result, discovery, question, reflection, start, end
#
# Examples:
#   exploration-stream.sh thought "I wonder how vector databases handle temporal memory..."
#   exploration-stream.sh tool_call "Searching for 'agent memory architectures'" "morning-2026-02-06" '{"tool":"web_search"}'
#   exploration-stream.sh discovery "Found that LangChain uses a sliding window approach"

TYPE="${1:?Usage: exploration-stream.sh <type> <content> [sessionId] [metadata_json]}"
CONTENT="${2:?Content required}"
SESSION_ID="${3:-exploration-$(date +%Y-%m-%d)}"
METADATA="${4:-{}}"

DASHBOARD_URL="http://localhost:3001"
AUTH="kartik:openclaw2026"

# Escape content for JSON (basic escaping)
ESCAPED_CONTENT=$(echo "$CONTENT" | sed 's/\\/\\\\/g; s/"/\\"/g; s/	/\\t/g' | tr '\n' ' ')

curl -s -X POST "${DASHBOARD_URL}/api/exploration/stream" \
  -H "Content-Type: application/json" \
  -H "Authorization: Basic $(echo -n ${AUTH} | base64)" \
  -d "{
    \"sessionId\": \"${SESSION_ID}\",
    \"type\": \"${TYPE}\",
    \"content\": \"${ESCAPED_CONTENT}\",
    \"metadata\": ${METADATA}
  }"
