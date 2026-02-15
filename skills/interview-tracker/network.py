#!/usr/bin/env python3
"""
Networking Tracker — Track professional contacts and follow-ups.

Usage:
    python3 network.py list [--needs-followup]
    python3 network.py add NAME [--company COMPANY] [--role ROLE] [--email EMAIL] [--linkedin URL] [--notes NOTE]
    python3 network.py log NAME NOTE
    python3 network.py followup NAME [--in-days DAYS]
    python3 network.py get NAME

Author: Limen
Created: 2026-02-15 01:40 AM (nightly autonomous session)
"""

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
DATA_DIR = WORKSPACE / "job-search"
DATA_FILE = DATA_DIR / "network.json"

def ensure_data_file():
    """Create data directory and file if they don't exist."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not DATA_FILE.exists():
        with open(DATA_FILE, 'w') as f:
            json.dump({"contacts": []}, f)

def load_data():
    """Load contacts from JSON file."""
    ensure_data_file()
    with open(DATA_FILE, 'r') as f:
        return json.load(f)

def save_data(data):
    """Save contacts to JSON file."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def find_contact(data, name):
    """Find contact by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for i, contact in enumerate(data["contacts"]):
        if name_lower in contact.get("name", "").lower():
            return i, contact
    return -1, None

def format_date(date_str):
    """Format date for display."""
    if not date_str:
        return "N/A"
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%b %d")
    except:
        return date_str

def days_since(date_str):
    """Calculate days since a date."""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str).replace(tzinfo=None)
        return (datetime.now() - dt).days
    except:
        return None

def days_until(date_str):
    """Calculate days until a date."""
    if not date_str:
        return None
    try:
        dt = datetime.fromisoformat(date_str).replace(tzinfo=None)
        return (dt - datetime.now()).days
    except:
        return None

def cmd_list(args):
    """List all contacts."""
    data = load_data()
    contacts = data.get("contacts", [])
    
    if not contacts:
        print("No contacts tracked yet.")
        print("\nAdd one with: python3 network.py add \"Name\" --company \"Company\"")
        return
    
    # Filter for needs follow-up
    if args.needs_followup:
        contacts = [c for c in contacts if c.get("followup_date")]
        contacts = [c for c in contacts if days_until(c.get("followup_date", "")) is not None and days_until(c["followup_date"]) <= 0]
    
    # Sort by last contact date (most recent first)
    contacts = sorted(contacts, key=lambda c: c.get("last_contact", ""), reverse=True)
    
    print(f"\n👥 Contacts ({len(contacts)})")
    print("=" * 50)
    
    for contact in contacts:
        name = contact.get("name", "Unknown")
        company = contact.get("company", "")
        role = contact.get("role", "")
        last_contact = contact.get("last_contact")
        followup = contact.get("followup_date")
        
        title = name
        if company:
            title += f" @ {company}"
        if role:
            title += f" ({role})"
        
        print(f"\n• {title}")
        
        if last_contact:
            days = days_since(last_contact)
            if days is not None:
                if days == 0:
                    print(f"  Last contact: Today")
                elif days == 1:
                    print(f"  Last contact: Yesterday")
                else:
                    print(f"  Last contact: {days} days ago")
        
        if followup:
            days = days_until(followup)
            if days is not None:
                if days < 0:
                    print(f"  ⚠️ Follow-up overdue by {-days} days")
                elif days == 0:
                    print(f"  🔥 Follow-up due TODAY")
                else:
                    print(f"  📅 Follow-up in {days} days")
    
    print()

def cmd_add(args):
    """Add a new contact."""
    data = load_data()
    
    idx, existing = find_contact(data, args.name)
    if existing:
        print(f"❌ Contact '{existing['name']}' already exists!")
        return
    
    now = datetime.now().isoformat()
    
    contact = {
        "name": args.name,
        "company": args.company,
        "role": args.role,
        "email": args.email,
        "linkedin": args.linkedin,
        "notes": [{"text": args.notes, "date": now}] if args.notes else [],
        "added": now,
        "last_contact": now,
    }
    
    data["contacts"].append(contact)
    save_data(data)
    
    print(f"✅ Added contact: {args.name}")
    if args.company:
        print(f"   Company: {args.company}")
    if args.role:
        print(f"   Role: {args.role}")

def cmd_log(args):
    """Log an interaction with a contact."""
    data = load_data()
    idx, contact = find_contact(data, args.name)
    
    if not contact:
        print(f"❌ No contact found matching '{args.name}'")
        return
    
    now = datetime.now().isoformat()
    
    if "notes" not in contact:
        contact["notes"] = []
    
    contact["notes"].append({"text": args.note, "date": now})
    contact["last_contact"] = now
    
    # Clear followup if set
    if contact.get("followup_date"):
        del contact["followup_date"]
    
    data["contacts"][idx] = contact
    save_data(data)
    
    print(f"✅ Logged interaction with {contact['name']}:")
    print(f"   \"{args.note}\"")

def cmd_followup(args):
    """Set a follow-up reminder for a contact."""
    data = load_data()
    idx, contact = find_contact(data, args.name)
    
    if not contact:
        print(f"❌ No contact found matching '{args.name}'")
        return
    
    followup_date = datetime.now() + timedelta(days=args.in_days)
    contact["followup_date"] = followup_date.isoformat()
    
    data["contacts"][idx] = contact
    save_data(data)
    
    print(f"✅ Set follow-up for {contact['name']}")
    print(f"   Reminder in {args.in_days} days ({followup_date.strftime('%b %d')})")

def cmd_get(args):
    """Get detailed info about a contact."""
    data = load_data()
    idx, contact = find_contact(data, args.name)
    
    if not contact:
        print(f"❌ No contact found matching '{args.name}'")
        return
    
    print(f"\n👤 {contact['name']}")
    print("=" * 40)
    
    if contact.get("company"):
        print(f"Company: {contact['company']}")
    if contact.get("role"):
        print(f"Role: {contact['role']}")
    if contact.get("email"):
        print(f"Email: {contact['email']}")
    if contact.get("linkedin"):
        print(f"LinkedIn: {contact['linkedin']}")
    
    if contact.get("last_contact"):
        print(f"\nLast contact: {format_date(contact['last_contact'])}")
    
    if contact.get("followup_date"):
        days = days_until(contact["followup_date"])
        if days is not None and days <= 0:
            print(f"⚠️ Follow-up OVERDUE")
        else:
            print(f"Follow-up: {format_date(contact['followup_date'])}")
    
    if contact.get("notes"):
        print(f"\n📝 Notes:")
        for note in contact["notes"][-5:]:  # Last 5 notes
            print(f"   [{format_date(note.get('date'))}] {note['text']}")
    
    print()

def main():
    parser = argparse.ArgumentParser(description="Track professional contacts")
    subparsers = parser.add_subparsers(dest="command")
    
    # list
    list_parser = subparsers.add_parser("list", help="List contacts")
    list_parser.add_argument("--needs-followup", action="store_true", help="Only show contacts needing follow-up")
    
    # add
    add_parser = subparsers.add_parser("add", help="Add a contact")
    add_parser.add_argument("name", help="Contact name")
    add_parser.add_argument("--company", help="Company name")
    add_parser.add_argument("--role", help="Role/title")
    add_parser.add_argument("--email", help="Email address")
    add_parser.add_argument("--linkedin", help="LinkedIn URL")
    add_parser.add_argument("--notes", help="Initial notes")
    
    # log
    log_parser = subparsers.add_parser("log", help="Log interaction")
    log_parser.add_argument("name", help="Contact name")
    log_parser.add_argument("note", help="Note about interaction")
    
    # followup
    followup_parser = subparsers.add_parser("followup", help="Set follow-up reminder")
    followup_parser.add_argument("name", help="Contact name")
    followup_parser.add_argument("--in-days", type=int, default=7, help="Days until follow-up")
    
    # get
    get_parser = subparsers.add_parser("get", help="Get contact details")
    get_parser.add_argument("name", help="Contact name")
    
    args = parser.parse_args()
    
    if args.command == "list":
        cmd_list(args)
    elif args.command == "add":
        cmd_add(args)
    elif args.command == "log":
        cmd_log(args)
    elif args.command == "followup":
        cmd_followup(args)
    elif args.command == "get":
        cmd_get(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
