#!/usr/bin/env python3
"""Search Spotify using Firefox cookies and play via AppleScript"""
import browser_cookie3
import requests
import subprocess
import sys

def get_spotify_token():
    """Get access token using cookies"""
    cj = browser_cookie3.firefox(domain_name='.spotify.com')
    session = requests.Session()
    session.cookies = cj
    
    # Get token from web player
    resp = session.get('https://open.spotify.com/get_access_token?reason=transport&productType=web_player')
    if resp.ok:
        return resp.json().get('accessToken')
    return None

def search_track(query, token):
    """Search for a track"""
    headers = {'Authorization': f'Bearer {token}'}
    params = {'q': query, 'type': 'track', 'limit': 1}
    resp = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    if resp.ok:
        tracks = resp.json().get('tracks', {}).get('items', [])
        if tracks:
            return tracks[0]
    return None

def play_track(uri):
    """Play track via AppleScript"""
    subprocess.run(['osascript', '-e', f'tell application "Spotify" to play track "{uri}"'])

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: spotify-search.py <query>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"Searching for: {query}")
    
    token = get_spotify_token()
    if not token:
        print("Failed to get token")
        sys.exit(1)
    
    track = search_track(query, token)
    if track:
        name = track['name']
        artist = track['artists'][0]['name']
        uri = track['uri']
        print(f"Found: {name} by {artist}")
        print(f"Playing...")
        play_track(uri)
        print(f"▶️ Now playing: {name} - {artist}")
    else:
        print("No tracks found")
