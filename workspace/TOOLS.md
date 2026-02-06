# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

## Phone Calls

Make outbound calls via ElevenLabs:
```
~/.openclaw/workspace/scripts/call.sh <phone_number> [reason]
```

- `phone_number` — required, E.164 format (e.g. +13015256653)
- `reason` — optional context the agent will use to open the call

Examples:
- `call.sh +13015256653 "Morning check-in, 2 meetings today"`
- `call.sh +15551234567 "Following up on the interview"`
- `call.sh +13015256653` (defaults to "Scheduled morning check-in")

Kartik's number: +13015256653

---

Add whatever helps you do your job. This is your cheat sheet.
