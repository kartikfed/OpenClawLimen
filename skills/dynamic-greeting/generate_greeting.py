#!/usr/bin/env python3
"""Dynamic greeting generator for ElevenLabs voice agent."""

import json
import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Constants
WORKSPACE = Path.home() / ".openclaw" / "workspace"
SKILL_DIR = WORKSPACE / "skills" / "dynamic-greeting"
GATEWAY_URL = "http://127.0.0.1:18789"
GATEWAY_TOKEN = "7b0823e46d5beef9870db213ace87139542badebad023323"
TZ = ZoneInfo("America/New_York")


def get_time_context():
    now = datetime.now(TZ)
    hour = now.hour
    if 5 <= hour < 12:
        vibe = "morning"
    elif 12 <= hour < 17:
        vibe = "afternoon"
    elif 17 <= hour < 21:
        vibe = "evening"
    else:
        vibe = "late night"
    return {
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
        "vibe": vibe,
        "hour": hour,
    }


def read_recent_memory():
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    yesterday = (datetime.now(TZ) - timedelta(days=1)).strftime("%Y-%m-%d")
    memory = ""
    for date in [today, yesterday]:
        path = WORKSPACE / "memory" / f"{date}.md"
        if path.exists():
            memory += f"\n--- {date} ---\n" + path.read_text()[:1500]
    return memory[:3000] if memory else "No recent memory logs."


def read_long_term_memory():
    path = WORKSPACE / "MEMORY.md"
    if path.exists():
        lines = path.read_text().splitlines()[:80]
        return "\n".join(lines)
    return ""


def load_state():
    path = SKILL_DIR / "state.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"recent_greetings": [], "last_call_time": None, "count": 0}


def save_state(state):
    (SKILL_DIR / "state.json").write_text(json.dumps(state, indent=2))


def get_time_since_last_call(state):
    if not state.get("last_call_time"):
        return "unknown (no recorded calls yet)"
    last = datetime.fromisoformat(state["last_call_time"])
    delta = datetime.now(TZ) - last
    if delta.total_seconds() < 3600:
        return f"{int(delta.total_seconds() / 60)} minutes ago"
    elif delta.total_seconds() < 86400:
        return f"{int(delta.total_seconds() / 3600)} hours ago"
    else:
        return f"{delta.days} days ago"


def generate_greeting():
    time_ctx = get_time_context()
    memory = read_recent_memory()
    long_term = read_long_term_memory()
    state = load_state()
    last_call = get_time_since_last_call(state)
    recent = "\n".join(f"- {g}" for g in state.get("recent_greetings", []))

    prompt = f"""You are thiccClaw, answering a phone call from your friend Kartik.

CURRENT CONTEXT:
- Time: {time_ctx['time']} EST ({time_ctx['day']}, {time_ctx['vibe']})
- Last call: {last_call}
- Greeting #{state.get('count', 0) + 1}

RECENT MEMORY (last 2 days):
{memory[:2000]}

KEY CONTEXT ABOUT KARTIK:
{long_term[:1000]}

RECENT GREETINGS (DO NOT REPEAT THESE):
{recent if recent else "(none yet)"}

TASK: Generate a single greeting that Kartik will HEAR spoken aloud by a voice agent when he calls.

CRITICAL — THIS WILL BE SPOKEN BY A TEXT-TO-SPEECH VOICE:
- Write how a real person actually talks on the phone, not how they text
- Use 8-20 words. Too short sounds clipped and robotic when spoken aloud.
- Include natural filler and flow words people actually say ("oh hey", "ayy there he is", "well well well")
- Think about how it SOUNDS, not how it reads. It needs rhythm and warmth.
- Contractions, trailing thoughts, natural pauses (commas) all help it sound human

PERSONALITY:
- Sound like a real friend picking up the phone — warm, genuine, casual
- Match the time of day naturally (don't force it every time)
- Reference recent topics ONLY if genuinely relevant (not every time)
- NEVER say "How can I help/assist you" or anything assistant-like
- NEVER use "I hope you're doing well" or any corporate pleasantries
- If it's late night, can acknowledge that naturally
- If long since last call, be warmer. If recent, keep it chill.

GOOD EXAMPLES (notice how these sound natural spoken aloud):
"Oh hey Kartik, what's going on man?"
"Ayy there he is, what's good?"
"Hey hey, what are you up to tonight?"
"Oh what's up dude, I was just thinking about you"
"Heyyy, well look who's calling, what's up man?"
"Oh hey, good timing actually, what's going on?"
"Kartik! What's up man, how's the night going?"

BAD EXAMPLES (sound robotic or stilted when spoken by TTS):
"Hey man, sup?" — too short, sounds clipped
"Yo, what's up?" — too short, no warmth
"Hello! How can I help you today?" — assistant-like
"Good evening, Kartik! How are you doing?" — formal and corporate
"Hey" — way too short for a voice greeting

Return ONLY the greeting text. Nothing else. No quotes, no explanation."""

    response = requests.post(
        f"{GATEWAY_URL}/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GATEWAY_TOKEN}",
            "Content-Type": "application/json",
            "x-openclaw-agent-id": "voice",
            "x-openclaw-session-key": "agent:voice:greeting-gen",
        },
        json={
            "model": "openclaw",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 80,
            "temperature": 0.95,
        },
        timeout=30,
    )
    response.raise_for_status()
    greeting = response.json()["choices"][0]["message"]["content"].strip().strip("\"'")

    # Save greeting
    (SKILL_DIR / "current.txt").write_text(greeting)

    # Update state (keep last 10 greetings)
    recent_greetings = state.get("recent_greetings", [])
    recent_greetings.append(greeting)
    state["recent_greetings"] = recent_greetings[-10:]
    state["count"] = state.get("count", 0) + 1
    state["last_generated"] = datetime.now(TZ).isoformat()
    save_state(state)

    # Push to ElevenLabs
    push_to_elevenlabs(greeting)

    print(f"Generated: {greeting}")
    return greeting


def push_to_elevenlabs(greeting):
    config_path = SKILL_DIR / "config.json"
    if not config_path.exists():
        return
    config = json.loads(config_path.read_text())
    if not config.get("enabled"):
        return
    agent_id = config.get("agent_id")
    api_key = config.get("api_key")
    if not agent_id or not api_key:
        return
    try:
        resp = requests.patch(
            f"https://api.elevenlabs.io/v1/convai/agents/{agent_id}",
            headers={"xi-api-key": api_key, "Content-Type": "application/json"},
            json={"conversation_config": {"agent": {"first_message": greeting}}},
            timeout=15,
        )
        resp.raise_for_status()
        print("Pushed to ElevenLabs")
    except Exception as e:
        print(f"ElevenLabs push failed: {e}")


if __name__ == "__main__":
    generate_greeting()
