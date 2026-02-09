#!/bin/bash
# Update Mission Control - consolidates all status updates
# Usage: update-mission-control.sh "mood" "activity" "thought" [thought_type]
#
# This script updates:
# 1. state.json - current status for dashboard
# 2. Exploration stream - thought feed
# 3. STREAM.md - full consciousness log (optional, via --stream flag)

MOOD="$1"
ACTIVITY="$2"
THOUGHT="$3"
THOUGHT_TYPE="${4:-thought}"
TIMESTAMP=$(date +"%Y-%m-%dT%H:%M:%S%z" | sed 's/\([0-9][0-9]\)$/:\1/')
TIMESTAMP_DISPLAY=$(date +"%H:%M")

# Validate inputs
if [ -z "$MOOD" ] || [ -z "$ACTIVITY" ]; then
  echo "Usage: update-mission-control.sh \"mood\" \"activity\" \"thought\" [thought_type]"
  exit 1
fi

# 1. Update state.json
STATE_FILE="$HOME/.openclaw/workspace/state.json"
if [ -f "$STATE_FILE" ]; then
  # Use Python for reliable JSON manipulation
  python3 << EOF
import json
import sys

with open("$STATE_FILE", "r") as f:
    state = json.load(f)

state["mood"] = "$MOOD"
state["currentActivity"] = "$ACTIVITY"
state["status"] = "ACTIVE"
state["lastUpdated"] = "$TIMESTAMP"

# Add thought to streamOfConsciousness (keep last 5)
if "streamOfConsciousness" not in state:
    state["streamOfConsciousness"] = []
if "$THOUGHT":
    state["streamOfConsciousness"].insert(0, "$THOUGHT")
    state["streamOfConsciousness"] = state["streamOfConsciousness"][:5]

with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2)

print("✓ state.json updated")
EOF
fi

# 2. Post to exploration stream (if thought provided)
if [ -n "$THOUGHT" ]; then
  curl -s -X POST "http://localhost:3001/api/exploration/stream" \
    -u kartik:openclaw2026 \
    -H "Content-Type: application/json" \
    -d "{\"content\": \"$THOUGHT\", \"type\": \"$THOUGHT_TYPE\", \"sessionId\": \"limen\"}" > /dev/null 2>&1
  echo "✓ Exploration stream updated"
fi

# 3. Append to STREAM.md (brief entry)
STREAM_FILE="$HOME/.openclaw/workspace/STREAM.md"
if [ -n "$THOUGHT" ] && [ -f "$STREAM_FILE" ]; then
  echo "" >> "$STREAM_FILE"
  echo "**$TIMESTAMP_DISPLAY** — $THOUGHT" >> "$STREAM_FILE"
fi

echo "✓ Mission Control updated"
