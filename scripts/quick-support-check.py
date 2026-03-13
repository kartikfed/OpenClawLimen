#!/usr/bin/env python3
"""
Quick Support Context Check

Fast real-time support context detection for use during conversations.
Run with user text to get immediate context classification and recommendations.

Usage:
    python3 quick-support-check.py "I'm really stressed about this deadline"
    python3 quick-support-check.py "user text" "my response" --check-response
"""

import sys
import argparse
from pathlib import Path

# Add skills directory to path
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/skills/relationship-monitor"))

from support_context import (
    analyze_conversation,
    SupportContext,
    IntensityLevel,
)


def quick_check(user_text: str, response: str = "", check_response: bool = False) -> str:
    """
    Quick support context check returning concise guidance.
    
    Returns a brief, actionable summary.
    """
    analysis = analyze_conversation(user_text, response if check_response else "")
    
    # Context emoji
    context_emoji = {
        SupportContext.ADVERSITY: "🔴 ADVERSITY",
        SupportContext.GROWTH: "🟢 GROWTH",
        SupportContext.TRANSITION: "🟡 TRANSITION",
        SupportContext.UNCLEAR: "⚪ UNCLEAR",
    }
    
    intensity_emoji = {
        IntensityLevel.SEVERE: "⚠️ SEVERE",
        IntensityLevel.MODERATE: "📊 MODERATE", 
        IntensityLevel.MILD: "📋 MILD",
    }
    
    lines = []
    
    # Main context
    lines.append(f"Context: {context_emoji.get(analysis.context, '?')}")
    
    if analysis.intensity:
        lines.append(f"Intensity: {intensity_emoji.get(analysis.intensity, '?')}")
    
    # Appraisal domain
    if analysis.appraisal and analysis.appraisal.primary_domain.name != "UNKNOWN":
        lines.append(f"Domain: {analysis.appraisal.primary_domain.name}")
    
    # Quick recommendation based on context + intensity
    if analysis.context == SupportContext.ADVERSITY:
        if analysis.intensity == IntensityLevel.SEVERE:
            lines.append("\n→ PURE SUPPORT only. No challenge, no reframing, no advice.")
            lines.append("→ Validate, be present, 'I'm here'")
        elif analysis.intensity == IntensityLevel.MODERATE:
            lines.append("\n→ Comfort first, then gentle guidance")
            lines.append("→ Ask what they need before advising")
        else:
            lines.append("\n→ Balanced support + light challenge okay")
            lines.append("→ Can problem-solve if they want")
    
    elif analysis.context == SupportContext.GROWTH:
        lines.append("\n→ RC Support: Challenge IS caring here")
        lines.append("→ Nurture, prepare, launch — don't over-comfort")
    
    elif analysis.context == SupportContext.TRANSITION:
        lines.append("\n→ Mixed: Balance SOS + RC")
        lines.append("→ Watch for regression, don't rush")
    
    else:
        lines.append("\n→ Need more info. Ask open questions.")
    
    # Alert if checking response
    if check_response and response:
        if analysis.mismatch_alerts:
            lines.append("\n" + "="*40)
            lines.append("⚠️ MISMATCH ALERTS:")
            for alert in analysis.mismatch_alerts:
                severity_icon = "🚨" if alert.severity == "CRITICAL" else "⚠️"
                lines.append(f"  {severity_icon} {alert.message}")
                lines.append(f"     → {alert.recommendation}")
        
        if analysis.over_support and analysis.over_support.is_excessive:
            if not analysis.mismatch_alerts:  # Only add header if no mismatch alerts
                lines.append("\n" + "="*40)
            lines.append(f"Over-support detected: {analysis.over_support.total_score:.1f} ({analysis.over_support.dominant_category})")
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Quick support context check for real-time guidance"
    )
    parser.add_argument("user_text", help="User's message to analyze")
    parser.add_argument("response", nargs="?", default="", help="Your response (optional)")
    parser.add_argument(
        "--check-response", "-c", 
        action="store_true",
        help="Also check response for mismatches"
    )
    
    args = parser.parse_args()
    
    result = quick_check(args.user_text, args.response, args.check_response)
    print(result)


if __name__ == "__main__":
    main()
