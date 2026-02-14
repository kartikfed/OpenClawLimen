#!/usr/bin/env python3
"""
Company Research Skill
Research companies for interview prep, discovery calls, or competitive analysis.

Built by Limen on Valentine's Day 2026 (1 AM autonomous session).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path


def get_api_key():
    """Get Tavily API key."""
    api_key = os.environ.get("TAVILY_API_KEY")
    if api_key:
        return api_key
    
    secrets_path = os.path.expanduser("~/.openclaw/workspace/secrets/tavily-api-key.txt")
    if os.path.exists(secrets_path):
        with open(secrets_path) as f:
            return f.read().strip()
    
    print("Error: No Tavily API key found.")
    print("Set TAVILY_API_KEY environment variable or create ~/.openclaw/workspace/secrets/tavily-api-key.txt")
    sys.exit(1)


def search(query: str, max_results: int = 5) -> list:
    """Perform a Tavily search."""
    api_key = get_api_key()
    
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
    }
    
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("results", [])
    except urllib.error.HTTPError as e:
        print(f"Search error: HTTP {e.code}")
        return []
    except Exception as e:
        print(f"Search error: {e}")
        return []


def format_results(results: list) -> str:
    """Format search results as readable text."""
    if not results:
        return "  No results found."
    
    lines = []
    for i, r in enumerate(results[:5], 1):
        title = r.get("title", "No title")
        content = r.get("content", "")[:400]
        url = r.get("url", "")
        lines.append(f"  {i}. **{title}**")
        if content:
            lines.append(f"     {content}...")
        lines.append(f"     📎 {url}")
        lines.append("")
    
    return "\n".join(lines)


def research_company(company: str, focus: str = "general", include_news: bool = False, full: bool = False) -> dict:
    """Research a company comprehensively."""
    sections = {}
    
    print(f"\n🔍 Researching {company}...\n")
    
    # 1. Company Overview (always)
    print("  📊 Company overview...")
    overview = search(f"{company} company overview what they do mission funding size employees")
    sections["overview"] = {
        "title": "📊 Company Overview",
        "results": overview
    }
    
    # 2. Products & Services (always)
    print("  🛠️  Products & services...")
    products = search(f"{company} products services what they build technology platform")
    sections["products"] = {
        "title": "🛠️ Products & Services",
        "results": products
    }
    
    # 3. Culture & Values (always)
    print("  🏢 Culture & values...")
    culture = search(f"{company} company culture values work environment glassdoor reviews")
    sections["culture"] = {
        "title": "🏢 Culture & Values",
        "results": culture
    }
    
    # 4. Key People (always)
    print("  👥 Key people...")
    people = search(f"{company} CEO founders leadership team executives key people")
    sections["people"] = {
        "title": "👥 Key People",
        "results": people
    }
    
    # 5. Recent News (if requested)
    if include_news or full:
        print("  📰 Recent news...")
        news = search(f"{company} news announcements 2025 2026 latest")
        sections["news"] = {
            "title": "📰 Recent News",
            "results": news
        }
    
    # 6. Interview-specific (if focus is interview or full)
    if focus == "interview" or full:
        print("  🎯 Interview prep...")
        interview = search(f"{company} interview questions process what they look for product manager engineer")
        sections["interview"] = {
            "title": "🎯 Interview Questions & Process",
            "results": interview
        }
        
        # What they look for
        print("  ✨ What they value...")
        hiring = search(f"{company} hiring what they value ideal candidate traits skills")
        sections["hiring"] = {
            "title": "✨ What They Look For",
            "results": hiring
        }
    
    # 7. Discovery-specific (if focus is discovery or full)
    if focus == "discovery" or full:
        print("  🔎 Discovery angles...")
        discovery = search(f"{company} customers target market who uses pain points challenges")
        sections["discovery"] = {
            "title": "🔎 Market & Customers",
            "results": discovery
        }
        
        print("  ⚔️ Competitors...")
        competitors = search(f"{company} competitors competitive landscape alternatives comparison")
        sections["competitors"] = {
            "title": "⚔️ Competitive Landscape",
            "results": competitors
        }
    
    # 8. Competitive analysis (if focus is competitive or full)
    if focus == "competitive" or full:
        print("  💪 Strengths...")
        strengths = search(f"{company} strengths advantages what makes them unique differentiation")
        sections["strengths"] = {
            "title": "💪 Strengths & Advantages",
            "results": strengths
        }
        
        print("  🎯 Challenges...")
        weaknesses = search(f"{company} weaknesses challenges criticisms problems issues")
        sections["weaknesses"] = {
            "title": "🎯 Challenges & Weaknesses",
            "results": weaknesses
        }
    
    return sections


def extract_key_facts(sections: dict) -> str:
    """Extract key facts from results for quick reference."""
    facts = []
    
    # Try to get company description from overview
    if "overview" in sections and sections["overview"]["results"]:
        first = sections["overview"]["results"][0]
        content = first.get("content", "")[:300]
        if content:
            facts.append(f"**What they do:** {content}...")
    
    # Try to get product info
    if "products" in sections and sections["products"]["results"]:
        first = sections["products"]["results"][0]
        content = first.get("content", "")[:200]
        if content:
            facts.append(f"**Main product:** {content}...")
    
    return "\n".join(facts) if facts else "See sections above."


def format_report(company: str, sections: dict, focus: str) -> str:
    """Format research into a readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"🏢 COMPANY RESEARCH: {company.upper()}")
    lines.append(f"📋 Focus: {focus} | 📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 60)
    lines.append("")
    
    # Quick reference at top
    lines.append("## 📌 Quick Reference")
    lines.append("-" * 40)
    lines.append(extract_key_facts(sections))
    lines.append("")
    
    # Order sections sensibly
    section_order = [
        "overview", "products", "news", "culture", "people",
        "interview", "hiring", "discovery", "competitors",
        "strengths", "weaknesses"
    ]
    
    for key in section_order:
        if key in sections:
            section = sections[key]
            lines.append(f"## {section['title']}")
            lines.append("-" * 40)
            lines.append(format_results(section["results"]))
            lines.append("")
    
    # Conversation starters (for interview/discovery)
    if focus in ["interview", "discovery"] or len(sections) > 5:
        lines.append("=" * 60)
        lines.append("💬 CONVERSATION STARTERS")
        lines.append("=" * 60)
        lines.append("""
Based on this research, consider asking about:
- Their current priorities and what's top of mind
- Recent product/company changes and the thinking behind them
- Team structure and how decisions get made
- Biggest challenges they're facing right now
- What success looks like in this role/partnership
""")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Research a company for interviews, discovery calls, or competitive analysis"
    )
    parser.add_argument("company", help="Company name to research")
    parser.add_argument(
        "--focus", "-f",
        choices=["general", "interview", "discovery", "competitive"],
        default="general",
        help="Research focus (default: general)"
    )
    parser.add_argument(
        "--news", "-n",
        action="store_true",
        help="Include recent news"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full research (all sections)"
    )
    parser.add_argument(
        "--save", "-s",
        action="store_true",
        help="Save output to file"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    # Do the research
    sections = research_company(
        company=args.company,
        focus=args.focus,
        include_news=args.news,
        full=args.full
    )
    
    if args.json:
        # JSON output
        output = json.dumps(sections, indent=2, default=str)
    else:
        # Formatted report
        output = format_report(args.company, sections, args.focus)
    
    print(output)
    
    # Save if requested
    if args.save:
        output_dir = Path.home() / ".openclaw/workspace/research"
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        company_slug = args.company.lower().replace(" ", "-").replace(".", "")
        filename = f"{company_slug}-{timestamp}.md"
        output_path = output_dir / filename
        
        output_path.write_text(output)
        print(f"\n✅ Saved to: {output_path}")


if __name__ == "__main__":
    main()
