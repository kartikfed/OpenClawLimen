#!/usr/bin/env python3
"""
Morning Briefing Generator
Automated briefing for Kartik's morning calls.

Pulls from:
- Google Calendar (today's events)
- Gmail (urgent/important emails from last 24h)
- TODO.md (high priority + recurring tasks)
- Memory context (recent events, pending items)

Usage:
    python3 briefing.py              # Full briefing
    python3 briefing.py --calendar   # Calendar only
    python3 briefing.py --email      # Email only
    python3 briefing.py --todos      # TODOs only
    python3 briefing.py --json       # Output as JSON
"""

import subprocess
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
import argparse


# Configuration
GOG_ACCOUNT = "krishnankartik70@gmail.com"
WORKSPACE = Path.home() / ".openclaw/workspace"
TODO_FILE = WORKSPACE / "TODO.md"
MEMORY_DIR = WORKSPACE / "memory"

# Email priority senders (check these first)
PRIORITY_SENDERS = [
    "anthropic.com",
    "janestreet.com",
    "uber.com",
    "figma.com",
    "microsoft.com",
    "actively.ai",
    "recruiter",
    "interview",
]

# Urgent keywords in email subjects
URGENT_KEYWORDS = [
    "urgent",
    "action required",
    "deadline",
    "interview",
    "offer",
    "final round",
    "decision",
]


def run_command(cmd: list[str], timeout: int = 30) -> tuple[str, bool]:
    """Run a shell command and return (output, success)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip(), True
        return result.stderr.strip(), False
    except subprocess.TimeoutExpired:
        return "Command timed out", False
    except Exception as e:
        return str(e), False


def get_calendar_events() -> dict:
    """Fetch today's calendar events."""
    today = datetime.now()
    start = today.replace(hour=0, minute=0, second=0).isoformat()
    end = today.replace(hour=23, minute=59, second=59).isoformat()
    
    cmd = [
        "gog", "calendar", "events", "primary",
        "--from", start,
        "--to", end,
        "--json",
        "--account", GOG_ACCOUNT,
    ]
    
    output, success = run_command(cmd)
    
    if not success:
        # Check for OAuth errors specifically
        if "invalid_grant" in output or "oauth2" in output.lower():
            return {"error": "OAuth token expired - run: gog auth add " + GOG_ACCOUNT, "events": [], "needs_reauth": True}
        return {"error": output, "events": []}
    
    try:
        events = json.loads(output) if output else []
        # Sort by start time
        events.sort(key=lambda e: e.get("start", {}).get("dateTime", ""))
        return {"events": events, "count": len(events)}
    except json.JSONDecodeError:
        return {"error": "Failed to parse calendar JSON", "events": []}


def get_urgent_emails() -> dict:
    """Fetch emails from last 24h, prioritize urgent ones."""
    # Search for emails from last 24h
    cmd = [
        "gog", "gmail", "messages", "search",
        "newer_than:1d in:inbox",
        "--max", "25",
        "--json",
        "--account", GOG_ACCOUNT,
    ]
    
    output, success = run_command(cmd, timeout=45)
    
    if not success:
        # Check for OAuth errors specifically
        if "invalid_grant" in output or "oauth2" in output.lower():
            return {"error": "OAuth token expired - run: gog auth add " + GOG_ACCOUNT, "emails": [], "urgent": [], "priority": [], "needs_reauth": True}
        return {"error": output, "emails": [], "urgent": [], "priority": []}
    
    try:
        emails = json.loads(output) if output else []
    except json.JSONDecodeError:
        return {"error": "Failed to parse email JSON", "emails": [], "urgent": []}
    
    # Categorize emails
    urgent = []
    priority = []
    regular = []
    
    for email in emails:
        subject = email.get("subject", "").lower()
        sender = email.get("from", "").lower()
        
        # Check if urgent
        is_urgent = any(kw in subject for kw in URGENT_KEYWORDS)
        is_priority = any(s in sender for s in PRIORITY_SENDERS)
        
        if is_urgent:
            urgent.append(email)
        elif is_priority:
            priority.append(email)
        else:
            regular.append(email)
    
    return {
        "urgent": urgent,
        "priority": priority,
        "regular": regular[:5],  # Cap regular at 5
        "total_count": len(emails),
    }


def get_todos() -> dict:
    """Parse TODO.md for high priority and recurring tasks."""
    if not TODO_FILE.exists():
        return {"error": "TODO.md not found", "tasks": []}
    
    content = TODO_FILE.read_text()
    
    tasks = {
        "high_priority": [],
        "recurring": [],
        "scheduled": [],
    }
    
    current_section = None
    
    for line in content.split("\n"):
        # Detect sections
        if "### High Priority" in line:
            current_section = "high_priority"
        elif "### Scheduled" in line:
            current_section = "scheduled"
        elif "### Daily/Recurring" in line:
            current_section = "recurring"
        elif line.startswith("## "):
            current_section = None
        
        # Parse task lines
        if current_section and line.strip().startswith("- [ ]"):
            task_text = line.strip()[5:].strip()  # Remove "- [ ]"
            # Extract task name (before pipes or other metadata)
            task_match = re.match(r"\*\*(.+?)\*\*", task_text)
            if task_match:
                task_name = task_match.group(1)
                tasks[current_section].append({
                    "name": task_name,
                    "full": task_text,
                })
    
    return tasks


def get_day_context() -> dict:
    """Get relevant context for the day."""
    today = datetime.now()
    day_name = today.strftime("%A")
    date_str = today.strftime("%B %d, %Y")
    
    context = {
        "day": day_name,
        "date": date_str,
        "is_weekend": day_name in ["Saturday", "Sunday"],
        "greeting_time": "morning" if today.hour < 12 else "afternoon" if today.hour < 17 else "evening",
    }
    
    # Check yesterday's memory file for continuity
    yesterday = today - timedelta(days=1)
    yesterday_file = MEMORY_DIR / f"{yesterday.strftime('%Y-%m-%d')}.md"
    
    if yesterday_file.exists():
        content = yesterday_file.read_text()
        # Look for "For Tomorrow" or similar sections
        if "tomorrow" in content.lower():
            context["has_yesterday_notes"] = True
    
    return context


def format_briefing(calendar: dict, emails: dict, todos: dict, context: dict) -> str:
    """Format all data into a readable briefing."""
    lines = []
    
    # Header
    lines.append(f"☀️ **Good {context['greeting_time']}, Kartik!**")
    lines.append(f"It's {context['day']}, {context['date']}.")
    lines.append("")
    
    # Calendar section
    lines.append("📅 **Today's Calendar**")
    if "error" in calendar:
        lines.append(f"  ⚠️ Couldn't fetch calendar: {calendar['error']}")
    elif not calendar.get("events"):
        lines.append("  No meetings scheduled - clear day!")
    else:
        for event in calendar["events"]:
            start = event.get("start", {})
            time_str = ""
            if "dateTime" in start:
                time = datetime.fromisoformat(start["dateTime"].replace("Z", "+00:00"))
                time_str = time.strftime("%I:%M %p")
            summary = event.get("summary", "Untitled event")
            lines.append(f"  • {time_str}: {summary}")
    lines.append("")
    
    # Email section
    lines.append("📧 **Email Summary**")
    if "error" in emails:
        lines.append(f"  ⚠️ Couldn't fetch emails: {emails['error']}")
    else:
        if emails.get("urgent"):
            lines.append("  🔴 **Urgent:**")
            for email in emails["urgent"]:
                lines.append(f"    • {email.get('from', 'Unknown')}: {email.get('subject', 'No subject')}")
        
        if emails.get("priority"):
            lines.append("  🟡 **Priority (job-related):**")
            for email in emails["priority"][:3]:  # Cap at 3
                lines.append(f"    • {email.get('from', 'Unknown')}: {email.get('subject', 'No subject')}")
        
        if not emails.get("urgent") and not emails.get("priority"):
            lines.append("  No urgent or priority emails.")
        
        lines.append(f"  ({emails.get('total_count', 0)} total emails in last 24h)")
    lines.append("")
    
    # TODOs section
    lines.append("✅ **Tasks for Today**")
    if "error" in todos:
        lines.append(f"  ⚠️ Couldn't read TODOs: {todos['error']}")
    else:
        if todos.get("high_priority"):
            lines.append("  **High Priority:**")
            for task in todos["high_priority"]:
                lines.append(f"    • {task['name']}")
        
        if todos.get("recurring"):
            lines.append("  **Daily Reminders:**")
            for task in todos["recurring"]:
                lines.append(f"    • {task['name']}")
        
        if not todos.get("high_priority") and not todos.get("recurring"):
            lines.append("  No high-priority tasks pending.")
    lines.append("")
    
    # Weekend note
    if context.get("is_weekend"):
        lines.append("🌴 It's the weekend - take it easy if you want!")
    
    return "\n".join(lines)


def format_json(calendar: dict, emails: dict, todos: dict, context: dict) -> str:
    """Output as JSON for programmatic use."""
    return json.dumps({
        "generated_at": datetime.now().isoformat(),
        "context": context,
        "calendar": calendar,
        "emails": emails,
        "todos": todos,
    }, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Generate morning briefing")
    parser.add_argument("--calendar", action="store_true", help="Calendar only")
    parser.add_argument("--email", action="store_true", help="Email only")
    parser.add_argument("--todos", action="store_true", help="TODOs only")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    # Get context
    context = get_day_context()
    
    # Selective fetching
    calendar = get_calendar_events() if not (args.email or args.todos) else {}
    emails = get_urgent_emails() if not (args.calendar or args.todos) else {}
    todos = get_todos() if not (args.calendar or args.email) else {}
    
    # Output
    if args.json:
        print(format_json(calendar, emails, todos, context))
    else:
        print(format_briefing(calendar, emails, todos, context))


if __name__ == "__main__":
    main()
