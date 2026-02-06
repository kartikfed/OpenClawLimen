#!/usr/bin/env python3
"""Tavily web search - fast, AI-optimized search."""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_KEY = os.environ.get("TAVILY_API_KEY")
if not API_KEY:
    sys.exit("Error: TAVILY_API_KEY environment variable not set")
API_URL = "https://api.tavily.com/search"

def search(query: str, max_results: int = 5, search_depth: str = "basic", include_answer: bool = False) -> dict:
    payload = {
        "api_key": API_KEY,
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": include_answer,
    }
    
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "body": e.read().decode("utf-8", errors="replace")}
    except Exception as e:
        return {"error": str(e)}

def format_results(data: dict) -> str:
    if "error" in data:
        return f"Error: {data['error']}"
    
    lines = []
    
    if data.get("answer"):
        lines.append(f"**Answer:** {data['answer']}\n")
    
    for i, result in enumerate(data.get("results", []), 1):
        title = result.get("title", "No title")
        url = result.get("url", "")
        content = result.get("content", "")[:500]
        lines.append(f"### {i}. {title}")
        lines.append(f"URL: {url}")
        lines.append(f"{content}\n")
    
    return "\n".join(lines) if lines else "No results found."

def main():
    parser = argparse.ArgumentParser(description="Tavily web search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--search-depth", choices=["basic", "advanced"], default="basic")
    parser.add_argument("--include-answer", action="store_true", help="Include AI answer")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    result = search(args.query, args.max_results, args.search_depth, args.include_answer)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_results(result))

if __name__ == "__main__":
    main()
