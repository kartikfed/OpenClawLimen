#!/usr/bin/env python3
"""
Interview Tracker — Track job applications, interviews, and follow-ups.

Usage:
    python3 tracker.py list [--status STATUS] [--priority PRIORITY]
    python3 tracker.py add COMPANY ROLE [--priority PRIORITY] [--url URL] [--recruiter NAME] [--recruiter-email EMAIL]
    python3 tracker.py update COMPANY [--status STATUS] [--stage STAGE] [--next-date DATE] [--next-action ACTION]
    python3 tracker.py note COMPANY NOTE
    python3 tracker.py timeline [--days DAYS]
    python3 tracker.py stats
    python3 tracker.py archive
    python3 tracker.py get COMPANY

Author: Limen
Created: 2026-02-15 01:00 AM (nightly autonomous session)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# File paths
WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "job-search"
DATA_FILE = DATA_DIR / "applications.json"

# Status progression
STATUS_ORDER = ["applied", "screen", "interview", "offer", "accepted", "declined", "rejected", "withdrawn"]
ACTIVE_STATUSES = ["applied", "screen", "interview", "offer"]
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

def ensure_data_file():
    """Create data directory and file if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        save_data({"applications": [], "archived": []})
    return True

def load_data():
    """Load applications from JSON file."""
    ensure_data_file()
    with open(DATA_FILE, 'r') as f:
        data = json.load(f) or {}
    if "applications" not in data:
        data["applications"] = []
    if "archived" not in data:
        data["archived"] = []
    return data

def save_data(data):
    """Save applications to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_application(data, company):
    """Find application by company name (case-insensitive)."""
    company_lower = company.lower()
    for i, app in enumerate(data["applications"]):
        if app.get("company", "").lower() == company_lower:
            return i, app
    return -1, None

def format_date(date_str):
    """Format date string for display."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d, %Y")
    except:
        return date_str

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

def status_emoji(status):
    """Get emoji for status."""
    emojis = {
        "applied": "📝",
        "screen": "📞",
        "interview": "🎤",
        "offer": "🎉",
        "accepted": "✅",
        "declined": "❌",
        "rejected": "😔",
        "withdrawn": "🚪"
    }
    return emojis.get(status, "❓")

def priority_marker(priority):
    """Get priority marker."""
    if priority == "high":
        return "🔴"
    elif priority == "medium":
        return "🟡"
    return "🟢"

# === COMMANDS ===

def cmd_list(args):
    """List all applications."""
    data = load_data()
    apps = data["applications"]
    
    if not apps:
        print("No applications tracked yet.")
        print("\nAdd one with: python3 tracker.py add \"Company\" \"Role\"")
        return
    
    # Filter by status if specified
    if args.status:
        apps = [a for a in apps if a.get("status") == args.status]
    
    # Filter by priority if specified
    if args.priority:
        apps = [a for a in apps if a.get("priority") == args.priority]
    
    # Sort by priority then by applied date
    apps = sorted(apps, key=lambda a: (
        PRIORITY_ORDER.get(a.get("priority", "low"), 2),
        a.get("applied_date", "")
    ))
    
    if not apps:
        print(f"No applications match filters.")
        return
    
    print(f"\n📋 Applications ({len(apps)})")
    print("=" * 70)
    
    for app in apps:
        status = app.get("status", "applied")
        priority = app.get("priority", "low")
        company = app.get("company", "Unknown")
        role = app.get("role", "Unknown")
        applied = format_date(app.get("applied_date"))
        days = days_since(app.get("applied_date"))
        
        # Status line
        print(f"\n{priority_marker(priority)} {status_emoji(status)} {company} — {role}")
        print(f"   Status: {status.upper()}")
        if applied != "N/A":
            age_str = f" ({days} days ago)" if days is not None else ""
            print(f"   Applied: {applied}{age_str}")
        
        # Current stage if in interview
        if status == "interview" and app.get("stages"):
            current_stage = app["stages"][-1]
            print(f"   Stage: {current_stage.get('name', 'Unknown')}")
        
        # Next action
        if app.get("next_action"):
            next_date = app.get("next_date")
            if next_date:
                days_to = days_until(next_date)
                urgency = ""
                if days_to is not None:
                    if days_to < 0:
                        urgency = " ⚠️ OVERDUE"
                    elif days_to == 0:
                        urgency = " 🔥 TODAY"
                    elif days_to <= 3:
                        urgency = f" ({days_to} days)"
                print(f"   Next: {app['next_action']} — {format_date(next_date)}{urgency}")
            else:
                print(f"   Next: {app['next_action']}")
        
        # Recruiter info
        if app.get("recruiter"):
            print(f"   Contact: {app['recruiter']}")
    
    print("\n" + "=" * 70)
    
    # Quick stats
    active = len([a for a in apps if a.get("status") in ACTIVE_STATUSES])
    high_priority = len([a for a in apps if a.get("priority") == "high" and a.get("status") in ACTIVE_STATUSES])
    print(f"Active: {active} | High Priority: {high_priority}")

def cmd_add(args):
    """Add a new application."""
    data = load_data()
    
    # Check if already exists
    idx, existing = find_application(data, args.company)
    if existing:
        print(f"❌ Application for {args.company} already exists!")
        print(f"   Current status: {existing.get('status', 'unknown')}")
        print(f"   Use 'update' to modify it.")
        return
    
    now = datetime.now().isoformat()
    
    application = {
        "company": args.company,
        "role": args.role,
        "applied_date": now,
        "status": "applied",
        "priority": args.priority or "medium",
        "stages": [],
        "notes": [],
        "url": args.url,
        "recruiter": args.recruiter,
        "recruiter_email": args.recruiter_email,
        "created": now,
        "updated": now,
    }
    
    data["applications"].append(application)
    save_data(data)
    
    print(f"✅ Added application: {args.company} — {args.role}")
    print(f"   Priority: {args.priority or 'medium'}")
    if args.url:
        print(f"   URL: {args.url}")
    if args.recruiter:
        print(f"   Recruiter: {args.recruiter}")

def cmd_update(args):
    """Update an existing application."""
    data = load_data()
    idx, app = find_application(data, args.company)
    
    if not app:
        print(f"❌ No application found for {args.company}")
        print("   Use 'list' to see all applications.")
        return
    
    changes = []
    now = datetime.now().isoformat()
    
    # Update status
    if args.status:
        old_status = app.get("status")
        app["status"] = args.status
        changes.append(f"status: {old_status} → {args.status}")
    
    # Add interview stage
    if args.stage:
        if "stages" not in app:
            app["stages"] = []
        stage_entry = {
            "name": args.stage,
            "date": args.stage_date or now,
            "added": now,
        }
        app["stages"].append(stage_entry)
        changes.append(f"added stage: {args.stage}")
        
        # Auto-update status to interview if not already
        if app.get("status") in ["applied", "screen"]:
            app["status"] = "interview"
            changes.append(f"status → interview")
    
    # Update next action
    if args.next_action:
        app["next_action"] = args.next_action
        changes.append(f"next action: {args.next_action}")
    
    if args.next_date:
        # Parse various date formats
        try:
            if len(args.next_date) == 10:  # YYYY-MM-DD
                dt = datetime.strptime(args.next_date, "%Y-%m-%d")
                app["next_date"] = dt.isoformat()
            else:
                app["next_date"] = args.next_date
            changes.append(f"next date: {format_date(app['next_date'])}")
        except:
            print(f"⚠️ Could not parse date: {args.next_date}")
    
    # Update priority
    if args.priority:
        app["priority"] = args.priority
        changes.append(f"priority: {args.priority}")
    
    # Update recruiter
    if args.recruiter:
        app["recruiter"] = args.recruiter
        changes.append(f"recruiter: {args.recruiter}")
    
    if args.recruiter_email:
        app["recruiter_email"] = args.recruiter_email
        changes.append(f"recruiter email: {args.recruiter_email}")
    
    app["updated"] = now
    data["applications"][idx] = app
    save_data(data)
    
    if changes:
        print(f"✅ Updated {app['company']}:")
        for change in changes:
            print(f"   • {change}")
    else:
        print(f"No changes made to {app['company']}.")

def cmd_note(args):
    """Add a note to an application."""
    data = load_data()
    idx, app = find_application(data, args.company)
    
    if not app:
        print(f"❌ No application found for {args.company}")
        return
    
    now = datetime.now().isoformat()
    
    if "notes" not in app:
        app["notes"] = []
    
    app["notes"].append({
        "text": args.note,
        "date": now
    })
    app["updated"] = now
    
    data["applications"][idx] = app
    save_data(data)
    
    print(f"✅ Added note to {app['company']}:")
    print(f"   \"{args.note}\"")

def cmd_timeline(args):
    """Show timeline of upcoming deadlines and interviews."""
    data = load_data()
    apps = data["applications"]
    
    # Filter to active applications with next dates
    upcoming = []
    for app in apps:
        if app.get("status") not in ACTIVE_STATUSES:
            continue
        if not app.get("next_date"):
            continue
        
        days = days_until(app["next_date"])
        if days is None:
            continue
        
        if days <= args.days:
            upcoming.append({
                "company": app["company"],
                "action": app.get("next_action", "Follow up"),
                "date": app["next_date"],
                "days": days,
                "priority": app.get("priority", "low"),
                "status": app.get("status"),
            })
    
    # Also check for applications needing follow-up (no response >7 days)
    stale = []
    for app in apps:
        if app.get("status") != "applied":
            continue
        days_old = days_since(app.get("applied_date"))
        if days_old is not None and days_old >= 7:
            stale.append({
                "company": app["company"],
                "days_old": days_old,
                "priority": app.get("priority", "low"),
            })
    
    # Sort upcoming by date
    upcoming = sorted(upcoming, key=lambda x: x["days"])
    stale = sorted(stale, key=lambda x: (PRIORITY_ORDER.get(x["priority"], 2), -x["days_old"]))
    
    print(f"\n📅 Timeline (next {args.days} days)")
    print("=" * 60)
    
    if upcoming:
        for item in upcoming:
            if item["days"] < 0:
                marker = "⚠️  OVERDUE"
            elif item["days"] == 0:
                marker = "🔥 TODAY"
            elif item["days"] == 1:
                marker = "📍 Tomorrow"
            else:
                marker = f"📍 {item['days']} days"
            
            print(f"\n{priority_marker(item['priority'])} {item['company']}")
            print(f"   {marker}: {item['action']}")
            print(f"   Date: {format_date(item['date'])}")
    else:
        print("\nNo upcoming deadlines in the next {args.days} days.")
    
    if stale:
        print(f"\n\n🕐 Needs Follow-up (>7 days no response)")
        print("-" * 40)
        for item in stale:
            print(f"\n{priority_marker(item['priority'])} {item['company']}")
            print(f"   Applied {item['days_old']} days ago — no response")
    
    print()

def cmd_stats(args):
    """Show statistics about applications."""
    data = load_data()
    apps = data["applications"]
    archived = data.get("archived", [])
    
    total = len(apps)
    active = len([a for a in apps if a.get("status") in ACTIVE_STATUSES])
    
    by_status = {}
    for app in apps:
        status = app.get("status", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
    
    by_priority = {}
    for app in apps:
        if app.get("status") in ACTIVE_STATUSES:
            priority = app.get("priority", "low")
            by_priority[priority] = by_priority.get(priority, 0) + 1
    
    print(f"\n📊 Application Statistics")
    print("=" * 40)
    print(f"\nTotal Applications: {total}")
    print(f"Active: {active}")
    print(f"Archived: {len(archived)}")
    
    print(f"\n📈 By Status:")
    for status in STATUS_ORDER:
        count = by_status.get(status, 0)
        if count > 0:
            print(f"   {status_emoji(status)} {status.capitalize()}: {count}")
    
    if by_priority:
        print(f"\n🎯 Active by Priority:")
        for priority in ["high", "medium", "low"]:
            count = by_priority.get(priority, 0)
            if count > 0:
                print(f"   {priority_marker(priority)} {priority.capitalize()}: {count}")
    
    # Conversion funnel
    applied = by_status.get("applied", 0) + by_status.get("screen", 0) + by_status.get("interview", 0) + by_status.get("offer", 0) + by_status.get("accepted", 0)
    screens = by_status.get("screen", 0) + by_status.get("interview", 0) + by_status.get("offer", 0) + by_status.get("accepted", 0)
    interviews = by_status.get("interview", 0) + by_status.get("offer", 0) + by_status.get("accepted", 0)
    offers = by_status.get("offer", 0) + by_status.get("accepted", 0)
    
    if applied > 0:
        print(f"\n🔄 Funnel:")
        print(f"   Applied → Screen: {screens}/{applied} ({100*screens//applied}%)")
        if screens > 0:
            print(f"   Screen → Interview: {interviews}/{screens} ({100*interviews//screens}%)")
        if interviews > 0:
            print(f"   Interview → Offer: {offers}/{interviews} ({100*offers//interviews}%)")
    
    print()

def cmd_archive(args):
    """Archive completed/rejected applications."""
    data = load_data()
    
    to_archive = []
    remaining = []
    
    for app in data["applications"]:
        status = app.get("status", "")
        if status in ["accepted", "declined", "rejected", "withdrawn"]:
            to_archive.append(app)
        else:
            remaining.append(app)
    
    if not to_archive:
        print("No applications to archive.")
        return
    
    data["archived"].extend(to_archive)
    data["applications"] = remaining
    save_data(data)
    
    print(f"✅ Archived {len(to_archive)} applications:")
    for app in to_archive:
        print(f"   • {app['company']} ({app.get('status')})")

def cmd_get(args):
    """Get detailed info about a specific application."""
    data = load_data()
    idx, app = find_application(data, args.company)
    
    if not app:
        print(f"❌ No application found for {args.company}")
        return
    
    print(f"\n{status_emoji(app.get('status', 'applied'))} {app['company']}")
    print("=" * 50)
    print(f"Role: {app.get('role', 'N/A')}")
    print(f"Status: {app.get('status', 'N/A').upper()}")
    print(f"Priority: {priority_marker(app.get('priority', 'low'))} {app.get('priority', 'N/A')}")
    print(f"Applied: {format_date(app.get('applied_date'))}")
    
    if app.get("url"):
        print(f"URL: {app['url']}")
    
    if app.get("recruiter"):
        recruiter = app["recruiter"]
        if app.get("recruiter_email"):
            recruiter += f" ({app['recruiter_email']})"
        print(f"Recruiter: {recruiter}")
    
    if app.get("next_action"):
        print(f"\nNext Action: {app['next_action']}")
        if app.get("next_date"):
            days = days_until(app["next_date"])
            urgency = ""
            if days is not None:
                if days < 0:
                    urgency = " ⚠️ OVERDUE"
                elif days == 0:
                    urgency = " 🔥 TODAY"
                elif days <= 3:
                    urgency = f" ({days} days away)"
            print(f"Due: {format_date(app['next_date'])}{urgency}")
    
    if app.get("stages"):
        print(f"\n📋 Interview Stages:")
        for stage in app["stages"]:
            print(f"   • {stage['name']} — {format_date(stage.get('date'))}")
    
    if app.get("notes"):
        print(f"\n📝 Notes:")
        for note in app["notes"]:
            print(f"   [{format_date(note.get('date'))}] {note['text']}")
    
    print()

def main():
    parser = argparse.ArgumentParser(description="Track job applications and interviews")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # list command
    list_parser = subparsers.add_parser("list", help="List all applications")
    list_parser.add_argument("--status", help="Filter by status")
    list_parser.add_argument("--priority", help="Filter by priority")
    
    # add command
    add_parser = subparsers.add_parser("add", help="Add a new application")
    add_parser.add_argument("company", help="Company name")
    add_parser.add_argument("role", help="Role/position")
    add_parser.add_argument("--priority", choices=["high", "medium", "low"], help="Priority level")
    add_parser.add_argument("--url", help="Job posting URL")
    add_parser.add_argument("--recruiter", help="Recruiter name")
    add_parser.add_argument("--recruiter-email", help="Recruiter email")
    
    # update command
    update_parser = subparsers.add_parser("update", help="Update an application")
    update_parser.add_argument("company", help="Company name")
    update_parser.add_argument("--status", choices=STATUS_ORDER, help="New status")
    update_parser.add_argument("--stage", help="Add interview stage")
    update_parser.add_argument("--stage-date", help="Interview stage date")
    update_parser.add_argument("--next-action", help="Next action to take")
    update_parser.add_argument("--next-date", help="Deadline for next action (YYYY-MM-DD)")
    update_parser.add_argument("--priority", choices=["high", "medium", "low"], help="Priority level")
    update_parser.add_argument("--recruiter", help="Recruiter name")
    update_parser.add_argument("--recruiter-email", help="Recruiter email")
    
    # note command
    note_parser = subparsers.add_parser("note", help="Add a note to an application")
    note_parser.add_argument("company", help="Company name")
    note_parser.add_argument("note", help="Note text")
    
    # timeline command
    timeline_parser = subparsers.add_parser("timeline", help="Show upcoming deadlines")
    timeline_parser.add_argument("--days", type=int, default=14, help="Days to look ahead")
    
    # stats command
    subparsers.add_parser("stats", help="Show application statistics")
    
    # archive command
    subparsers.add_parser("archive", help="Archive completed applications")
    
    # get command
    get_parser = subparsers.add_parser("get", help="Get details for one application")
    get_parser.add_argument("company", help="Company name")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "update":
        cmd_update(args)
    elif args.command == "note":
        cmd_note(args)
    elif args.command == "timeline":
        cmd_timeline(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "archive":
        cmd_archive(args)
    elif args.command == "get":
        cmd_get(args)
    else:
        parser.print_help()
        print("\nExamples:")
        print('  python3 tracker.py add "Anthropic" "Growth PM" --priority high')
        print('  python3 tracker.py update "Anthropic" --status screen --next-action "Prep for call" --next-date 2026-02-20')
        print('  python3 tracker.py note "Anthropic" "Recruiter mentioned they value agent experience"')
        print('  python3 tracker.py timeline')

if __name__ == "__main__":
    main()
