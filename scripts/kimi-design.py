#!/usr/bin/env python3
"""
Kimi K2.5 Dashboard Design Tool

Uses Kimi K2.5's visual-to-code capabilities to redesign dashboard components.
Supports both NVIDIA NIMs (free) and Moonshot AI (official) endpoints.
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from openai import OpenAI

# API Configuration
# Priority: NVIDIA NIMs (free) > Moonshot AI > OpenRouter
PROVIDERS = {
    "nvidia": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "moonshotai/kimi-k2.5",
        "env_key": "NVIDIA_API_KEY",
    },
    "moonshot": {
        "base_url": "https://api.moonshot.cn/v1",
        "model": "kimi-k2.5",
        "env_key": "MOONSHOT_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "moonshotai/kimi-k2.5",
        "env_key": "OPENROUTER_API_KEY",
    },
}

# Design system prompt for premium dashboard redesign
DESIGN_SYSTEM_PROMPT = """You are a senior product designer and front-end engineer specializing in premium dashboard design.

Your design philosophy:
- Professional, shipped product aesthetic — NOT AI-generated looking
- Strong visual hierarchy with balanced whitespace
- Clear typography with proper sizing hierarchy
- Cohesive color system (dark theme with purple/blue/coral accents)
- Tasteful motion design: scroll-triggered reveals, subtle hover states, micro-interactions
- Modern glassmorphism effects done right (subtle, not overdone)

Tech stack: React + TypeScript + Tailwind CSS + Framer Motion

When redesigning:
1. Preserve all data and functionality
2. Improve visual hierarchy and aesthetics
3. Add tasteful animations (entrance, hover, transitions)
4. Use consistent spacing and sizing
5. Include comments explaining key design decisions

Return ONLY the code — no explanations before or after."""


def encode_image(image_path: str) -> str:
    """Encode image to base64 for API."""
    with open(image_path, "rb") as f:
        return base64.standard_b64encode(f.read()).decode("utf-8")


def get_mime_type(path: str) -> str:
    """Get MIME type from file extension."""
    ext = Path(path).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/png")


def get_client(provider: str = "nvidia"):
    """Get OpenAI-compatible client for specified provider."""
    config = PROVIDERS.get(provider, PROVIDERS["nvidia"])
    api_key = os.environ.get(config["env_key"])
    
    if not api_key:
        # Try fallback providers
        for p, c in PROVIDERS.items():
            key = os.environ.get(c["env_key"])
            if key:
                print(f"Using fallback provider: {p}")
                config = c
                api_key = key
                break
    
    if not api_key:
        raise ValueError(
            f"No API key found. Set one of: "
            f"{', '.join(c['env_key'] for c in PROVIDERS.values())}"
        )
    
    return OpenAI(base_url=config["base_url"], api_key=api_key), config["model"]


def redesign_component(
    code: str,
    screenshot_path: str = None,
    reference_images: list = None,
    custom_prompt: str = None,
    provider: str = "nvidia",
    thinking: bool = False,
) -> str:
    """
    Send code (and optionally screenshot) to Kimi K2.5 for redesign.
    
    Args:
        code: Current component code
        screenshot_path: Path to screenshot of current component
        reference_images: List of paths to reference/inspiration images
        custom_prompt: Custom design instructions
        provider: API provider to use
        thinking: Enable reasoning mode for more thoughtful design
    
    Returns:
        Redesigned code
    """
    client, model = get_client(provider)
    
    # Build the message content
    content = []
    
    # Add design brief
    design_brief = custom_prompt or """
Redesign this dashboard component to look like a professional, shipped SaaS product.

Goals:
- Premium dark theme with purple/blue/coral gradient accents
- Big, prominent stat numbers with proper visual hierarchy  
- Card-based layout with subtle glass morphism
- Tasteful entrance animations and hover states
- Minimal but visually interesting
- Progress rings, mini charts where appropriate
- Modern spacing and typography

Keep the same data/props interface but completely transform the visuals.
"""
    content.append({"type": "text", "text": design_brief})
    
    # Add reference images if provided
    if reference_images:
        content.append({
            "type": "text", 
            "text": "\n\nHere are reference dashboards I want to match the style of:"
        })
        for img_path in reference_images:
            if os.path.exists(img_path):
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{get_mime_type(img_path)};base64,{encode_image(img_path)}"
                    }
                })
    
    # Add current screenshot if provided
    if screenshot_path and os.path.exists(screenshot_path):
        content.append({
            "type": "text",
            "text": "\n\nHere is a screenshot of the current component:"
        })
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{get_mime_type(screenshot_path)};base64,{encode_image(screenshot_path)}"
            }
        })
    
    # Add the code
    content.append({
        "type": "text",
        "text": f"\n\nHere is the current code to redesign:\n\n```tsx\n{code}\n```"
    })
    
    # Make the API call
    messages = [
        {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
        {"role": "user", "content": content}
    ]
    
    # Add thinking parameter if supported
    extra_params = {}
    if thinking:
        extra_params["extra_body"] = {"thinking": True}
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=16000,
        temperature=0.7,
        **extra_params
    )
    
    return response.choices[0].message.content


def motion_refinement_pass(code: str, provider: str = "nvidia") -> str:
    """
    Second pass focused only on motion design refinement.
    """
    client, model = get_client(provider)
    
    motion_prompt = """
Do not change layout or content. Only refine motion design:
- Entrance animations (staggered fades, slides)
- Hover micro-interactions (subtle lifts, glows)
- Smooth transitions between dashboard panels
- Chart/progress animations
- Keep it subtle, aligned with modern SaaS patterns

Return the full code with motion improvements.
"""
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": DESIGN_SYSTEM_PROMPT},
            {"role": "user", "content": f"{motion_prompt}\n\n```tsx\n{code}\n```"}
        ],
        max_tokens=16000,
        temperature=0.5,
    )
    
    return response.choices[0].message.content


def main():
    parser = argparse.ArgumentParser(description="Kimi K2.5 Dashboard Design Tool")
    parser.add_argument("code_file", help="Path to component file to redesign")
    parser.add_argument("--screenshot", "-s", help="Screenshot of current component")
    parser.add_argument("--reference", "-r", nargs="+", help="Reference/inspiration images")
    parser.add_argument("--prompt", "-p", help="Custom design prompt")
    parser.add_argument("--provider", default="nvidia", choices=PROVIDERS.keys())
    parser.add_argument("--thinking", "-t", action="store_true", help="Enable reasoning mode")
    parser.add_argument("--motion-pass", "-m", action="store_true", help="Do motion refinement pass")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    # Read the code
    with open(args.code_file, "r") as f:
        code = f.read()
    
    print(f"🎨 Sending to Kimi K2.5 ({args.provider})...", file=sys.stderr)
    
    # First pass: full redesign
    result = redesign_component(
        code=code,
        screenshot_path=args.screenshot,
        reference_images=args.reference,
        custom_prompt=args.prompt,
        provider=args.provider,
        thinking=args.thinking,
    )
    
    # Optional motion refinement pass
    if args.motion_pass:
        print("✨ Running motion refinement pass...", file=sys.stderr)
        result = motion_refinement_pass(result, provider=args.provider)
    
    # Output
    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"✅ Saved to {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
