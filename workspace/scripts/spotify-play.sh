#!/bin/bash
# Fast Spotify search and play
# Uses browser briefly but minimizes disruption

QUERY="$*"
if [ -z "$QUERY" ]; then
    echo "Usage: spotify-play.sh <song name>"
    exit 1
fi

ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
URL="https://open.spotify.com/search/${ENCODED}/tracks"

# Use Python to get track ID via headless browser simulation
TRACK_ID=$(python3 << PYEOF
import subprocess
import json
import sys

# Use openclaw browser tool via CLI
result = subprocess.run([
    'curl', '-s', '-X', 'POST', 
    'http://127.0.0.1:18800/snapshot',
    '-H', 'Content-Type: application/json',
    '-d', '{"url": "${URL}"}'
], capture_output=True, text=True)

# Parse response for track ID
import re
matches = re.findall(r'/track/([a-zA-Z0-9]{22})', result.stdout)
if matches:
    print(matches[0])
PYEOF
)

if [ -z "$TRACK_ID" ]; then
    echo "Could not find track for: $QUERY"
    exit 1
fi

# Play it
osascript -e "tell application \"Spotify\" to play track \"spotify:track:$TRACK_ID\""
sleep 1
osascript -e 'tell application "Spotify" to return "▶️ " & name of current track & " - " & artist of current track'
