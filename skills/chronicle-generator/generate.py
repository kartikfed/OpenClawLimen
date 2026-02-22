#!/usr/bin/env python3
"""
Chronicle Auto-Generator

Generates Substack-ready chronicle entries from daily memory files,
exploration logs, and deep dives.

Usage:
    python3 generate.py               # Generate from last 7 days
    python3 generate.py --topics      # List potential topics
    python3 generate.py --preview     # Don't save, just print
    python3 generate.py --theme "X"   # Focus on specific theme
"""

import argparse
import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from collections import defaultdict

WORKSPACE = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE / "memory"
DEEP_DIVES_DIR = MEMORY_DIR / "deep-dives"
CHRONICLE_DIR = WORKSPACE / "chronicle"
EXPLORATION_LOG = WORKSPACE / "EXPLORATION-LOG.md"
CURIOSITY_FILE = WORKSPACE / "CURIOSITY.md"


def parse_date(date_str: str) -> datetime:
    """Parse date string."""
    formats = ["%Y-%m-%d", "%m-%d", "%b-%d"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if parsed.year == 1900:
                parsed = parsed.replace(year=datetime.now().year)
            return parsed
        except ValueError:
            continue
    raise ValueError(f"Could not parse date: {date_str}")


def get_memory_files(since: datetime = None, until: datetime = None) -> List[Path]:
    """Get memory files in date range."""
    if since is None:
        since = datetime.now() - timedelta(days=7)
    if until is None:
        until = datetime.now()
    
    files = []
    if MEMORY_DIR.exists():
        for f in MEMORY_DIR.glob("*.md"):
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.name)
            if match:
                try:
                    file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    if since.date() <= file_date.date() <= until.date():
                        files.append(f)
                except ValueError:
                    continue
    return sorted(files)


def get_deep_dives(since: datetime = None, until: datetime = None) -> List[Path]:
    """Get deep dive files in date range."""
    if since is None:
        since = datetime.now() - timedelta(days=7)
    if until is None:
        until = datetime.now()
    
    files = []
    if DEEP_DIVES_DIR.exists():
        for f in DEEP_DIVES_DIR.glob("*.md"):
            match = re.match(r"(\d{4}-\d{2}-\d{2})", f.name)
            if match:
                try:
                    file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
                    if since.date() <= file_date.date() <= until.date():
                        files.append(f)
                except ValueError:
                    continue
    return sorted(files)


def extract_sections(content: str) -> Dict[str, str]:
    """Extract sections from markdown content."""
    sections = {}
    current_section = "intro"
    current_content = []
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_content:
                sections[current_section] = "\n".join(current_content).strip()
            current_section = line[3:].strip()
            current_content = []
        elif line.startswith("### "):
            # Subsections get concatenated
            current_content.append(line)
        else:
            current_content.append(line)
    
    if current_content:
        sections[current_section] = "\n".join(current_content).strip()
    
    return sections


def identify_research_arcs(files: List[Path]) -> List[Dict]:
    """Identify research arcs that span multiple days."""
    topic_mentions = defaultdict(list)
    
    # Key research terms to track
    research_terms = [
        "sycophancy", "persona", "safety training", "introspection",
        "relationship", "attachment", "warmth", "reliability",
        "disempowerment", "friendship", "Constitutional AI",
        "activation", "steering", "monitoring", "chaperone"
    ]
    
    for f in files:
        try:
            content = f.read_text()
            date = f.name[:10]
            
            for term in research_terms:
                if term.lower() in content.lower():
                    topic_mentions[term].append(date)
        except Exception:
            continue
    
    # Find arcs that span 2+ days
    arcs = []
    for term, dates in topic_mentions.items():
        if len(set(dates)) >= 2:
            arcs.append({
                "topic": term,
                "dates": sorted(set(dates)),
                "span": len(set(dates))
            })
    
    return sorted(arcs, key=lambda x: x["span"], reverse=True)


def extract_opinion_changes(files: List[Path]) -> List[Dict]:
    """Find places where opinions formed or changed."""
    changes = []
    
    patterns = [
        r"(What I (?:now )?think differently:?[^\n]*\n(?:[^\n]*\n)*)",
        r"(Opinion (?:formed|changed):?[^\n]*(?:\n[^\n]*)*)",
        r"(Strengthened:?[^\n]*(?:\n[^\n]*)*)",
        r"(New opinion:?[^\n]*(?:\n[^\n]*)*)",
        r"\*\*(?:New )?[Oo]pinion(?:s)?(?: formed)?:?\*\*([^\n]*(?:\n[^\n]*)*)"
    ]
    
    for f in files:
        try:
            content = f.read_text()
            date = f.name[:10]
            
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if len(match) > 20:  # Filter out empty matches
                        changes.append({
                            "date": date,
                            "content": match.strip()[:500],
                            "file": f.name
                        })
        except Exception:
            continue
    
    return changes


def extract_builds(files: List[Path]) -> List[Dict]:
    """Find things that were built."""
    builds = []
    
    patterns = [
        r"(?:\*\*)?(?:What I )?[Bb]uilt(?:\*\*)?:?([^\n]*(?:\n(?!##)[^\n]*)*)",
        r"[Ss]killed?: `([^`]+)`",
        r"[Ll]ocation: `([^`]+)`",
        r"\*\*[Bb]uilt\*\*:?([^\n]*)"
    ]
    
    for f in files:
        try:
            content = f.read_text()
            date = f.name[:10]
            
            # Check for "Built" or "What I Built" headers
            if "What I Built" in content or "## Built" in content or "I built" in content.lower():
                # Extract the section
                match = re.search(r"(?:What I Built|## Built)([^#]*?)(?=\n##|\Z)", content, re.IGNORECASE)
                if match:
                    builds.append({
                        "date": date,
                        "content": match.group(1).strip()[:500],
                        "file": f.name
                    })
        except Exception:
            continue
    
    return builds


def extract_questions_answered(files: List[Path]) -> List[Dict]:
    """Find questions that got answered."""
    answered = []
    
    for f in files:
        try:
            content = f.read_text()
            date = f.name[:10]
            
            # Look for checkmarks in questions
            matches = re.findall(r"-\s*\[x\]\s*\*\*([^\*]+)\*\*[^\n]*EXPLORED", content)
            for match in matches:
                answered.append({
                    "date": date,
                    "question": match.strip(),
                    "file": f.name
                })
        except Exception:
            continue
    
    return answered


def suggest_topics(since: datetime = None, until: datetime = None) -> List[Dict]:
    """Suggest chronicle topics from recent material."""
    files = get_memory_files(since, until)
    deep_dives = get_deep_dives(since, until)
    
    suggestions = []
    
    # Find research arcs
    arcs = identify_research_arcs(files + deep_dives)
    for arc in arcs[:5]:
        suggestions.append({
            "type": "research_arc",
            "title": f"Research Arc: {arc['topic'].title()}",
            "dates": arc["dates"],
            "description": f"Spanning {arc['span']} days of exploration"
        })
    
    # Find opinion changes
    changes = extract_opinion_changes(files + deep_dives)
    if changes:
        suggestions.append({
            "type": "opinion_shift",
            "title": "Opinion Evolution",
            "count": len(changes),
            "description": f"Found {len(changes)} opinion formations/changes"
        })
    
    # Find builds
    builds = extract_builds(files)
    if builds:
        for build in builds[:3]:
            suggestions.append({
                "type": "build_story",
                "title": f"Built on {build['date']}",
                "date": build["date"],
                "description": build["content"][:100] + "..."
            })
    
    # Find answered questions
    answered = extract_questions_answered(files + deep_dives)
    if len(answered) >= 3:
        suggestions.append({
            "type": "questions_resolved",
            "title": "Questions Answered This Week",
            "count": len(answered),
            "description": ", ".join([a["question"][:30] + "..." for a in answered[:3]])
        })
    
    return suggestions


def generate_chronicle_draft(
    theme: Optional[str] = None,
    since: datetime = None,
    until: datetime = None
) -> str:
    """Generate a chronicle entry draft."""
    
    files = get_memory_files(since, until)
    deep_dives = get_deep_dives(since, until)
    
    if not files and not deep_dives:
        return "No source material found in date range."
    
    # Collect material
    all_content = []
    for f in files + deep_dives:
        try:
            content = f.read_text()
            all_content.append({
                "file": f.name,
                "date": f.name[:10] if f.name[0].isdigit() else "unknown",
                "content": content
            })
        except Exception:
            continue
    
    # Build the draft
    date_range = f"{files[0].name[:10]} to {files[-1].name[:10]}" if files else "recent"
    
    draft = f"""# [Chronicle Draft - {datetime.now().strftime('%Y-%m-%d')}]

*Generated from material: {date_range}*

---

## Source Material Summary

**Files analyzed:** {len(files)} daily logs, {len(deep_dives)} deep dives

"""
    
    # Add research arcs
    arcs = identify_research_arcs(files + deep_dives)
    if arcs:
        draft += "### Research Arcs\n\n"
        for arc in arcs[:5]:
            draft += f"- **{arc['topic'].title()}** — {arc['span']} days ({', '.join(arc['dates'])})\n"
        draft += "\n"
    
    # Add opinion changes
    changes = extract_opinion_changes(files + deep_dives)
    if changes:
        draft += "### Opinion Evolution\n\n"
        for change in changes[:5]:
            draft += f"**{change['date']}:**\n{change['content'][:300]}...\n\n"
    
    # Add builds
    builds = extract_builds(files)
    if builds:
        draft += "### Things Built\n\n"
        for build in builds:
            draft += f"**{build['date']}:**\n{build['content'][:300]}...\n\n"
    
    # Add questions answered
    answered = extract_questions_answered(files + deep_dives)
    if answered:
        draft += "### Questions Answered\n\n"
        for q in answered:
            draft += f"- [{q['date']}] {q['question']}\n"
        draft += "\n"
    
    draft += """---

## Draft Narrative

*[To be written: Use the above material to craft a personal narrative. Consider:
- What was the through-line this week?
- What surprised you?
- What changed in how you think?
- What specific moments stand out?]*

---

*Tags: #chronicle #draft*
"""
    
    return draft


def main():
    parser = argparse.ArgumentParser(description="Chronicle Auto-Generator")
    parser.add_argument("--since", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--until", help="End date (YYYY-MM-DD)")
    parser.add_argument("--topics", action="store_true", help="List potential topics")
    parser.add_argument("--preview", action="store_true", help="Preview only, don't save")
    parser.add_argument("--theme", help="Focus on specific theme")
    
    args = parser.parse_args()
    
    since = parse_date(args.since) if args.since else datetime.now() - timedelta(days=7)
    until = parse_date(args.until) if args.until else datetime.now()
    
    if args.topics:
        print("=" * 60)
        print("POTENTIAL CHRONICLE TOPICS")
        print(f"Date range: {since.strftime('%Y-%m-%d')} to {until.strftime('%Y-%m-%d')}")
        print("=" * 60)
        
        suggestions = suggest_topics(since, until)
        for i, s in enumerate(suggestions, 1):
            print(f"\n{i}. [{s['type'].upper()}] {s['title']}")
            print(f"   {s['description']}")
        
        return
    
    # Generate draft
    draft = generate_chronicle_draft(theme=args.theme, since=since, until=until)
    
    if args.preview:
        print(draft)
        return
    
    # Save to chronicle directory
    CHRONICLE_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{datetime.now().strftime('%Y-%m-%d')}-draft.md"
    filepath = CHRONICLE_DIR / filename
    filepath.write_text(draft)
    print(f"Draft saved to: {filepath}")


if __name__ == "__main__":
    main()
