#!/usr/bin/env python3
"""
Interview Briefing — Generate morning call summary for job search status.

Usage:
    python3 briefing.py

Returns a formatted summary suitable for voice calls.

Author: Limen
Created: 2026-02-15 01:30 AM (nightly autonomous session)
"""

import json
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_FILE = WORKSPACE / "job-search" / "applications.json"

def days_until(date_str):
    """Calculate days until a date."""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str).replace(tzinfo=None)
        now = datetime.now()
        return (dt - now).days
    except:
        return None

def days_since(date_str):
    """Calculate days since a date."""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str).replace(tzinfo=None)
        now = datetime.now()
        return (now - dt).days
    except:
        return None

def generate_briefing():
    """Generate a spoken-word briefing for job search status."""
    
    if not DATA_FILE.exists():
        return "No job applications tracked yet."
    
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    apps = data.get("applications", [])
    if not apps:
        return "No job applications tracked yet."
    
    # Find key items
    active = [a for a in apps if a.get("status") in ["applied", "screen", "interview", "offer"]]
    high_priority = [a for a in active if a.get("priority") == "high"]
    
    # Find urgent items (deadlines in next 3 days)
    urgent = []
    for app in active:
        if app.get("next_date"):
            days = days_until(app["next_date"])
            if days is not None and days <= 3:
                urgent.append({
                    "company": app["company"],
                    "action": app.get("next_action", "Follow up"),
                    "days": days
                })
    urgent.sort(key=lambda x: x["days"])
    
    # Find stale applications (no movement >7 days)
    stale = []
    for app in apps:
        if app.get("status") == "applied":
            days = days_since(app.get("applied_date"))
            if days is not None and days >= 7:
                stale.append({"company": app["company"], "days": days})
    
    # Build briefing
    parts = []
    
    # Summary
    parts.append(f"You have {len(active)} active applications, {len(high_priority)} high priority.")
    
    # Urgent deadlines
    if urgent:
        parts.append("")
        for item in urgent:
            if item["days"] < 0:
                parts.append(f"OVERDUE: {item['company']} — {item['action']}.")
            elif item["days"] == 0:
                parts.append(f"TODAY: {item['company']} — {item['action']}.")
            elif item["days"] == 1:
                parts.append(f"Tomorrow: {item['company']} — {item['action']}.")
            else:
                parts.append(f"In {item['days']} days: {item['company']} — {item['action']}.")
    
    # Stale applications
    if stale:
        if len(stale) == 1:
            parts.append(f"Heads up: {stale[0]['company']} has had no response in {stale[0]['days']} days.")
        else:
            names = ", ".join([s["company"] for s in stale[:3]])
            parts.append(f"Needs follow-up: {names}. No response in over a week.")
    
    # Interview stages
    in_interview = [a for a in active if a.get("status") == "interview"]
    if in_interview:
        parts.append("")
        parts.append(f"Currently interviewing at: {', '.join([a['company'] for a in in_interview])}.")
    
    return " ".join(parts) if parts else "Job search is on track. No urgent items."

if __name__ == "__main__":
    print(generate_briefing())
