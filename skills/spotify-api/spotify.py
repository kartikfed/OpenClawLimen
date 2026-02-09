#!/usr/bin/env python3
"""Spotify Web API CLI — search, playback, devices, queue, library.

Usage: python3 spotify.py <command> [args...]

Commands:
  search <query> [--type track|album|artist|playlist]
  play <query> [--device <name>] [--uri <spotify:uri>]
  pause
  resume
  next
  prev
  seek <seconds>
  volume <0-100>
  shuffle on|off
  repeat off|track|context
  status
  devices
  device <name_or_id>
  queue <query> [--device <name>]
  queue --show
  playlists
  recent
  like
  unlike
  auth [status]
"""

import json
import sys
import time
from pathlib import Path

import requests

# Add skill dir to path for auth import
sys.path.insert(0, str(Path(__file__).parent))
from auth import get_valid_token, authorize, auth_status

API_BASE = "https://api.spotify.com/v1"


def api(method, endpoint, retry_auth=True, **kwargs):
    """Make an authenticated Spotify API request."""
    token = get_valid_token()
    headers = {"Authorization": f"Bearer {token}"}
    if "json" in kwargs:
        headers["Content-Type"] = "application/json"

    url = f"{API_BASE}{endpoint}"
    resp = requests.request(method, url, headers=headers, **kwargs)

    if resp.status_code == 204:
        return None

    if resp.status_code == 200 or resp.status_code == 201:
        if resp.text:
            return resp.json()
        return None

    if resp.status_code == 401 and retry_auth:
        from auth import refresh_access_token
        refresh_access_token()
        return api(method, endpoint, retry_auth=False, **kwargs)

    if resp.status_code == 403:
        error = resp.json().get("error", {})
        reason = error.get("reason", "")
        if reason == "PREMIUM_REQUIRED":
            print("Error: Spotify Premium required for playback control.")
        else:
            print(f"Error: Forbidden — {error.get('message', 'unknown')}")
        sys.exit(1)

    if resp.status_code == 404:
        error = resp.json().get("error", {})
        msg = error.get("message", "")
        if "no active device" in msg.lower() or "device" in msg.lower():
            print("Error: No active Spotify device.")
            _suggest_devices()
        else:
            print(f"Error: {msg}")
        sys.exit(1)

    if resp.status_code == 429:
        retry_after = resp.headers.get("Retry-After", "a few")
        print(f"Rate limited. Retry after {retry_after} seconds.")
        sys.exit(1)

    print(f"Error {resp.status_code}: {resp.text[:200]}")
    sys.exit(1)


def _suggest_devices():
    data = api("GET", "/me/player/devices")
    devices = data.get("devices", []) if data else []
    if devices:
        print("Available devices:")
        for i, d in enumerate(devices, 1):
            active = " [ACTIVE]" if d["is_active"] else ""
            print(f"  {i}. {d['name']} ({d['type']}){active}")
        print("Use: spotify.py device <name>")
    else:
        print("No devices found. Open Spotify on a device first.")


def _resolve_device_id(name):
    """Resolve a device name/number to a device ID."""
    data = api("GET", "/me/player/devices")
    devices = data.get("devices", []) if data else []
    if not devices:
        print("No devices found. Open Spotify on a device first.")
        sys.exit(1)

    # Try numeric index
    try:
        idx = int(name) - 1
        if 0 <= idx < len(devices):
            return devices[idx]["id"]
    except ValueError:
        pass

    # Try exact or partial name match (case-insensitive)
    name_lower = name.lower()
    for d in devices:
        if d["name"].lower() == name_lower:
            return d["id"]
    for d in devices:
        if name_lower in d["name"].lower():
            return d["id"]

    print(f"Device '{name}' not found. Available:")
    for i, d in enumerate(devices, 1):
        print(f"  {i}. {d['name']} ({d['type']})")
    sys.exit(1)


def _parse_flag(args, flag):
    """Extract a --flag value from args list, returns (value, remaining_args)."""
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            val = args[idx + 1]
            remaining = args[:idx] + args[idx + 2:]
            return val, remaining
    return None, args


def _format_duration(ms):
    seconds = ms // 1000
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"


# --- Commands ---

def cmd_search(args):
    if not args:
        print("Usage: spotify.py search <query> [--type track|album|artist|playlist]")
        sys.exit(1)

    search_type, args = _parse_flag(args, "--type")
    search_type = search_type or "track"
    query = " ".join(args)

    data = api("GET", "/search", params={"q": query, "type": search_type, "limit": 5})
    key = search_type + "s"
    items = data.get(key, {}).get("items", [])

    if not items:
        print(f"No {search_type} results for '{query}'")
        return

    for i, item in enumerate(items, 1):
        if search_type == "track":
            artists = ", ".join(a["name"] for a in item["artists"])
            dur = _format_duration(item["duration_ms"])
            print(f"  {i}. {item['name']} — {artists} [{dur}]")
            print(f"     URI: {item['uri']}")
        elif search_type == "album":
            artists = ", ".join(a["name"] for a in item["artists"])
            print(f"  {i}. {item['name']} — {artists} ({item.get('release_date', '?')})")
            print(f"     URI: {item['uri']}")
        elif search_type == "artist":
            followers = item.get("followers", {}).get("total", 0)
            print(f"  {i}. {item['name']} ({followers:,} followers)")
            print(f"     URI: {item['uri']}")
        elif search_type == "playlist":
            owner = item.get("owner", {}).get("display_name", "?")
            total = item.get("tracks", {}).get("total", 0)
            print(f"  {i}. {item['name']} by {owner} ({total} tracks)")
            print(f"     URI: {item['uri']}")


def cmd_play(args):
    uri, args = _parse_flag(args, "--uri")
    device_name, args = _parse_flag(args, "--device")

    params = {}
    if device_name:
        params["device_id"] = _resolve_device_id(device_name)

    if uri:
        # Play a specific URI
        if ":track:" in uri:
            body = {"uris": [uri]}
        else:
            body = {"context_uri": uri}
        api("PUT", "/me/player/play", params=params, json=body)
    elif args:
        # Search and play first result
        query = " ".join(args)
        data = api("GET", "/search", params={"q": query, "type": "track", "limit": 1})
        items = data.get("tracks", {}).get("items", [])
        if not items:
            print(f"No results for '{query}'")
            sys.exit(1)
        track_uri = items[0]["uri"]
        api("PUT", "/me/player/play", params=params, json={"uris": [track_uri]})
    else:
        # Resume playback
        api("PUT", "/me/player/play", params=params)

    time.sleep(0.5)
    cmd_status([])


def cmd_pause(_args):
    api("PUT", "/me/player/pause")
    print("Paused.")


def cmd_resume(_args):
    api("PUT", "/me/player/play")
    time.sleep(0.5)
    cmd_status([])


def cmd_next(_args):
    api("POST", "/me/player/next")
    time.sleep(0.5)
    cmd_status([])


def cmd_prev(_args):
    api("POST", "/me/player/previous")
    time.sleep(0.5)
    cmd_status([])


def cmd_seek(args):
    if not args:
        print("Usage: spotify.py seek <seconds>")
        sys.exit(1)
    ms = int(args[0]) * 1000
    api("PUT", "/me/player/seek", params={"position_ms": ms})
    print(f"Seeked to {args[0]}s.")


def cmd_volume(args):
    if not args:
        print("Usage: spotify.py volume <0-100>")
        sys.exit(1)
    vol = int(args[0])
    api("PUT", "/me/player/volume", params={"volume_percent": vol})
    print(f"Volume set to {vol}%.")


def cmd_shuffle(args):
    if not args or args[0] not in ("on", "off"):
        print("Usage: spotify.py shuffle on|off")
        sys.exit(1)
    state = args[0] == "on"
    api("PUT", "/me/player/shuffle", params={"state": str(state).lower()})
    print(f"Shuffle {'on' if state else 'off'}.")


def cmd_repeat(args):
    if not args or args[0] not in ("off", "track", "context"):
        print("Usage: spotify.py repeat off|track|context")
        sys.exit(1)
    api("PUT", "/me/player/repeat", params={"state": args[0]})
    print(f"Repeat: {args[0]}.")


def cmd_status(_args):
    data = api("GET", "/me/player")
    if not data:
        print("Nothing playing.")
        return

    item = data.get("item")
    if not item:
        print("Nothing playing.")
        return

    name = item.get("name", "Unknown")
    artists = ", ".join(a["name"] for a in item.get("artists", []))
    album = item.get("album", {}).get("name", "")
    progress = _format_duration(data.get("progress_ms", 0))
    duration = _format_duration(item.get("duration_ms", 0))
    is_playing = data.get("is_playing", False)
    state = "Playing" if is_playing else "Paused"

    device = data.get("device", {})
    device_name = device.get("name", "Unknown")
    device_vol = device.get("volume_percent", "?")

    print(f"{state}: {name} — {artists}")
    print(f"Album: {album}")
    print(f"Progress: {progress} / {duration}")
    print(f"Device: {device_name} (volume: {device_vol}%)")


def cmd_devices(_args):
    data = api("GET", "/me/player/devices")
    devices = data.get("devices", []) if data else []
    if not devices:
        print("No devices found. Open Spotify on a device first.")
        return
    print("Devices:")
    for i, d in enumerate(devices, 1):
        active = " [ACTIVE]" if d["is_active"] else ""
        vol = d.get("volume_percent", "?")
        print(f"  {i}. {d['name']} ({d['type']}) [volume: {vol}%]{active}")


def cmd_device(args):
    if not args:
        print("Usage: spotify.py device <name_or_id>")
        sys.exit(1)
    device_id = _resolve_device_id(" ".join(args))
    api("PUT", "/me/player", json={"device_ids": [device_id]})
    print(f"Playback transferred.")


def cmd_queue(args):
    show, args = _parse_flag(args, "--show")
    if show is not None or (args and args[0] == "--show"):
        # Show current queue
        data = api("GET", "/me/player/queue")
        if not data:
            print("Queue is empty.")
            return
        current = data.get("currently_playing")
        if current:
            artists = ", ".join(a["name"] for a in current.get("artists", []))
            print(f"Now playing: {current['name']} — {artists}")
        queue = data.get("queue", [])
        if queue:
            print(f"Queue ({len(queue)} tracks):")
            for i, item in enumerate(queue[:10], 1):
                artists = ", ".join(a["name"] for a in item.get("artists", []))
                print(f"  {i}. {item['name']} — {artists}")
            if len(queue) > 10:
                print(f"  ... and {len(queue) - 10} more")
        else:
            print("Queue is empty.")
        return

    if not args:
        print("Usage: spotify.py queue <query> | spotify.py queue --show")
        sys.exit(1)

    device_name, args = _parse_flag(args, "--device")
    query = " ".join(args)

    # Search for track
    data = api("GET", "/search", params={"q": query, "type": "track", "limit": 1})
    items = data.get("tracks", {}).get("items", [])
    if not items:
        print(f"No results for '{query}'")
        sys.exit(1)

    track = items[0]
    params = {"uri": track["uri"]}
    if device_name:
        params["device_id"] = _resolve_device_id(device_name)

    api("POST", "/me/player/queue", params=params)
    artists = ", ".join(a["name"] for a in track["artists"])
    print(f"Added to queue: {track['name']} — {artists}")


def cmd_playlists(_args):
    data = api("GET", "/me/playlists", params={"limit": 20})
    items = data.get("items", []) if data else []
    if not items:
        print("No playlists found.")
        return
    print("Playlists:")
    for i, p in enumerate(items, 1):
        total = p.get("tracks", {}).get("total", 0)
        print(f"  {i}. {p['name']} ({total} tracks)")
        print(f"     URI: {p['uri']}")


def cmd_recent(_args):
    data = api("GET", "/me/player/recently-played", params={"limit": 10})
    items = data.get("items", []) if data else []
    if not items:
        print("No recent tracks.")
        return
    print("Recently played:")
    for i, item in enumerate(items, 1):
        track = item["track"]
        artists = ", ".join(a["name"] for a in track["artists"])
        print(f"  {i}. {track['name']} — {artists}")


def cmd_like(_args):
    data = api("GET", "/me/player")
    if not data or not data.get("item"):
        print("Nothing playing.")
        return
    track = data["item"]
    api("PUT", "/me/tracks", params={"ids": track["id"]})
    artists = ", ".join(a["name"] for a in track["artists"])
    print(f"Liked: {track['name']} — {artists}")


def cmd_unlike(_args):
    data = api("GET", "/me/player")
    if not data or not data.get("item"):
        print("Nothing playing.")
        return
    track = data["item"]
    api("DELETE", "/me/tracks", params={"ids": track["id"]})
    artists = ", ".join(a["name"] for a in track["artists"])
    print(f"Removed: {track['name']} — {artists}")


def cmd_auth(args):
    if args and args[0] == "status":
        auth_status()
    else:
        authorize()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    commands = {
        "search": cmd_search,
        "play": cmd_play,
        "pause": cmd_pause,
        "resume": cmd_resume,
        "next": cmd_next,
        "prev": cmd_prev,
        "seek": cmd_seek,
        "volume": cmd_volume,
        "shuffle": cmd_shuffle,
        "repeat": cmd_repeat,
        "status": cmd_status,
        "devices": cmd_devices,
        "device": cmd_device,
        "queue": cmd_queue,
        "playlists": cmd_playlists,
        "recent": cmd_recent,
        "like": cmd_like,
        "unlike": cmd_unlike,
        "auth": cmd_auth,
    }

    handler = commands.get(cmd)
    if not handler:
        print(f"Unknown command: {cmd}")
        print("Run with no args to see available commands.")
        sys.exit(1)

    handler(args)


if __name__ == "__main__":
    main()
