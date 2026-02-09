#!/usr/bin/env python3
"""Grok social search - real-time X/Twitter search via xAI API."""

import argparse
import json
import os
import urllib.request
import urllib.error

API_KEY = os.environ.get("XAI_API_KEY")
if not API_KEY:
    # Try loading from secrets file
    secrets_path = os.path.expanduser("~/.openclaw/workspace/secrets/xai-api-key.txt")
    if os.path.exists(secrets_path):
        with open(secrets_path) as f:
            API_KEY = f.read().strip()
    else:
        import sys
        sys.exit("Error: XAI_API_KEY environment variable not set")
API_URL = "https://api.x.ai/v1/responses"

def search(query: str, mode: str = "x_search", max_tokens: int = 1000) -> dict:
    """Search X/Twitter or web using Grok's live search."""
    
    payload = {
        "model": "grok-4-1-fast",
        "input": [
            {"role": "user", "content": query}
        ],
        "tools": [{"type": mode}],
        "max_output_tokens": max_tokens,
    }
    
    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
            "User-Agent": "OpenClaw/1.0"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"error": f"HTTP {e.code}: {e.reason}", "body": body}
    except Exception as e:
        return {"error": str(e)}

def format_results(data: dict) -> str:
    if data.get("error"):  # Only if error is truthy (not None/null)
        return f"Error: {data['error']}\n{data.get('body', '')}"
    
    # Extract response content
    output = data.get("output", [])
    content_parts = []
    
    for item in output:
        if item.get("type") == "message":
            content = item.get("content", [])
            # content is a list of objects with "text" field
            if isinstance(content, list):
                for c in content:
                    if isinstance(c, dict) and c.get("text"):
                        content_parts.append(c["text"])
            elif isinstance(content, str) and content:
                content_parts.append(content)
    
    result = "\n".join(content_parts) if content_parts else "No results."
    
    # Add citations if present
    citations = data.get("citations", [])
    if citations:
        result += "\n\n**Sources:**\n"
        for cite in citations[:5]:
            if isinstance(cite, dict):
                result += f"- {cite.get('url', cite)}\n"
            else:
                result += f"- {cite}\n"
    
    return result

def main():
    parser = argparse.ArgumentParser(description="Grok X/Twitter search")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--mode", choices=["x_search", "web_search"], default="x_search",
                        help="Search mode (default: x_search for X/Twitter)")
    parser.add_argument("--max-tokens", type=int, default=1000, help="Max tokens")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    result = search(args.query, args.mode, args.max_tokens)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_results(result))

if __name__ == "__main__":
    main()
