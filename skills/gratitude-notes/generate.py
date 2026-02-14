#!/usr/bin/env python3
"""
Gratitude Notes Generator
Generate thoughtful, personalized appreciation messages.

Built by Limen on Valentine's Day 2026 (1 AM autonomous session).
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error


def get_api_key():
    """Get Anthropic API key."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        return api_key
    
    # Try common locations
    key_paths = [
        os.path.expanduser("~/.openclaw/workspace/secrets/anthropic-api-key.txt"),
        os.path.expanduser("~/.anthropic/api_key"),
        os.path.expanduser("~/.config/anthropic/api_key"),
    ]
    
    for path in key_paths:
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
    
    return None  # Will fall back to templates


TEMPLATES = {
    "valentines": {
        "casual": [
            "Hey {name}, just wanted to say you're awesome and I appreciate having you in my life. Happy Valentine's Day! 💝",
            "Happy V-Day {name}! Thanks for being you. {context_snippet}",
            "Yo {name}! Couldn't let today pass without saying thanks for everything. You're the best.",
        ],
        "heartfelt": [
            "{name}, I don't say it enough, but I'm really grateful for you. {context_snippet} Here's to many more memories together.",
            "Happy Valentine's Day, {name}. You've made such a difference in my life. Thank you for being you.",
            "Thinking about everything you bring to my life today, {name}. Grateful doesn't cover it.",
        ],
    },
    "general": {
        "casual": [
            "Hey {name}! Random appreciation: {context_snippet} Thanks for being awesome.",
            "Just wanted to say thanks for being you, {name}. {context_snippet}",
            "{name}! Quick note to say you're great. That's all. 😊",
        ],
        "heartfelt": [
            "{name}, I've been thinking about how lucky I am to have you in my life. {context_snippet} Thank you.",
            "No special occasion, just wanted you to know I appreciate you, {name}. {context_snippet}",
            "Hey {name}. Sometimes I forget to say it, but you mean a lot to me. {context_snippet}",
        ],
    },
}


def generate_with_templates(name: str, context: str, tone: str, occasion: str) -> str:
    """Generate messages using templates (fallback when no API key)."""
    # Extract a snippet from context
    context_snippet = context.split(",")[0].strip() if "," in context else context[:50]
    
    templates = TEMPLATES.get(occasion, TEMPLATES["general"]).get(tone, TEMPLATES["general"]["heartfelt"])
    
    lines = ["(Generated with templates - set ANTHROPIC_API_KEY for personalized messages)\n"]
    for i, template in enumerate(templates, 1):
        msg = template.format(name=name, context_snippet=context_snippet)
        lines.append(f"**Option {i}:**\n{msg}\n")
    
    return "\n".join(lines)


def generate_with_claude(prompt: str, api_key: str) -> str:
    """Generate text using Claude API."""
    
    payload = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("content", [{}])[0].get("text", "")
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"API error: HTTP {e.code}")
        print(f"Details: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def build_prompt(name: str, context: str, tone: str, occasion: str, length: str) -> str:
    """Build the prompt for generating gratitude notes."""
    
    occasion_context = {
        "valentines": "This is for Valentine's Day - a day to express love and appreciation to the important people in your life (not just romantic partners).",
        "birthday": "This is for their birthday - celebrate them and what they mean to you.",
        "thanks": "This is a thank you note for something specific they did.",
        "general": "This is a 'just because' appreciation message - no special occasion needed."
    }
    
    tone_guidance = {
        "casual": "Keep it light and conversational, like texting a friend.",
        "heartfelt": "Be sincere and emotionally genuine without being over the top.",
        "professional": "Warm but appropriate for a work relationship.",
        "funny": "Add some humor and lightness while still being appreciative."
    }
    
    length_guidance = {
        "short": "1-2 sentences max. Perfect for a quick text.",
        "medium": "3-4 sentences. Substantial but not overwhelming.",
        "long": "A full paragraph. Really express yourself."
    }
    
    prompt = f"""Generate 3 appreciation messages for {name}.

Context about them and our relationship: {context}

Occasion: {occasion_context.get(occasion, occasion_context['general'])}
Tone: {tone_guidance.get(tone, tone_guidance['heartfelt'])}
Length for each option: {length_guidance.get(length, length_guidance['medium'])}

Guidelines:
- Make it personal and specific based on the context provided
- Sound like a real person wrote it, not a template
- Don't be cheesy or use clichés like "in this fast-paced world"
- Vary the approach across the 3 options (different angles on appreciation)
- Don't include greetings like "Dear X" - just the message content

Format your response as:

**Option 1:**
[message]

**Option 2:**
[message]

**Option 3:**
[message]
"""
    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Generate thoughtful appreciation messages"
    )
    parser.add_argument("name", help="Who the note is for")
    parser.add_argument("context", help="What you appreciate about them, relationship details")
    parser.add_argument(
        "--tone", "-t",
        choices=["casual", "heartfelt", "professional", "funny"],
        default="heartfelt",
        help="Tone of the message (default: heartfelt)"
    )
    parser.add_argument(
        "--occasion", "-o",
        choices=["valentines", "birthday", "thanks", "general"],
        default="general",
        help="Occasion for the note (default: general)"
    )
    parser.add_argument(
        "--length", "-l",
        choices=["short", "medium", "long"],
        default="medium",
        help="Message length (default: medium)"
    )
    
    args = parser.parse_args()
    
    print(f"\n💝 Generating appreciation notes for {args.name}...\n")
    
    api_key = get_api_key()
    
    if api_key:
        prompt = build_prompt(
            name=args.name,
            context=args.context,
            tone=args.tone,
            occasion=args.occasion,
            length=args.length
        )
        result = generate_with_claude(prompt, api_key)
    else:
        result = generate_with_templates(
            name=args.name,
            context=args.context,
            tone=args.tone,
            occasion=args.occasion
        )
    
    print("=" * 50)
    print(f"💌 GRATITUDE NOTES FOR {args.name.upper()}")
    print(f"Tone: {args.tone} | Occasion: {args.occasion} | Length: {args.length}")
    print("=" * 50)
    print()
    print(result)
    print()
    print("=" * 50)
    print("Pick the one that feels most like you, or mix and match! 💝")
    print("=" * 50)


if __name__ == "__main__":
    main()
