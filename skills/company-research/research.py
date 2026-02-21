#!/usr/bin/env python3
"""
Company Research Tool

Quick research on any company for interview prep.
Usage: python3 research.py "Company Name" [--depth quick|deep]
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SECRETS_DIR = WORKSPACE / "secrets"
OUTPUT_DIR = WORKSPACE / "job-search" / "prep"

def get_tavily_key():
    """Read Tavily API key from secrets."""
    key_file = SECRETS_DIR / "tavily-api-key.txt"
    if not key_file.exists():
        print("Error: Tavily API key not found at", key_file)
        sys.exit(1)
    return key_file.read_text().strip()

def search_tavily(query: str, max_results: int = 5) -> list[dict]:
    """Run a Tavily search and return results."""
    api_key = get_tavily_key()
    
    cmd = [
        "curl", "-s", "https://api.tavily.com/search",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({
            "api_key": api_key,
            "query": query,
            "search_depth": "advanced",
            "max_results": max_results
        })
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        data = json.loads(result.stdout)
        return data.get("results", [])
    except Exception as e:
        print(f"Search failed: {e}")
        return []

def format_results(results: list[dict], max_chars: int = 500) -> str:
    """Format search results for markdown."""
    output = []
    for r in results:
        title = r.get("title", "No title")
        content = r.get("content", "")[:max_chars]
        url = r.get("url", "")
        output.append(f"**{title}**\n{content}...\n*Source: {url}*\n")
    return "\n".join(output)

def research_company(company: str, depth: str = "quick") -> str:
    """Research a company and return markdown report."""
    
    searches = {
        "quick": [
            (f"{company} company overview what they do", "Overview"),
            (f"{company} interview process hiring 2025", "Interview Process"),
        ],
        "deep": [
            (f"{company} company overview what they do funding valuation", "Overview"),
            (f"{company} culture values mission", "Culture & Values"),
            (f"{company} recent news announcements 2025 2026", "Recent News"),
            (f"{company} interview process hiring tips 2025", "Interview Process"),
            (f"{company} CEO leadership team founders", "Key People"),
        ]
    }
    
    sections = []
    for query, section_name in searches[depth]:
        print(f"  Searching: {section_name}...")
        results = search_tavily(query, max_results=3)
        if results:
            sections.append(f"## {section_name}\n\n{format_results(results)}")
    
    # Build markdown document
    doc = f"""# {company} Research

*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*
*Depth: {depth}*

---

{"---".join(sections)}

---

## Talking Points

Based on the research above, consider discussing:
- [Fill in based on research]
- [Fill in based on research]
- [Fill in based on research]

## Questions to Ask

- What's the biggest challenge the team is working on right now?
- How do you measure success in this role?
- What does growth look like here?

---

*Research compiled by Limen*
"""
    return doc

def main():
    parser = argparse.ArgumentParser(description="Research a company for interview prep")
    parser.add_argument("company", help="Company name to research")
    parser.add_argument("--depth", choices=["quick", "deep"], default="quick",
                        help="Research depth (default: quick)")
    args = parser.parse_args()
    
    print(f"Researching {args.company} ({args.depth} depth)...")
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Run research
    report = research_company(args.company, args.depth)
    
    # Save report
    filename = args.company.lower().replace(" ", "-").replace(".", "") + "-research.md"
    output_path = OUTPUT_DIR / filename
    output_path.write_text(report)
    
    print(f"\n✅ Research saved to: {output_path}")
    print(f"\nPreview:\n{'-'*40}")
    print(report[:1000] + "...")

if __name__ == "__main__":
    main()
