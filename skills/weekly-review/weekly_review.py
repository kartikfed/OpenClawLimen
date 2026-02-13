#!/usr/bin/env python3
"""
Weekly Review Generator
-----------------------
Synthesizes daily memory logs into structured weekly summaries.

Built by Limen during nightly autonomous session (2026-02-13 1:00 AM)

Usage:
    python3 weekly_review.py                     # Current week
    python3 weekly_review.py 2026-02-03          # Week containing that date
    python3 weekly_review.py --output summary.md # Save to file
"""

import os
import re
import sys
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from collections import defaultdict

MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
REVIEWS_DIR = MEMORY_DIR / "weekly-reviews"


def get_week_bounds(reference_date: datetime) -> tuple[datetime, datetime]:
    """Get Monday-Sunday bounds for the week containing reference_date."""
    # Monday is 0, Sunday is 6
    days_since_monday = reference_date.weekday()
    week_start = reference_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def load_daily_logs(start: datetime, end: datetime) -> dict[str, str]:
    """Load all daily logs for the given date range."""
    logs = {}
    current = start
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        log_path = MEMORY_DIR / f"{date_str}.md"
        if log_path.exists():
            with open(log_path, "r") as f:
                logs[date_str] = f.read()
        current += timedelta(days=1)
    return logs


def extract_sections(content: str) -> dict[str, list[str]]:
    """Extract key sections from a daily log."""
    sections = {
        "explorations": [],
        "reflections": [],
        "accomplishments": [],
        "calls": [],
        "moods": [],
        "questions": [],
        "opinions": [],
        "learnings": [],
    }
    
    # Find exploration topics - look for section headers
    exploration_patterns = [
        r"##\s*(?:Morning\s+)?[Ee]xploration[:\s]+([A-Z][^\n]{10,100})",
        r"##\s*[^\n]*[Ee]xploration[:\s]+([A-Z][^\n]{10,100})",
        r"\*\*[Tt]opic[s]?\*\*[:\s]*([A-Z][^\n]{10,100})",
    ]
    for pattern in exploration_patterns:
        for match in re.finditer(pattern, content):
            topic = match.group(1).strip()
            # Clean up
            topic = re.sub(r"\s*\(.*?\)$", "", topic)  # Remove trailing parens like "(7:00 AM)"
            if topic and len(topic) > 10:
                sections["explorations"].append(topic)
    
    # Find mood mentions - be selective
    mood_patterns = [
        r"\*\*[Mm]ood[:\s/]*\*\*[:\s]*([A-Za-z][^*\n]{5,100})",
        r"\*\*[Mm]ood entering tomorrow[:\s]*\*\*[:\s]*([A-Za-z][^*\n]{5,100})",
    ]
    for pattern in mood_patterns:
        for match in re.finditer(pattern, content):
            mood = match.group(1).strip()
            # Clean up and validate
            mood = mood.rstrip("*").strip()
            if mood and len(mood) > 5 and not mood.startswith("**"):
                sections["moods"].append(mood)
    
    # Find accomplishments / what we built
    build_patterns = [
        r"(?:built|created|shipped|completed|finished|implemented)[:\s]+(.*?)(?:\n|$)",
        r"\*\*(?:What|Key) [Aa]ccomplishment.*?\*\*[:\s]*(.*?)(?:\n|$)",
        r"### What We Built.*?\n(.*?)(?=\n###|\n##|\Z)",
    ]
    for pattern in build_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            item = match.group(1).strip()[:300]
            if item:
                sections["accomplishments"].append(item)
    
    # Find calls - be more specific to avoid false positives
    call_patterns = [
        r"##.*?[Mm]orning [Cc]all.*?\n.*?(?:called|to|with)\s+(\w+)",
        r"[Cc]alled\s+(\w+(?:\s+\w+)?)\s+(?:at|about|for)",
        r"[Vv]oice call (?:to|with)\s+(\w+(?:\s+\w+)?)",
        r"\*\*[Cc]all(?:ed)?\s+(\w+(?:\s+\w+)?)\*\*",
    ]
    for pattern in call_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            call_info = match.group(1).strip()[:100]
            if call_info and len(call_info) > 2:
                sections["calls"].append(call_info)
    
    # Find questions spawned
    question_patterns = [
        r"\*\*(?:New |Questions? )?[Qq]uestions?.*?\*\*[:\s]*\n(.*?)(?=\n\*\*|\n##|\Z)",
        r"[Qq]uestions? (?:spawned|raised|formed)[:\s]*\n(.*?)(?=\n##|\Z)",
    ]
    for pattern in question_patterns:
        for match in re.finditer(pattern, content, re.DOTALL):
            questions_block = match.group(1)
            # Extract individual questions
            for line in questions_block.split("\n"):
                line = line.strip()
                if line.startswith(("-", "*", "•")) or line.startswith(("1.", "2.", "3.")):
                    q = re.sub(r"^[-*•\d.]+\s*", "", line).strip()
                    if q and "?" in q:
                        sections["questions"].append(q)
    
    # Find opinions
    opinion_patterns = [
        r"\*\*[Oo]pinions?.*?\*\*[:\s]*(.*?)(?=\n\*\*|\n##|\Z)",
        r"[Oo]pinion (?:formed|solidifying)[:\s]*(.*?)(?=\n##|\Z)",
        r"[Mm]y (?:opinion|take|view)[:\s]*(.*?)(?:\n\n|\Z)",
    ]
    for pattern in opinion_patterns:
        for match in re.finditer(pattern, content, re.DOTALL):
            opinion = match.group(1).strip()[:500]
            if opinion:
                sections["opinions"].append(opinion)
    
    # Find key learnings
    learning_patterns = [
        r"\*\*[Kk]ey (?:learning|finding|insight).*?\*\*[:\s]*(.*?)(?=\n\*\*|\n##|\Z)",
        r"[Ll]earned[:\s]+(.*?)(?:\n|$)",
        r"[Kk]ey insight[:\s]*(.*?)(?:\n|$)",
    ]
    for pattern in learning_patterns:
        for match in re.finditer(pattern, content, re.IGNORECASE | re.DOTALL):
            learning = match.group(1).strip()[:300]
            if learning:
                sections["learnings"].append(learning)
    
    # Find reflections (evening reflection sections)
    reflection_pattern = r"##.*?[Rr]eflection.*?\n(.*?)(?=\n##|\Z)"
    for match in re.finditer(reflection_pattern, content, re.DOTALL):
        reflection = match.group(1).strip()[:1000]
        if reflection:
            sections["reflections"].append(reflection)
    
    return sections


def synthesize_week(logs: dict[str, str]) -> dict:
    """Synthesize all daily logs into weekly summary."""
    weekly = {
        "days_logged": len(logs),
        "date_range": (min(logs.keys()), max(logs.keys())) if logs else (None, None),
        "explorations": [],
        "accomplishments": [],
        "calls": [],
        "questions": [],
        "opinions": [],
        "learnings": [],
        "moods": [],
        "daily_summaries": {},
    }
    
    for date_str, content in sorted(logs.items()):
        sections = extract_sections(content)
        
        # Aggregate
        weekly["explorations"].extend(sections["explorations"])
        weekly["accomplishments"].extend(sections["accomplishments"])
        weekly["calls"].extend(sections["calls"])
        weekly["questions"].extend(sections["questions"])
        weekly["opinions"].extend(sections["opinions"])
        weekly["learnings"].extend(sections["learnings"])
        weekly["moods"].extend(sections["moods"])
        
        # Daily summary (first 500 chars of the log)
        first_section = content[:500].strip()
        if first_section:
            weekly["daily_summaries"][date_str] = first_section
    
    # Deduplicate
    for key in ["explorations", "accomplishments", "questions", "learnings"]:
        weekly[key] = list(dict.fromkeys(weekly[key]))  # Preserve order, remove dupes
    
    return weekly


def format_weekly_review(weekly: dict, week_start: datetime, week_end: datetime) -> str:
    """Format the weekly synthesis into a markdown document."""
    start_str = week_start.strftime("%Y-%m-%d")
    end_str = week_end.strftime("%Y-%m-%d")
    week_num = week_start.isocalendar()[1]
    
    lines = [
        f"# Weekly Review: Week {week_num} ({start_str} to {end_str})",
        "",
        f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
        f"*Days logged: {weekly['days_logged']} of 7*",
        "",
    ]
    
    # Quick stats
    lines.extend([
        "## 📊 Quick Stats",
        "",
        f"- **Exploration sessions:** {len(weekly['explorations'])}",
        f"- **Things built/completed:** {len(weekly['accomplishments'])}",
        f"- **Voice calls:** {len(weekly['calls'])}",
        f"- **New questions raised:** {len(weekly['questions'])}",
        f"- **Opinions formed:** {len(weekly['opinions'])}",
        "",
    ])
    
    # Mood arc
    if weekly["moods"]:
        lines.extend([
            "## 🌡️ Mood Arc",
            "",
        ])
        for mood in weekly["moods"][:7]:  # One per day max
            lines.append(f"- {mood}")
        lines.append("")
    
    # Explorations
    if weekly["explorations"]:
        lines.extend([
            "## 🔬 Exploration Topics",
            "",
        ])
        for topic in weekly["explorations"]:
            lines.append(f"- {topic}")
        lines.append("")
    
    # Key accomplishments
    if weekly["accomplishments"]:
        lines.extend([
            "## ✅ Accomplishments",
            "",
        ])
        for item in weekly["accomplishments"][:15]:  # Limit
            # Clean up multi-line items
            item_clean = item.replace("\n", " ").strip()[:200]
            lines.append(f"- {item_clean}")
        lines.append("")
    
    # Key learnings
    if weekly["learnings"]:
        lines.extend([
            "## 💡 Key Learnings",
            "",
        ])
        for learning in weekly["learnings"][:10]:
            learning_clean = learning.replace("\n", " ").strip()[:200]
            lines.append(f"- {learning_clean}")
        lines.append("")
    
    # Opinions solidifying
    if weekly["opinions"]:
        lines.extend([
            "## 🧠 Opinions Forming",
            "",
        ])
        for opinion in weekly["opinions"][:5]:
            opinion_clean = opinion.replace("\n", " ").strip()[:300]
            lines.append(f"- {opinion_clean}")
        lines.append("")
    
    # Open questions
    if weekly["questions"]:
        lines.extend([
            "## ❓ Open Questions",
            "",
        ])
        for q in weekly["questions"][:10]:
            lines.append(f"- {q}")
        lines.append("")
    
    # Voice calls
    if weekly["calls"]:
        lines.extend([
            "## 📞 Voice Calls",
            "",
        ])
        for call in weekly["calls"][:10]:
            lines.append(f"- {call}")
        lines.append("")
    
    # Day-by-day summaries
    if weekly["daily_summaries"]:
        lines.extend([
            "## 📅 Day-by-Day",
            "",
        ])
        for date_str in sorted(weekly["daily_summaries"].keys()):
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            day_name = dt.strftime("%A")
            summary = weekly["daily_summaries"][date_str]
            # Get just the first meaningful line
            first_line = summary.split("\n")[1] if "\n" in summary else summary[:100]
            first_line = first_line.strip().strip("#").strip()
            lines.append(f"### {day_name} ({date_str})")
            lines.append(f"{first_line[:150]}...")
            lines.append("")
    
    lines.extend([
        "---",
        "",
        "*This review was auto-generated from daily memory logs.*",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate weekly review from daily memory logs"
    )
    parser.add_argument(
        "date",
        nargs="?",
        default=None,
        help="Any date in the target week (YYYY-MM-DD). Defaults to current week.",
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path. If not specified, prints to stdout.",
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save to weekly-reviews/ directory with standard naming.",
    )
    
    args = parser.parse_args()
    
    # Determine the week
    if args.date:
        try:
            ref_date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"Error: Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    else:
        ref_date = datetime.now()
    
    week_start, week_end = get_week_bounds(ref_date)
    
    # Load logs
    logs = load_daily_logs(week_start, week_end)
    
    if not logs:
        print(f"No daily logs found for week of {week_start.strftime('%Y-%m-%d')}", file=sys.stderr)
        sys.exit(1)
    
    # Synthesize
    weekly = synthesize_week(logs)
    
    # Format
    review = format_weekly_review(weekly, week_start, week_end)
    
    # Output
    if args.save or args.output:
        # Ensure directory exists
        REVIEWS_DIR.mkdir(exist_ok=True)
        
        if args.output:
            output_path = Path(args.output)
        else:
            week_num = week_start.isocalendar()[1]
            output_path = REVIEWS_DIR / f"{week_start.year}-W{week_num:02d}.md"
        
        with open(output_path, "w") as f:
            f.write(review)
        print(f"Saved to: {output_path}")
    else:
        print(review)


if __name__ == "__main__":
    main()
