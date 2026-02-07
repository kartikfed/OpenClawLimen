---
name: spotify-control
description: Search and control Spotify playback using headless browser + AppleScript. No API keys needed.
---

# Spotify Control

Search and play music on Spotify without visible browser windows.

## Requirements

- Spotify desktop app installed and logged in
- Python 3 with playwright: `pip3 install playwright && python3 -m playwright install chromium`

## Commands

### Play a song
```bash
python3 ~/.openclaw/workspace/skills/spotify-control/spotify-play.py "song name artist"
```

### Quick controls (AppleScript)
```bash
# Play/pause
osascript -e 'tell application "Spotify" to playpause'

# Next/previous
osascript -e 'tell application "Spotify" to next track'
osascript -e 'tell application "Spotify" to previous track'

# Current track
osascript -e 'tell application "Spotify" to return name of current track & " - " & artist of current track'

# Volume (0-100)
osascript -e 'tell application "Spotify" to set sound volume to 50'
```

## How It Works

1. Uses Playwright headless Chrome to search open.spotify.com
2. Extracts the first track ID from search results  
3. Plays via AppleScript `tell application "Spotify" to play track "spotify:track:ID"`

No browser windows pop up. Search takes ~3 seconds.

## Future

When Spotify re-enables developer app creation, switch to `shpotify` for instant search:
```bash
brew install shpotify
# Add client_id/secret to ~/.shpotify.cfg
spotify play "song name"
```
