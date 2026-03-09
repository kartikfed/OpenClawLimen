# Morning Briefing Generator

Automated briefing generation for Kartik's morning calls.

## What It Does

Pulls from multiple sources and generates a formatted briefing:
- **Google Calendar**: Today's events, sorted by time
- **Gmail**: Urgent emails + priority senders (recruiters, interview-related)
- **TODO.md**: High priority tasks + daily recurring reminders
- **Context**: Day of week, weekend detection, greeting timing

## Usage

```bash
# Full briefing (all sources)
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py

# Specific sources
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py --calendar
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py --email
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py --todos

# JSON output (for programmatic use)
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py --json
```

## Example Output

```
☀️ **Good morning, Kartik!**
It's Monday, March 10, 2026.

📅 **Today's Calendar**
  • 10:00 AM: Standup
  • 02:00 PM: Interview prep call

📧 **Email Summary**
  🟡 **Priority (job-related):**
    • recruiter@anthropic.com: Follow-up on application
  (12 total emails in last 24h)

✅ **Tasks for Today**
  **Daily Reminders:**
    • Job applications
    • Schedule customer discovery calls
```

## Priority Detection

**Urgent emails** (flagged 🔴):
- Subject contains: urgent, action required, deadline, interview, offer, final round, decision

**Priority senders** (flagged 🟡):
- anthropic.com, janestreet.com, uber.com, figma.com, microsoft.com, actively.ai
- Any sender with "recruiter" or "interview" in the address

## Integration

**For morning cron job:**
```bash
# In briefing prep script
BRIEFING=$(python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py)
# Use $BRIEFING in call context
```

**For heartbeat checks:**
```bash
# Quick urgent check
python3 ~/.openclaw/workspace/skills/morning-briefing/briefing.py --email --json | jq '.emails.urgent'
```

## Configuration

Edit `briefing.py` to customize:
- `GOG_ACCOUNT`: Gmail account (default: krishnankartik70@gmail.com)
- `PRIORITY_SENDERS`: List of email domains to flag
- `URGENT_KEYWORDS`: Keywords that mark emails as urgent

## Requirements

- `gog` CLI installed and authenticated
- Python 3.10+
- `TODO.md` at workspace root

## Notes

- Calendar/email fetch can timeout if network is slow (30s default)
- Emails limited to last 24 hours, max 25
- Regular emails capped at 5 (priority/urgent shown in full)
