#!/usr/bin/env python3
"""Spotify OAuth 2.0 Authorization Code Flow + token management."""

import base64
import hashlib
import http.server
import json
import os
import secrets
import sys
import time
import urllib.parse
import webbrowser
from pathlib import Path

import requests

# Paths
SKILL_DIR = Path(__file__).parent
CONFIG_FILE = SKILL_DIR / "config.json"
SECRETS_DIR = Path.home() / ".openclaw" / "workspace" / "secrets"
SECRET_FILE = SECRETS_DIR / "spotify-client-secret.txt"
TOKEN_FILE = SECRETS_DIR / "spotify-tokens.json"

# Spotify endpoints
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = " ".join([
    "user-read-playback-state",
    "user-modify-playback-state",
    "user-read-currently-playing",
    "user-read-recently-played",
    "user-library-modify",
    "user-library-read",
    "playlist-read-private",
    "playlist-read-collaborative",
])


def load_config():
    if not CONFIG_FILE.exists():
        print(f"Error: {CONFIG_FILE} not found. Create it with your client_id.")
        sys.exit(1)
    with open(CONFIG_FILE) as f:
        return json.load(f)


def load_client_secret():
    if not SECRET_FILE.exists():
        print(f"Error: {SECRET_FILE} not found.")
        print("Create it with your Spotify client secret (single line).")
        sys.exit(1)
    return SECRET_FILE.read_text().strip()


def _auth_header(client_id, client_secret):
    encoded = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    return {"Authorization": f"Basic {encoded}"}


def save_tokens(token_data):
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 3600)
    SECRETS_DIR.mkdir(parents=True, exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(token_data, f, indent=2)
    os.chmod(TOKEN_FILE, 0o600)


def load_tokens():
    if not TOKEN_FILE.exists():
        return None
    with open(TOKEN_FILE) as f:
        return json.load(f)


def refresh_access_token():
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("Error: No refresh token. Run: python3 auth.py authorize")
        sys.exit(1)

    config = load_config()

    resp = requests.post(TOKEN_URL, data={
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": config["client_id"],
    })

    if resp.status_code != 200:
        print(f"Error refreshing token: {resp.status_code} {resp.text[:200]}")
        print("Run: python3 auth.py authorize")
        sys.exit(1)

    new_data = resp.json()
    # Spotify may or may not return a new refresh_token
    if "refresh_token" not in new_data:
        new_data["refresh_token"] = tokens["refresh_token"]
    save_tokens(new_data)
    return new_data["access_token"]


def get_valid_token():
    tokens = load_tokens()
    if not tokens:
        print("Error: Not authorized. Run: python3 auth.py authorize")
        sys.exit(1)

    # Refresh if within 60 seconds of expiry
    if time.time() >= tokens.get("expires_at", 0) - 60:
        return refresh_access_token()

    return tokens["access_token"]


def _generate_pkce():
    """Generate PKCE code_verifier and code_challenge."""
    code_verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode()
    return code_verifier, code_challenge


def authorize():
    config = load_config()
    client_id = config["client_id"]
    redirect_uri = config.get("redirect_uri", "http://localhost:8888/callback")

    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = _generate_pkce()

    params = urllib.parse.urlencode({
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "state": state,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
    })
    auth_url = f"{AUTH_URL}?{params}"

    # Parse port from redirect_uri
    parsed = urllib.parse.urlparse(redirect_uri)
    port = parsed.port or 8888

    auth_code = None
    error_msg = None

    class CallbackHandler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            nonlocal auth_code, error_msg
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            returned_state = query.get("state", [None])[0]
            if returned_state != state:
                error_msg = "State mismatch — possible CSRF attack."
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Error: State mismatch</h1>")
                return

            if "error" in query:
                error_msg = query["error"][0]
                self.send_response(400)
                self.send_header("Content-Type", "text/html")
                self.end_headers()
                self.wfile.write(f"<h1>Error: {error_msg}</h1>".encode())
                return

            auth_code = query.get("code", [None])[0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<h1>Authorization complete! You can close this tab.</h1>")

        def log_message(self, format, *args):
            pass  # Suppress server logs

    server = http.server.HTTPServer(("127.0.0.1", port), CallbackHandler)
    print(f"Opening browser for Spotify authorization...")
    webbrowser.open(auth_url)
    print(f"Waiting for callback on localhost:{port}...")

    # Handle one request (the callback)
    server.handle_request()
    server.server_close()

    if error_msg:
        print(f"Authorization failed: {error_msg}")
        sys.exit(1)

    if not auth_code:
        print("No authorization code received.")
        sys.exit(1)

    # Exchange code for tokens (PKCE: client_id in body, no Basic auth)
    resp = requests.post(TOKEN_URL, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
        "client_id": client_id,
        "code_verifier": code_verifier,
    })

    if resp.status_code != 200:
        print(f"Token exchange failed: {resp.status_code} {resp.text[:200]}")
        sys.exit(1)

    save_tokens(resp.json())
    print("Authorization successful! Tokens saved.")


def auth_status():
    tokens = load_tokens()
    if not tokens:
        print("Status: Not authorized")
        print("Run: python3 auth.py authorize")
        return

    expires_at = tokens.get("expires_at", 0)
    remaining = expires_at - time.time()

    if remaining > 0:
        minutes = int(remaining // 60)
        print(f"Status: Authorized")
        print(f"Token expires in: {minutes} minutes")
        print(f"Scopes: {tokens.get('scope', 'unknown')}")
    else:
        print("Status: Token expired (will auto-refresh on next use)")
        print(f"Scopes: {tokens.get('scope', 'unknown')}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 auth.py <authorize|status>")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "authorize":
        authorize()
    elif cmd == "status":
        auth_status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
