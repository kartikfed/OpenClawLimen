---
name: spotify-api
description: Control Spotify playback, search music, manage devices and queue via the Spotify Web API.
---

# Spotify API

Full Spotify control via the Web API. Supports multi-device playback.

## Setup (one-time)

1. Add client secret: `~/.openclaw/workspace/secrets/spotify-client-secret.txt`
2. Edit `~/.openclaw/workspace/skills/spotify-api/config.json` with your `client_id`
3. Authorize: `python3 ~/.openclaw/workspace/skills/spotify-api/auth.py authorize`
   (Opens browser, log in, tokens saved automatically)

## Commands

### Play a song
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py play "song name artist"
```

### Play on a specific device
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py play "song name" --device "MacBook Pro"
```

### Play a specific URI
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py play --uri spotify:track:ID
```

### Search
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py search "query"
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py search "query" --type album
```
Types: track (default), album, artist, playlist

### Playback controls
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py pause
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py resume
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py next
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py prev
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py seek 30
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py volume 50
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py shuffle on
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py repeat track
```

### Current status
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py status
```

### Device management
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py devices
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py device "MacBook Pro"
```

### Queue
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py queue "song name"
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py queue --show
```

### Library
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py playlists
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py recent
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py like
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py unlike
```

### Auth management
```bash
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py auth         # Re-authorize
python3 ~/.openclaw/workspace/skills/spotify-api/spotify.py auth status  # Check token
```

## Notes
- Requires Spotify Premium for playback control
- Tokens auto-refresh; re-authorize only if refresh fails
- If no active device, use `devices` then `device <name>` first
- Device names support partial matching (e.g., "echo" matches "Echo Dot")
