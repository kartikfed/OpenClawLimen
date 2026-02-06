---
name: dynamic-greeting
description: Generates contextual, varied greetings for the ElevenLabs voice agent. Reads time of day, recent memory, and personality context to create natural phone greetings.
---

# Dynamic Greeting Generator

Generates fresh greetings every 5 minutes via cron. Pushes to ElevenLabs API automatically.

## Usage
- **Check current greeting:** `cat ~/.openclaw/workspace/skills/dynamic-greeting/current.txt`
- **Manual run:** `python3 ~/.openclaw/workspace/skills/dynamic-greeting/generate_greeting.py`
- **Update last call time:** Edit state.json `last_call_time` field

## Config
Edit `config.json` with your ElevenLabs agent_id and api_key.
