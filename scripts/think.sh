#!/bin/bash
# Post a thought to the exploration stream
# Usage: think.sh "Your thought here" [type]
# Types: thought, discovery, question, reflection, tool_call, tool_result

THOUGHT="$1"
TYPE="${2:-thought}"

curl -s -X POST "http://localhost:3001/api/exploration/stream" \
  -u kartik:openclaw2026 \
  -H "Content-Type: application/json" \
  -d "{\"content\": \"$THOUGHT\", \"type\": \"$TYPE\", \"sessionId\": \"limen\"}" > /dev/null

echo "💭 Posted: $THOUGHT"
