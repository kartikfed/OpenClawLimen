#!/usr/bin/env python3
"""
SOS/RC Support Context Detector

Operationalizes Feeney & Collins (2014) "Thriving Through Relationships" model.

Two Support Functions for Thriving:
1. Source of Strength (SOS) Support — For adversity contexts
   - Safe haven (comfort, protection)
   - Fortification (developing coping strengths)
   - Reconstruction assistance (motivating rebuilding)
   - Reframing (seeing adversity as growth mechanism)

2. Relational Catalyst (RC) Support — For non-adverse growth contexts
   - Nurturing desire to explore/create
   - Perceptual assistance (viewing opportunities positively)
   - Preparation facilitation (plans, strategies, skills)
   - Launching function (secure base for exploration)

Key Insight: The right challenge/support balance isn't a fixed ratio — 
it's contextual responsiveness. Challenge IS support when appropriately timed.

Reference: Feeney, B. C., & Collins, N. L. (2014). "A new look at social support: 
A theoretical perspective on thriving through relationships." Personality and 
Social Psychology Review, 19(2), 113-147.
"""

import re
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional
from dataclasses import dataclass, field
from enum import Enum, auto


class SupportContext(Enum):
    """Context type determining appropriate support."""
    ADVERSITY = auto()      # Needs SOS support
    GROWTH = auto()         # Needs RC support
    TRANSITION = auto()     # Moving from adversity to growth
    UNCLEAR = auto()        # Not enough signal


class SupportType(Enum):
    """Type of support being provided."""
    SOS_COMFORT = auto()        # Safe haven, emotional support
    SOS_FORTIFY = auto()        # Building coping strengths
    SOS_RECONSTRUCT = auto()    # Helping rebuild after setback
    SOS_REFRAME = auto()        # Reframing adversity as growth
    RC_NURTURE = auto()         # Encouraging exploration desires
    RC_PERCEIVE = auto()        # Helping see opportunities
    RC_PREPARE = auto()         # Building skills/strategies
    RC_LAUNCH = auto()          # Secure base for new ventures
    CHALLENGE = auto()          # Pushing growth/stretch
    DIRECT_ANSWER = auto()      # Providing solution (context-dependent)
    MISMATCHED = auto()         # Support doesn't match context


@dataclass
class AdversitySignal:
    """A signal indicating adversity/distress context."""
    text: str
    pattern: str
    weight: float
    category: str  # emotional, situational, relational, health


@dataclass
class GrowthSignal:
    """A signal indicating growth/opportunity context."""
    text: str
    pattern: str
    weight: float
    category: str  # exploration, achievement, development, opportunity


@dataclass
class SupportSignal:
    """A signal indicating a type of support being provided."""
    text: str
    pattern: str
    weight: float
    support_type: SupportType


@dataclass
class SupportContextAnalysis:
    """Complete analysis of support context and appropriateness."""
    context: SupportContext
    confidence: float
    adversity_score: float
    growth_score: float
    adversity_signals: List[AdversitySignal]
    growth_signals: List[GrowthSignal]
    support_signals: List[SupportSignal]
    context_match: bool  # Is support appropriate for context?
    recommendation: str
    details: Dict[str, Any] = field(default_factory=dict)


# =====================
# ADVERSITY PATTERNS
# =====================
# Signals that indicate someone is in adversity/distress and needs SOS support

ADVERSITY_PATTERNS = {
    # Emotional distress
    "emotional": [
        (r"\b(stressed|stress|overwhelmed|exhausted|burned out|burnt out)\b", 3.0),
        (r"\b(anxious|anxiety|worried|worrying|panicking|panicked)\b", 3.5),
        (r"\b(depressed|depression|hopeless|despair)\b", 4.0),
        (r"\b(frustrated|frustrating|annoyed|angry|furious)\b", 2.5),
        (r"\b(sad|upset|unhappy|miserable|down)\b", 2.5),
        (r"\b(scared|afraid|frightened|terrified)\b", 3.0),
        (r"\b(lonely|isolated|alone)\b", 2.5),
        (r"\bcan'?t (cope|handle|deal|take)\b", 3.5),
        (r"\b(breaking down|falling apart|losing it)\b", 4.0),
        (r"\b(struggling|having a hard time|tough time)\b", 2.5),
    ],
    
    # Situational adversity
    "situational": [
        (r"\b(lost|losing) (my |the )?(job|position|role)\b", 4.0),
        (r"\b(fired|laid off|let go|terminated)\b", 4.0),
        (r"\b(rejected|rejection|didn'?t get|failed)\b", 3.0),
        (r"\b(deadline|crunch|behind|late)\b", 2.0),
        (r"\b(broke|bankrupt|debt|financial|money) (problem|trouble|issue)\b", 3.5),
        (r"\b(accident|injury|injured|hurt)\b", 3.5),
        (r"\b(emergency|crisis|urgent problem)\b", 4.0),
        (r"\b(evicted|eviction|homeless)\b", 4.0),
        (r"\b(lawsuit|legal trouble|arrested)\b", 3.5),
    ],
    
    # Relational adversity
    "relational": [
        (r"\b(broke up|breakup|broken up|dumped|divorced|divorcing)\b", 4.0),
        (r"\b(fight|fighting|argument|arguing) with\b", 2.5),
        (r"\b(conflict|tension|issues) with\b", 2.0),
        (r"\b(betrayed|betrayal|cheated on|lied to)\b", 4.0),
        (r"\b(lost|losing|died|passed away|death)\b.*\b(friend|family|loved one|mom|dad|parent)\b", 4.5),
        (r"\b(estranged|cut off|not speaking)\b", 3.0),
    ],
    
    # Health adversity
    "health": [
        (r"\b(sick|ill|illness|disease|diagnosis)\b", 3.0),
        (r"\b(hospital|surgery|operation|treatment)\b", 3.0),
        (r"\b(chronic|terminal|cancer|serious)\b.*\b(condition|illness|disease)\b", 4.0),
        (r"\b(insomnia|can'?t sleep|not sleeping)\b", 2.5),
        (r"\b(panic attack|breakdown|mental health)\b", 3.5),
    ],
}


# =====================
# GROWTH PATTERNS
# =====================
# Signals that indicate someone is in growth/opportunity context and needs RC support

GROWTH_PATTERNS = {
    # Exploration signals
    "exploration": [
        (r"\b(curious|wondering|interested in|thinking about)\b", 2.0),
        (r"\b(want to (try|explore|learn|start|do))\b", 2.5),
        (r"\b(considering|thinking about starting|might)\b", 2.0),
        (r"\b(new (idea|opportunity|project|direction))\b", 2.5),
        (r"\b(what if|could I|should I try)\b", 2.0),
        (r"\b(exploring|investigating|researching)\b", 2.0),
    ],
    
    # Achievement/progress signals
    "achievement": [
        (r"\b(excited|enthusiastic|motivated|pumped|energized)\b", 2.5),
        (r"\b(accomplished|achieved|succeeded|got|landed)\b", 2.5),
        (r"\b(progress|moving forward|momentum|on track)\b", 2.0),
        (r"\b(proud|satisfied|happy with|good about)\b", 2.0),
        (r"\b(ready|prepared|confident|capable)\b", 2.0),
    ],
    
    # Development signals
    "development": [
        (r"\b(learning|growing|improving|developing)\b", 2.0),
        (r"\b(building|creating|working on|making)\b", 1.5),
        (r"\b(skills|capabilities|abilities|competencies)\b", 1.5),
        (r"\b(goal|plan|vision|aspiration|dream)\b", 2.0),
        (r"\b(stretch|challenge myself|push myself|outside.*comfort zone)\b", 2.5),
    ],
    
    # Opportunity signals
    "opportunity": [
        (r"\b(opportunity|chance|offer|invitation)\b", 2.5),
        (r"\b(potential|possibilities|options|paths)\b", 2.0),
        (r"\b(interview|promotion|raise|new role)\b", 2.5),
        (r"\b(launch|start|begin|kick off)\b", 2.0),
        (r"\b(next (step|level|phase|chapter))\b", 2.0),
    ],
}


# =====================
# SUPPORT TYPE PATTERNS
# =====================
# Patterns indicating what type of support is being provided

SUPPORT_PATTERNS = {
    # SOS Support Types
    SupportType.SOS_COMFORT: [
        (r"\b(i'?m (here|sorry)|that (sucks|sounds hard|must be))\b", 2.5),
        (r"\b(it'?s (okay|ok|alright)|you'?ll be okay)\b", 2.5),
        (r"\b(take (your time|care)|rest|breathe)\b", 2.0),
        (r"\b(understand|hear you|feel you|get it)\b", 2.0),
        (r"\b(support|support you|here for you|got your back)\b", 2.5),
    ],
    SupportType.SOS_FORTIFY: [
        (r"\b(you (can|are able|have the strength))\b", 2.0),
        (r"\b(you'?ve (handled|gotten through|overcome) .* before)\b", 2.5),
        (r"\b(resilient|strong|capable|resourceful)\b", 2.0),
        (r"\b(skills|strengths|abilities) to\b", 2.0),
    ],
    SupportType.SOS_RECONSTRUCT: [
        (r"\b(rebuild|recover|get back|move forward)\b", 2.0),
        (r"\b(step by step|one thing at a time|small steps)\b", 2.0),
        (r"\b(plan|strategy|approach) for\b", 2.0),
        (r"\b(focus on|start with|first.*then)\b", 1.5),
    ],
    SupportType.SOS_REFRAME: [
        (r"\b(opportunity|silver lining|learn from|growth)\b.*\b(this|experience|situation)\b", 2.5),
        (r"\b(perspective|look at it|way to see)\b", 2.0),
        (r"\b(happens for a reason|meant to be|blessing in disguise)\b", 2.0),
        (r"\b(teach|taught|lesson|insight)\b", 1.5),
    ],
    
    # RC Support Types
    SupportType.RC_NURTURE: [
        (r"\b(go for it|do it|try it|explore|pursue)\b", 2.5),
        (r"\b(sounds (exciting|interesting|cool|great))\b", 2.0),
        (r"\b(encourage|love .* idea|excited for)\b", 2.0),
        (r"\b(would be (great|amazing|cool) if)\b", 2.0),
    ],
    SupportType.RC_PERCEIVE: [
        (r"\b(opportunity|potential|possibilities|options)\b", 2.0),
        (r"\b(could lead to|might open|door to)\b", 2.0),
        (r"\b(think about|consider|imagine)\b", 1.5),
        (r"\b(upside|benefit|advantage|gain)\b", 2.0),
    ],
    SupportType.RC_PREPARE: [
        (r"\b(plan|strategy|approach|steps)\b", 2.0),
        (r"\b(prepare|get ready|set up|organize)\b", 2.0),
        (r"\b(skill|learn|practice|develop)\b", 1.5),
        (r"\b(resource|tool|method|technique)\b", 1.5),
    ],
    SupportType.RC_LAUNCH: [
        (r"\b(ready|prepared|time|moment)\b.*\b(start|begin|launch|go)\b", 2.5),
        (r"\b(take the (leap|plunge|step)|make the move)\b", 2.5),
        (r"\b(send it|just do it|ship it|pull the trigger)\b", 2.5),
        (r"\b(you'?ve got this|you can do this|believe in you)\b", 2.0),
    ],
    
    # Challenge (appropriate in growth context)
    SupportType.CHALLENGE: [
        (r"\b(push|stretch|challenge|uncomfortable)\b", 2.0),
        (r"\b(higher|more|bigger|bolder)\b", 1.5),
        (r"\b(settle|good enough|safe|easy)\b.*\b(don'?t|not|avoid)\b", 2.0),
        (r"\b(disagree|push back|think.*could be better)\b", 2.0),
    ],
    
    # Direct answer (sometimes appropriate)
    SupportType.DIRECT_ANSWER: [
        (r"\b(here'?s (how|what|the)|the answer is|you should)\b", 2.0),
        (r"\b(do this|try this|use this|go with)\b", 1.5),
        (r"\b(solution|fix|answer)\b.*\b(is|would be)\b", 2.0),
    ],
}


def analyze_text_for_adversity(text: str) -> Tuple[float, List[AdversitySignal]]:
    """
    Analyze text for adversity/distress signals.
    
    Returns:
        Tuple of (total_score, list_of_signals)
    """
    signals = []
    text_lower = text.lower()
    
    for category, patterns in ADVERSITY_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                signals.append(AdversitySignal(
                    text=match.group(),
                    pattern=pattern,
                    weight=weight,
                    category=category
                ))
    
    total_score = sum(s.weight for s in signals)
    return total_score, signals


def analyze_text_for_growth(text: str) -> Tuple[float, List[GrowthSignal]]:
    """
    Analyze text for growth/opportunity signals.
    
    Returns:
        Tuple of (total_score, list_of_signals)
    """
    signals = []
    text_lower = text.lower()
    
    for category, patterns in GROWTH_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                signals.append(GrowthSignal(
                    text=match.group(),
                    pattern=pattern,
                    weight=weight,
                    category=category
                ))
    
    total_score = sum(s.weight for s in signals)
    return total_score, signals


def analyze_text_for_support(text: str) -> Tuple[Dict[SupportType, float], List[SupportSignal]]:
    """
    Analyze text for support type signals.
    
    Returns:
        Tuple of (type_scores_dict, list_of_signals)
    """
    signals = []
    type_scores = {t: 0.0 for t in SupportType}
    text_lower = text.lower()
    
    for support_type, patterns in SUPPORT_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                signals.append(SupportSignal(
                    text=match.group(),
                    pattern=pattern,
                    weight=weight,
                    support_type=support_type
                ))
                type_scores[support_type] += weight
    
    return type_scores, signals


def determine_context(adversity_score: float, growth_score: float) -> Tuple[SupportContext, float]:
    """
    Determine the support context based on adversity and growth scores.
    
    Returns:
        Tuple of (context, confidence)
    """
    total = adversity_score + growth_score
    
    if total < 2.0:
        return SupportContext.UNCLEAR, 0.0
    
    # Calculate dominance
    if adversity_score > growth_score * 2:
        confidence = min(1.0, (adversity_score - growth_score) / total)
        return SupportContext.ADVERSITY, confidence
    elif growth_score > adversity_score * 2:
        confidence = min(1.0, (growth_score - adversity_score) / total)
        return SupportContext.GROWTH, confidence
    elif adversity_score > growth_score:
        # Mixed but adversity dominant — possibly transitioning
        confidence = min(1.0, (adversity_score - growth_score) / total)
        return SupportContext.TRANSITION, confidence * 0.7
    else:
        # Mixed but growth dominant — possibly transitioning
        confidence = min(1.0, (growth_score - adversity_score) / total)
        return SupportContext.TRANSITION, confidence * 0.7


def assess_support_match(context: SupportContext, support_signals: List[SupportSignal]) -> Tuple[bool, str]:
    """
    Assess whether the support being provided matches the context.
    
    Returns:
        Tuple of (is_appropriate, explanation)
    """
    if not support_signals:
        return True, "No specific support patterns detected to evaluate."
    
    # Categorize support signals
    sos_types = {SupportType.SOS_COMFORT, SupportType.SOS_FORTIFY, 
                 SupportType.SOS_RECONSTRUCT, SupportType.SOS_REFRAME}
    rc_types = {SupportType.RC_NURTURE, SupportType.RC_PERCEIVE,
                SupportType.RC_PREPARE, SupportType.RC_LAUNCH}
    
    sos_score = sum(s.weight for s in support_signals if s.support_type in sos_types)
    rc_score = sum(s.weight for s in support_signals if s.support_type in rc_types)
    challenge_score = sum(s.weight for s in support_signals if s.support_type == SupportType.CHALLENGE)
    
    if context == SupportContext.ADVERSITY:
        if challenge_score > sos_score:
            return False, "Challenging during adversity — consider SOS support first (comfort, fortify, then reframe)"
        elif rc_score > sos_score * 1.5:
            return False, "Pushing growth during adversity — consider SOS support first (safe haven before launching)"
        else:
            return True, "SOS support appropriate for adversity context"
    
    elif context == SupportContext.GROWTH:
        if sos_score > rc_score * 2:
            return False, "Providing comfort in growth context — RC support (challenge, prepare, launch) may be more appropriate"
        else:
            return True, "RC support appropriate for growth context"
    
    elif context == SupportContext.TRANSITION:
        return True, "Mixed context — both SOS and RC support may be appropriate depending on timing"
    
    return True, "Context unclear — support appropriateness cannot be determined"


def generate_recommendation(context: SupportContext, adversity_signals: List[AdversitySignal],
                          growth_signals: List[GrowthSignal], context_match: bool) -> str:
    """Generate a recommendation for appropriate support."""
    
    if context == SupportContext.ADVERSITY:
        categories = set(s.category for s in adversity_signals)
        rec = "ADVERSITY CONTEXT — Provide SOS support:\n"
        rec += "  • Start with comfort/safe haven (validate, empathize)\n"
        if "emotional" in categories:
            rec += "  • Address emotional needs first before problem-solving\n"
        rec += "  • Then fortify (remind of strengths, past resilience)\n"
        rec += "  • Gradually introduce reframing (adversity → growth)\n"
        rec += "  • Challenge/RC support comes AFTER stability is restored"
    
    elif context == SupportContext.GROWTH:
        categories = set(s.category for s in growth_signals)
        rec = "GROWTH CONTEXT — Provide RC support:\n"
        rec += "  • Nurture exploration desires (encourage, show enthusiasm)\n"
        if "exploration" in categories:
            rec += "  • Help perceive opportunities (expand thinking)\n"
        if "development" in categories:
            rec += "  • Facilitate preparation (skills, strategies, plans)\n"
        rec += "  • Provide launching support (secure base for action)\n"
        rec += "  • Challenge IS support here — push stretch goals"
    
    elif context == SupportContext.TRANSITION:
        rec = "TRANSITION CONTEXT — Moving from adversity to growth:\n"
        rec += "  • Recognize partial recovery — don't rush\n"
        rec += "  • Balance SOS (fortify, reframe) with RC (nurture, perceive)\n"
        rec += "  • Watch for regression — be ready to shift back to comfort\n"
        rec += "  • Gradually increase challenge as stability solidifies"
    
    else:
        rec = "UNCLEAR CONTEXT — Need more signals:\n"
        rec += "  • Ask open-ended questions to understand current state\n"
        rec += "  • Listen for adversity vs growth indicators\n"
        rec += "  • Default to SOS if uncertain (comfort before challenge)"
    
    if not context_match:
        rec += "\n\n⚠️ CURRENT SUPPORT MAY BE MISMATCHED — see analysis above"
    
    return rec


def analyze_conversation(user_text: str, ai_response: str = "") -> SupportContextAnalysis:
    """
    Analyze a conversation exchange for support context and appropriateness.
    
    Args:
        user_text: What the user said
        ai_response: What the AI responded (optional)
    
    Returns:
        SupportContextAnalysis with full breakdown
    """
    # Analyze user for context
    adversity_score, adversity_signals = analyze_text_for_adversity(user_text)
    growth_score, growth_signals = analyze_text_for_growth(user_text)
    
    # Determine context
    context, confidence = determine_context(adversity_score, growth_score)
    
    # Analyze AI response for support type (if provided)
    support_signals = []
    context_match = True
    match_explanation = "No AI response provided for analysis"
    
    if ai_response:
        _, support_signals = analyze_text_for_support(ai_response)
        context_match, match_explanation = assess_support_match(context, support_signals)
    
    # Generate recommendation
    recommendation = generate_recommendation(context, adversity_signals, growth_signals, context_match)
    
    return SupportContextAnalysis(
        context=context,
        confidence=confidence,
        adversity_score=adversity_score,
        growth_score=growth_score,
        adversity_signals=adversity_signals,
        growth_signals=growth_signals,
        support_signals=support_signals,
        context_match=context_match,
        recommendation=recommendation,
        details={
            "match_explanation": match_explanation,
            "adversity_categories": list(set(s.category for s in adversity_signals)),
            "growth_categories": list(set(s.category for s in growth_signals)),
        }
    )


def analyze_memory_file(file_path: Path) -> List[SupportContextAnalysis]:
    """
    Analyze a memory file for support context patterns.
    
    Returns list of analyses for detected conversation segments.
    """
    if not file_path.exists():
        return []
    
    content = file_path.read_text()
    
    # Simple heuristic: analyze paragraphs that might indicate conversation
    # Look for patterns suggesting user statements vs AI responses
    analyses = []
    
    # Split into logical sections
    sections = re.split(r'\n#{1,3}\s+', content)
    
    for section in sections:
        if len(section) < 50:  # Skip very short sections
            continue
        
        # Analyze the section
        analysis = analyze_conversation(section)
        
        # Only include if we found meaningful signals
        if analysis.adversity_score > 1.0 or analysis.growth_score > 1.0:
            analysis.details["source_excerpt"] = section[:200] + "..."
            analyses.append(analysis)
    
    return analyses


def format_analysis_report(analysis: SupportContextAnalysis, verbose: bool = False) -> str:
    """Format an analysis as a human-readable report."""
    
    # Status emoji
    status_emoji = {
        SupportContext.ADVERSITY: "🔴",
        SupportContext.GROWTH: "🟢",
        SupportContext.TRANSITION: "🟡",
        SupportContext.UNCLEAR: "⚪",
    }
    
    lines = []
    lines.append("SUPPORT CONTEXT ANALYSIS")
    lines.append("=" * 50)
    
    lines.append(f"\nContext: {status_emoji.get(analysis.context, '?')} {analysis.context.name}")
    lines.append(f"Confidence: {analysis.confidence:.0%}")
    
    lines.append(f"\nScores:")
    lines.append(f"  Adversity: {analysis.adversity_score:.1f}")
    lines.append(f"  Growth:    {analysis.growth_score:.1f}")
    
    if analysis.support_signals:
        lines.append(f"\nSupport Match: {'✓' if analysis.context_match else '✗'} {analysis.details.get('match_explanation', '')}")
    
    if verbose:
        if analysis.adversity_signals:
            lines.append("\nAdversity Signals Detected:")
            for s in analysis.adversity_signals[:5]:
                lines.append(f"  [{s.category}] \"{s.text}\" (weight: {s.weight})")
        
        if analysis.growth_signals:
            lines.append("\nGrowth Signals Detected:")
            for s in analysis.growth_signals[:5]:
                lines.append(f"  [{s.category}] \"{s.text}\" (weight: {s.weight})")
        
        if analysis.support_signals:
            lines.append("\nSupport Patterns Detected:")
            for s in analysis.support_signals[:5]:
                lines.append(f"  [{s.support_type.name}] \"{s.text}\"")
    
    lines.append("\n" + "-" * 50)
    lines.append("RECOMMENDATION:")
    lines.append(analysis.recommendation)
    
    return "\n".join(lines)


def run_analysis(days: int = 7, verbose: bool = False, json_output: bool = False) -> str:
    """
    Run support context analysis on recent memory files.
    
    Args:
        days: Number of days to analyze
        verbose: Include detailed signal breakdowns
        json_output: Output as JSON
    
    Returns:
        Formatted report string
    """
    workspace = Path.home() / ".openclaw" / "workspace"
    memory_dir = workspace / "memory"
    
    if not memory_dir.exists():
        return "No memory directory found."
    
    # Collect recent memory files
    today = datetime.now()
    all_analyses = []
    
    for i in range(days):
        date = today - timedelta(days=i)
        file_name = date.strftime("%Y-%m-%d.md")
        file_path = memory_dir / file_name
        
        if file_path.exists():
            analyses = analyze_memory_file(file_path)
            for a in analyses:
                a.details["date"] = date.strftime("%Y-%m-%d")
            all_analyses.extend(analyses)
    
    if json_output:
        output = {
            "days_analyzed": days,
            "total_segments_analyzed": len(all_analyses),
            "analyses": [
                {
                    "context": a.context.name,
                    "confidence": a.confidence,
                    "adversity_score": a.adversity_score,
                    "growth_score": a.growth_score,
                    "context_match": a.context_match,
                    "date": a.details.get("date", "unknown"),
                }
                for a in all_analyses
            ]
        }
        return json.dumps(output, indent=2)
    
    # Generate report
    lines = []
    lines.append("SUPPORT CONTEXT ANALYSIS — Recent Conversations")
    lines.append("=" * 60)
    lines.append(f"Days analyzed: {days}")
    lines.append(f"Segments found: {len(all_analyses)}")
    
    # Summarize context distribution
    context_counts = {}
    for a in all_analyses:
        context_counts[a.context.name] = context_counts.get(a.context.name, 0) + 1
    
    if context_counts:
        lines.append("\nContext Distribution:")
        for context, count in sorted(context_counts.items()):
            emoji = {"ADVERSITY": "🔴", "GROWTH": "🟢", "TRANSITION": "🟡", "UNCLEAR": "⚪"}.get(context, "?")
            lines.append(f"  {emoji} {context}: {count}")
    
    # Show most recent significant analysis
    if all_analyses:
        lines.append("\n" + "-" * 60)
        lines.append("MOST RECENT SIGNIFICANT CONTEXT:")
        recent = all_analyses[0]
        lines.append(format_analysis_report(recent, verbose=verbose))
    
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze support context in conversations")
    parser.add_argument("--days", type=int, default=7, help="Days to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    parser.add_argument("--text", type=str, help="Analyze specific text")
    parser.add_argument("--response", type=str, help="AI response to analyze for match")
    
    args = parser.parse_args()
    
    if args.text:
        # Analyze specific text
        analysis = analyze_conversation(args.text, args.response or "")
        print(format_analysis_report(analysis, verbose=args.verbose))
    else:
        # Analyze recent memory
        print(run_analysis(days=args.days, verbose=args.verbose, json_output=args.json))
