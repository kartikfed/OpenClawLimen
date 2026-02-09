#!/usr/bin/env python3
"""
Daily Digest Generator
Generates a summary of what happened today from memory files, state, and exploration logs.
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
OPENCLAW_URL = os.environ.get('OPENCLAW_URL', 'http://127.0.0.1:18789')
OPENCLAW_TOKEN = os.environ.get('OPENCLAW_TOKEN', '7b0823e46d5beef9870db213ace87139542badebad023323')

def read_file(path):
    """Read a file if it exists."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except:
        return None

def get_today_memory():
    """Get today's memory file."""
    today = datetime.now().strftime('%Y-%m-%d')
    path = WORKSPACE / 'memory' / f'{today}.md'
    return read_file(path) or "No memory file for today yet."

def get_state():
    """Get current state.json."""
    path = WORKSPACE / 'state.json'
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return {}

def get_exploration_log():
    """Get recent exploration log entries."""
    path = WORKSPACE / 'EXPLORATION-LOG.md'
    content = read_file(path)
    if not content:
        return "No exploration log."
    # Get last 50 lines
    lines = content.split('\n')
    return '\n'.join(lines[-50:])

def get_stream():
    """Get recent stream entries."""
    path = WORKSPACE / 'STREAM.md'
    content = read_file(path)
    if not content:
        return "No stream."
    lines = content.split('\n')
    return '\n'.join(lines[-30:])

def generate_digest():
    """Generate the daily digest using LLM."""
    import requests
    
    today_memory = get_today_memory()
    state = get_state()
    exploration = get_exploration_log()
    stream = get_stream()
    
    prompt = f"""Generate a daily digest summarizing what happened today. Be concise but capture the key highlights.

TODAY'S DATE: {datetime.now().strftime('%Y-%m-%d %A')}

CURRENT STATE:
- Mood: {state.get('mood', 'unknown')}
- Activity: {state.get('currentActivity', 'unknown')}
- Top of Mind: {state.get('topOfMind', [])}
- Recent Learnings: {state.get('recentLearnings', [])}
- Recent Actions: {state.get('recentActions', [])}

TODAY'S MEMORY FILE:
{today_memory[:3000]}

RECENT EXPLORATION LOG:
{exploration[:2000]}

RECENT STREAM (THOUGHTS):
{stream[:1500]}

---

Generate a digest with these sections:
1. **Summary** (2-3 sentences on the day's theme)
2. **Key Accomplishments** (bullet points)
3. **What I Learned** (insights, realizations)
4. **People & Interactions** (who I talked to, about what)
5. **Projects Progressed** (what moved forward)
6. **Questions Raised** (new curiosities)
7. **Mood/Energy** (how I'm doing)

Keep it readable and engaging. This is for Kartik to quickly catch up on what I did."""

    try:
        response = requests.post(
            f"{OPENCLAW_URL}/v1/chat/completions",
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {OPENCLAW_TOKEN}'
            },
            json={
                'model': 'anthropic/claude-sonnet-4',
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1500
            },
            timeout=60
        )
        
        if response.ok:
            data = response.json()
            digest = data['choices'][0]['message']['content']
            return digest
        else:
            return f"Error generating digest: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

def save_digest(digest):
    """Save the digest to a file."""
    today = datetime.now().strftime('%Y-%m-%d')
    path = WORKSPACE / 'digests' / f'{today}.md'
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, 'w') as f:
        f.write(f"# Daily Digest: {today}\n\n")
        f.write(f"*Generated at {datetime.now().strftime('%H:%M')}*\n\n")
        f.write(digest)
    
    return path

def main():
    print("📊 Generating daily digest...")
    digest = generate_digest()
    
    if digest.startswith("Error"):
        print(digest)
        return
    
    print("\n" + "="*60)
    print(digest)
    print("="*60 + "\n")
    
    path = save_digest(digest)
    print(f"✓ Saved to: {path}")

if __name__ == '__main__':
    main()
