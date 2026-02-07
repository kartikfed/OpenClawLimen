#!/usr/bin/env python3
"""Headless Spotify search and play - no visible browser"""
import sys
import subprocess
import re

def search_spotify_headless(query):
    """Search Spotify using headless browser"""
    from playwright.sync_api import sync_playwright
    
    encoded = query.replace(' ', '%20')
    url = f"https://open.spotify.com/search/{encoded}/tracks"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=10000)
        
        # Get first track link
        links = page.query_selector_all('a[href*="/track/"]')
        if links:
            href = links[0].get_attribute('href')
            match = re.search(r'/track/([a-zA-Z0-9]+)', href)
            if match:
                browser.close()
                return match.group(1)
        
        browser.close()
        return None

def play_track(track_id):
    """Play via AppleScript"""
    subprocess.run(['osascript', '-e', 
        f'tell application "Spotify" to play track "spotify:track:{track_id}"'])

def get_current_track():
    """Get current track info"""
    result = subprocess.run(['osascript', '-e',
        'tell application "Spotify" to return name of current track & " - " & artist of current track'],
        capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: spotify-play.py <song name>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    print(f"🔍 Searching: {query}")
    
    track_id = search_spotify_headless(query)
    if track_id:
        play_track(track_id)
        import time
        time.sleep(1)
        print(f"▶️ {get_current_track()}")
    else:
        print("❌ No track found")
        sys.exit(1)
