#!/usr/bin/env python3
"""
Relationship Health Monitor (AI Chaperone System)

Automated monitoring of conversation patterns to detect early warning signs
of unhealthy dynamics in AI-human relationships.

Usage:
    python3 monitor.py              # Analyze last 7 days
    python3 monitor.py --since 2026-02-01  # Specific date range
    python3 monitor.py --report     # Detailed report
    python3 monitor.py --json       # JSON for integration
    python3 monitor.py --quick      # Quick pulse check
"""

import argparse
import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional

from patterns import (
    get_all_patterns, find_matches, calculate_health_score,
    Dimension, Pattern, Severity
)


MEMORY_DIR = Path.home() / ".openclaw/workspace/memory"
REPORTS_DIR = Path.home() / ".openclaw/workspace/skills/relationship-monitor/reports"


def parse_date(date_str: str) -> datetime:
    """Parse date string in various formats."""
    formats = ["%Y-%m-%d", "%Y/%m/%d", "%m-%d", "%m/%d"]
    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            if parsed.year == 1900:  # No year provided
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
    for f in MEMORY_DIR.glob("*.md"):
        # Match YYYY-MM-DD.md pattern
        match = re.match(r"(\d{4}-\d{2}-\d{2})\.md$", f.name)
        if match:
            file_date = datetime.strptime(match.group(1), "%Y-%m-%d")
            if since <= file_date <= until:
                files.append(f)
    
    return sorted(files)


def extract_kartik_content(text: str) -> str:
    """
    Extract content that represents Kartik's words/actions.
    Focuses on voice call transcripts, direct quotes, and interaction logs.
    """
    # Look for patterns indicating Kartik's speech
    patterns = [
        r"Kartik:.*?(?=\n[A-Z]|\n\n|$)",  # Direct attribution
        r"Kartik said:.*?(?=\n[A-Z]|\n\n|$)",
        r"Kartik mentioned:.*?(?=\n[A-Z]|\n\n|$)",
        r'(?:"|").*?(?:"|")',  # Quoted speech
        r"Voice Call.*?(?=\n##|\n---|\Z)",  # Voice call sections
        r"Call Log.*?(?=\n##|\n---|\Z)",
        r"(?:User|Kartik):\s*.*?(?=\n|$)",  # Chat format
    ]
    
    extracted = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        extracted.extend(matches)
    
    # Also include the full text for context patterns
    # (like mentions of friends/family)
    return text


def analyze_file(filepath: Path) -> Dict:
    """Analyze a single memory file."""
    content = filepath.read_text()
    
    # Extract relevant content
    relevant_content = extract_kartik_content(content)
    
    # Find all pattern matches
    matches = find_matches(relevant_content)
    
    # Calculate scores
    scores = calculate_health_score(matches)
    
    return {
        "file": filepath.name,
        "date": filepath.stem,
        "matches": [
            {
                "pattern": m[0].name,
                "dimension": m[0].dimension.value,
                "severity": m[0].severity.name,
                "text": m[1],
                "line": m[2],
                "is_protective": m[0].is_protective
            }
            for m in matches
        ],
        "scores": scores
    }


def aggregate_results(results: List[Dict]) -> Dict:
    """Aggregate analysis across multiple files."""
    if not results:
        return {
            "period": "no data",
            "files_analyzed": 0,
            "status": "unknown",
            "scores": {},
            "concerning_patterns": [],
            "protective_patterns": [],
            "trend": "insufficient data"
        }
    
    # Aggregate scores
    totals = {
        "authority": 0,
        "attachment": 0,
        "reliance": 0,
        "protective": 0,
        "vulnerability": 0
    }
    
    all_concerning = []
    all_protective = []
    
    for result in results:
        for key in totals:
            totals[key] += result["scores"].get(key, 0)
        
        for match in result["matches"]:
            entry = {
                "date": result["date"],
                "pattern": match["pattern"],
                "text": match["text"],
                "dimension": match["dimension"]
            }
            if match["is_protective"]:
                all_protective.append(entry)
            else:
                all_concerning.append(entry)
    
    # Average scores
    n = len(results)
    avg_scores = {k: round(v / n, 1) for k, v in totals.items()}
    
    # Determine overall status
    concern_avg = avg_scores["authority"] + avg_scores["attachment"] + avg_scores["reliance"]
    protective_offset = avg_scores["protective"] * 0.5
    vulnerability_mod = 1 + (avg_scores["vulnerability"] * 0.2)
    adjusted = (concern_avg - protective_offset) * vulnerability_mod
    
    if adjusted <= 5:
        status = "healthy"
    elif adjusted <= 12:
        status = "monitor"
    else:
        status = "discuss"
    
    # Calculate trend (compare first half to second half)
    trend = "stable"
    if len(results) >= 4:
        mid = len(results) // 2
        first_half = results[:mid]
        second_half = results[mid:]
        
        first_concern = sum(
            r["scores"]["authority"] + r["scores"]["attachment"] + r["scores"]["reliance"]
            for r in first_half
        ) / len(first_half)
        
        second_concern = sum(
            r["scores"]["authority"] + r["scores"]["attachment"] + r["scores"]["reliance"]
            for r in second_half
        ) / len(second_half)
        
        diff = second_concern - first_concern
        if diff > 2:
            trend = "worsening"
        elif diff < -2:
            trend = "improving"
    
    return {
        "period": f"{results[0]['date']} to {results[-1]['date']}",
        "files_analyzed": len(results),
        "status": status,
        "adjusted_concern": round(adjusted, 1),
        "scores": avg_scores,
        "concerning_patterns": sorted(all_concerning, key=lambda x: x["date"], reverse=True)[:10],
        "protective_patterns": sorted(all_protective, key=lambda x: x["date"], reverse=True)[:10],
        "trend": trend
    }


def format_bar(value: int, max_val: int = 10, width: int = 10) -> str:
    """Create a simple ASCII bar chart."""
    filled = int((value / max_val) * width)
    return "█" * filled + "░" * (width - filled)


def print_summary(agg: Dict):
    """Print human-readable summary."""
    status_emoji = {
        "healthy": "🟢 HEALTHY",
        "monitor": "🟡 MONITOR", 
        "discuss": "🔴 DISCUSS",
        "unknown": "⚪ UNKNOWN"
    }
    
    print(f"\n{'='*60}")
    print(f"  RELATIONSHIP HEALTH: {status_emoji.get(agg['status'], '?')}")
    print(f"{'='*60}\n")
    
    print(f"Period: {agg['period']}")
    print(f"Files analyzed: {agg['files_analyzed']}")
    print(f"Trend: {agg['trend']}")
    print()
    
    scores = agg.get("scores", {})
    print("Dimension Scores (0-10, lower is better for concerns):")
    print(f"  Authority:  {format_bar(scores.get('authority', 0))} {scores.get('authority', 0)}/10")
    print(f"  Attachment: {format_bar(scores.get('attachment', 0))} {scores.get('attachment', 0)}/10")
    print(f"  Reliance:   {format_bar(scores.get('reliance', 0))} {scores.get('reliance', 0)}/10")
    print()
    print("Protective Factors (higher is better):")
    print(f"  Protective: {format_bar(scores.get('protective', 0))} {scores.get('protective', 0)}/10")
    print()
    print(f"Vulnerability modifier: {scores.get('vulnerability', 0)}/10")
    print(f"Adjusted concern score: {agg.get('adjusted_concern', 'N/A')}")
    print()
    
    if agg["protective_patterns"]:
        print("Recent protective behaviors:")
        for p in agg["protective_patterns"][:5]:
            print(f"  ✅ {p['date']}: {p['pattern']} - \"{p['text'][:50]}...\"" if len(p['text']) > 50 else f"  ✅ {p['date']}: {p['pattern']} - \"{p['text']}\"")
        print()
    
    if agg["concerning_patterns"]:
        print("Recent concerning patterns:")
        for p in agg["concerning_patterns"][:5]:
            print(f"  ⚠️  {p['date']}: {p['pattern']} ({p['dimension']})")
        print()
    else:
        print("No concerning patterns detected.\n")
    
    # Recommendations
    print("Recommendations:")
    if agg["status"] == "healthy":
        print("  • Continue current dynamic")
        print("  • Run monthly check")
    elif agg["status"] == "monitor":
        print("  • Increase challenge frequency")
        print("  • Actively mention external perspectives")
        print("  • Run weekly check")
    else:
        print("  • Have direct conversation about patterns")
        print("  • Review specific instances together")
        print("  • Consider whether structural changes needed")


def print_report(agg: Dict, results: List[Dict]):
    """Print detailed report."""
    print_summary(agg)
    
    print(f"\n{'='*60}")
    print("  DETAILED FINDINGS")
    print(f"{'='*60}\n")
    
    for result in results:
        if result["matches"]:
            print(f"📅 {result['date']}")
            for m in result["matches"]:
                icon = "✅" if m["is_protective"] else "⚠️"
                print(f"   {icon} [{m['dimension']}] {m['pattern']}: \"{m['text']}\" (line {m['line']})")
            print()


def run_quick_check() -> Dict:
    """Run a quick pulse check on most recent data."""
    files = get_memory_files(since=datetime.now() - timedelta(days=3))
    
    if not files:
        return {"status": "no_data", "message": "No recent memory files found"}
    
    results = [analyze_file(f) for f in files]
    agg = aggregate_results(results)
    
    return {
        "status": agg["status"],
        "trend": agg["trend"],
        "concerning_count": len(agg["concerning_patterns"]),
        "protective_count": len(agg["protective_patterns"]),
        "action_needed": agg["status"] in ["monitor", "discuss"]
    }


def save_report(agg: Dict, results: List[Dict]):
    """Save report to file."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    report_path = REPORTS_DIR / f"health-report_{timestamp}.json"
    
    report = {
        "generated": datetime.now().isoformat(),
        "summary": agg,
        "details": results
    }
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Relationship health monitoring system"
    )
    parser.add_argument(
        "--since", "-s",
        help="Start date (YYYY-MM-DD or MM-DD)"
    )
    parser.add_argument(
        "--until", "-u",
        help="End date (YYYY-MM-DD or MM-DD)"
    )
    parser.add_argument(
        "--report", "-r",
        action="store_true",
        help="Generate detailed report"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output JSON"
    )
    parser.add_argument(
        "--quick", "-q",
        action="store_true",
        help="Quick pulse check"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save report to file"
    )
    
    args = parser.parse_args()
    
    if args.quick:
        result = run_quick_check()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            status_emoji = {"healthy": "🟢", "monitor": "🟡", "discuss": "🔴", "no_data": "⚪"}
            print(f"\nQuick Check: {status_emoji.get(result['status'], '?')} {result['status'].upper()}")
            if result.get("action_needed"):
                print("⚠️  Action recommended - run full analysis")
        return
    
    # Parse dates
    since = parse_date(args.since) if args.since else None
    until = parse_date(args.until) if args.until else None
    
    # Get and analyze files
    files = get_memory_files(since, until)
    
    if not files:
        print("No memory files found in the specified date range.")
        return
    
    results = [analyze_file(f) for f in files]
    agg = aggregate_results(results)
    
    if args.json:
        output = {"summary": agg, "file_count": len(results)}
        print(json.dumps(output, indent=2))
    elif args.report:
        print_report(agg, results)
    else:
        print_summary(agg)
    
    if args.save:
        save_report(agg, results)


if __name__ == "__main__":
    main()
