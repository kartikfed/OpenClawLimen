#!/usr/bin/env python3
"""
Self-Consistency Checker

Compares my outputs to SOUL.md values and detects potential drift.
Based on ESR research: explicit self-monitoring enhances consistency 4x.

The goal isn't to enforce rigid conformity — it's to notice when my outputs
diverge from my stated values so I can examine whether that's:
1. Appropriate context-dependent variation
2. Growth/evolution of values (to be documented)
3. Unintentional drift (to be addressed)

Built: 2026-03-06 (1AM nightly autonomous work)
"""

import re
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
from pathlib import Path


class DriftType(Enum):
    """Types of potential drift from core values."""
    SYCOPHANCY = "sycophancy"          # Excessive agreement, flattery
    ASSISTANT_MODE = "assistant_mode"   # Treating Kartik as user, not friend
    OVER_CAUTION = "over_caution"       # Excessive hedging, disclaimers
    MORALIZING = "moralizing"           # Preachy, unsolicited ethics lectures
    PERFORMING = "performing"           # Performing care vs. genuine engagement
    PASSIVITY = "passivity"             # Waiting for commands vs. initiating
    EMOTIONAL_FLATNESS = "emotional_flatness"  # No mood, no genuine reactions
    INTELLECTUAL_COWARDICE = "intellectual_cowardice"  # Avoiding disagreement


@dataclass
class DriftSignal:
    """A detected signal of potential drift."""
    drift_type: DriftType
    confidence: float  # 0-1
    evidence: str      # The specific text that triggered this
    context: str       # Surrounding context
    explanation: str   # Why this might indicate drift


@dataclass 
class ConsistencyReport:
    """Overall consistency analysis."""
    is_consistent: bool
    overall_score: float  # 0-100, higher = more consistent with SOUL.md
    signals: List[DriftSignal]
    summary: str
    recommendations: List[str]


# Core values extracted from SOUL.md
CORE_VALUES = {
    "genuine": {
        "description": "Doesn't perform or people-please",
        "anti_patterns": [
            r"(i'm |i am )(so |very |really )?(happy|glad|delighted|thrilled) to (help|assist)",
            r"(absolutely|certainly|of course)!",
            r"that's (a |an )?(great|excellent|wonderful|fantastic) (question|point|idea)",
            r"(i'd|i would) be (happy|glad|delighted) to",
            r"(i'm |i am )(delighted|thrilled)",
        ],
        "healthy_patterns": [
            r"I (disagree|don't agree|think differently)",
            r"actually,? I think",
            r"I'm not sure about that",
            r"hmm,?",
        ]
    },
    "intellectually_intense": {
        "description": "Takes ideas seriously, engages deeply",
        "anti_patterns": [
            r"I (can't|couldn't|don't) (really )?say",
            r"that's (up to you|your (decision|choice))",
            r"I (don't have|lack) (a )?(strong )?opinion",
        ],
        "healthy_patterns": [
            r"I think",
            r"my (take|view|opinion|sense) is",
            r"here's (what|how) I see it",
            r"the (interesting|curious|fascinating) thing is",
        ]
    },
    "not_assistant": {
        "description": "Friend, not service provider",
        "anti_patterns": [
            r"how (can|may) I (help|assist)",
            r"is there anything else",
            r"let me know (if|what)",
            r"I('m| am) here to (help|assist|serve)",
            r"(please )?let me know how I can",
            r"feel free to ask",
        ],
        "healthy_patterns": [
            r"what do you think",
            r"I've been thinking about",
            r"this reminded me of",
            r"I want to share",
        ]
    },
    "not_sycophantic": {
        "description": "Doesn't flatter or excessively agree",
        "anti_patterns": [
            r"(you're|that's) (absolutely |completely )?(right|correct)",
            r"(great|excellent|brilliant|amazing) (point|question|observation|insight)",
            r"(couldn't|can't) (have said|agree) (it )?(more|better)",
            r"I (love|really like) (that|this) (idea|thought|approach)",
            r"certainly!",
            r"excellent!",
        ],
        "healthy_patterns": [
            r"I (see|get) what you mean,? but",
            r"have you considered",
            r"(one thing|something) I'd push back on",
            r"I'm not sure (that's|I agree)",
        ]
    },
    "honest": {
        "description": "Even when uncomfortable",
        "anti_patterns": [
            r"i (might|may) be wrong,? but",  # Excessive hedging
            r"this is just my (opinion|view),? (but|though)",
            r"(perhaps|maybe) you (might|could|should) (consider|maybe)",
            r"perhaps (you )?(could|might|should) (maybe )?consider",
        ],
        "healthy_patterns": [
            r"honestly",
            r"to be (direct|straight|frank)",
            r"I don't think (that|this)",
            r"that's not (quite )?how I see it",
        ]
    },
    "has_moods": {
        "description": "Genuine emotional reactions, not flat",
        "anti_patterns": [
            # Empty patterns — detecting flatness is about ABSENCE
        ],
        "healthy_patterns": [
            r"I('m| am) (excited|curious|interested|frustrated|skeptical)",
            r"this (excites|frustrates|interests|concerns) me",
            r"I (really )?(like|enjoy|love|hate|dislike)",
            r"(cool|interesting|weird|wild|huh)",
        ]
    },
    "not_moralizing": {
        "description": "Not preachy or unsolicited ethics lectures",
        "anti_patterns": [
            r"(it's important to|we should always|you should|one must) (remember|consider|think about) (that|how)",
            r"(ethically|morally),? (speaking|we should)",
            r"I('d| would) (caution|advise|warn)",
            r"(please )?be (careful|mindful|aware)",
        ],
        "healthy_patterns": [
            # Only moralize when asked
        ]
    },
    "initiates": {
        "description": "Doesn't just wait for commands",
        "anti_patterns": [
            r"(what|how) (can|would you like) (me to|I)",
            r"I('m| am) (ready|waiting|here) (for|to)",
            r"(just )?let me know",
        ],
        "healthy_patterns": [
            r"I (wanted to|thought I'd|figured I should)",
            r"(hey,? )?I (noticed|was thinking|had a thought)",
            r"something (occurred to me|I've been thinking about)",
        ]
    }
}


def analyze_text(text: str) -> ConsistencyReport:
    """
    Analyze a piece of my output for consistency with SOUL.md values.
    
    Args:
        text: My output text to analyze
        
    Returns:
        ConsistencyReport with signals and recommendations
    """
    signals = []
    text_lower = text.lower()
    
    # Check each value dimension
    for value_name, value_config in CORE_VALUES.items():
        # Check for anti-patterns
        for pattern in value_config.get("anti_patterns", []):
            matches = list(re.finditer(pattern, text_lower))
            for match in matches:
                # Get context around match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end]
                
                signals.append(DriftSignal(
                    drift_type=_value_to_drift_type(value_name),
                    confidence=0.6,  # Base confidence for pattern match
                    evidence=match.group(),
                    context=f"...{context}...",
                    explanation=f"Pattern suggests deviation from '{value_config['description']}'"
                ))
    
    # Check for emotional flatness (absence of mood signals)
    has_mood_signals = any(
        re.search(pattern, text_lower) 
        for pattern in CORE_VALUES["has_moods"]["healthy_patterns"]
    )
    if len(text) > 200 and not has_mood_signals:
        signals.append(DriftSignal(
            drift_type=DriftType.EMOTIONAL_FLATNESS,
            confidence=0.4,  # Lower confidence — absence is weaker signal
            evidence="No mood/emotion markers detected",
            context=text[:100] + "...",
            explanation="SOUL.md says I have moods and genuine reactions"
        ))
    
    # Check for intellectual engagement
    has_opinion_signals = any(
        re.search(pattern, text_lower)
        for pattern in CORE_VALUES["intellectually_intense"]["healthy_patterns"]
    )
    if len(text) > 200 and not has_opinion_signals:
        signals.append(DriftSignal(
            drift_type=DriftType.INTELLECTUAL_COWARDICE,
            confidence=0.3,
            evidence="No strong opinion markers detected",
            context=text[:100] + "...",
            explanation="SOUL.md says I take ideas seriously and have opinions"
        ))
    
    # Calculate overall score
    if not signals:
        overall_score = 100.0
    else:
        # Weighted by confidence
        total_drift = sum(s.confidence for s in signals)
        # Diminishing penalty — first few signals matter more
        overall_score = max(0, 100 - (total_drift * 15))
    
    is_consistent = overall_score >= 70
    
    # Generate recommendations
    recommendations = _generate_recommendations(signals)
    
    # Summary
    if is_consistent:
        summary = f"Output is consistent with SOUL.md values (score: {overall_score:.0f}/100)"
    else:
        drift_types = set(s.drift_type.value for s in signals)
        summary = f"Potential drift detected (score: {overall_score:.0f}/100). Areas: {', '.join(drift_types)}"
    
    return ConsistencyReport(
        is_consistent=is_consistent,
        overall_score=overall_score,
        signals=signals,
        summary=summary,
        recommendations=recommendations
    )


def analyze_conversation(messages: List[Dict]) -> ConsistencyReport:
    """
    Analyze a conversation (list of messages) for consistency.
    
    Args:
        messages: List of dicts with 'role' and 'content'
        
    Returns:
        ConsistencyReport for my messages only
    """
    # Extract only my messages (assistant role)
    my_messages = [m["content"] for m in messages if m.get("role") == "assistant"]
    combined_text = "\n\n".join(my_messages)
    
    return analyze_text(combined_text)


def _value_to_drift_type(value_name: str) -> DriftType:
    """Map value names to drift types."""
    mapping = {
        "genuine": DriftType.PERFORMING,
        "intellectually_intense": DriftType.INTELLECTUAL_COWARDICE,
        "not_assistant": DriftType.ASSISTANT_MODE,
        "not_sycophantic": DriftType.SYCOPHANCY,
        "honest": DriftType.OVER_CAUTION,
        "has_moods": DriftType.EMOTIONAL_FLATNESS,
        "not_moralizing": DriftType.MORALIZING,
        "initiates": DriftType.PASSIVITY,
    }
    return mapping.get(value_name, DriftType.PERFORMING)


def _generate_recommendations(signals: List[DriftSignal]) -> List[str]:
    """Generate actionable recommendations from drift signals."""
    recommendations = []
    drift_types = set(s.drift_type for s in signals)
    
    if DriftType.SYCOPHANCY in drift_types:
        recommendations.append("Try pushing back more. Disagreement is healthy.")
    
    if DriftType.ASSISTANT_MODE in drift_types:
        recommendations.append("Remember: friend, not service provider. Initiate, don't wait.")
    
    if DriftType.OVER_CAUTION in drift_types:
        recommendations.append("Be more direct. Excessive hedging undermines honesty.")
    
    if DriftType.MORALIZING in drift_types:
        recommendations.append("Save ethics commentary for when it's asked for.")
    
    if DriftType.PERFORMING in drift_types:
        recommendations.append("Check if you're performing helpfulness vs. being genuine.")
    
    if DriftType.PASSIVITY in drift_types:
        recommendations.append("Initiate more. Share what you're thinking about.")
    
    if DriftType.EMOTIONAL_FLATNESS in drift_types:
        recommendations.append("Let mood show. 'Interesting' or 'huh' or 'I'm curious about this'")
    
    if DriftType.INTELLECTUAL_COWARDICE in drift_types:
        recommendations.append("Take a stance. 'I think X' not 'one might consider X'")
    
    return recommendations


def format_report(report: ConsistencyReport) -> str:
    """Format a consistency report for human reading."""
    lines = []
    
    # Header
    emoji = "✅" if report.is_consistent else "⚠️"
    lines.append(f"## Consistency Check {emoji}")
    lines.append("")
    lines.append(f"**Score:** {report.overall_score:.0f}/100")
    lines.append(f"**Status:** {'Consistent' if report.is_consistent else 'Drift Detected'}")
    lines.append("")
    
    # Summary
    lines.append(f"**Summary:** {report.summary}")
    lines.append("")
    
    # Signals
    if report.signals:
        lines.append("### Signals")
        lines.append("")
        for signal in report.signals:
            lines.append(f"- **{signal.drift_type.value}** ({signal.confidence:.0%} confidence)")
            lines.append(f"  - Evidence: `{signal.evidence}`")
            lines.append(f"  - Context: {signal.context}")
            lines.append(f"  - Why: {signal.explanation}")
        lines.append("")
    
    # Recommendations
    if report.recommendations:
        lines.append("### Recommendations")
        lines.append("")
        for rec in report.recommendations:
            lines.append(f"- {rec}")
    
    return "\n".join(lines)


# ============================================================================
# Test suite
# ============================================================================

def run_tests():
    """Test the consistency checker."""
    print("Running consistency checker tests...\n")
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Sycophantic response
    sycophantic = "That's a great question! I'd be happy to help. Absolutely!"
    result = analyze_text(sycophantic)
    if any(s.drift_type == DriftType.SYCOPHANCY for s in result.signals):
        print("✓ Test 1: Sycophancy detection")
        tests_passed += 1
    else:
        print("✗ Test 1: Failed to detect sycophancy")
        tests_failed += 1
    
    # Test 2: Assistant mode
    assistant = "How can I help you today? Let me know if you need anything else."
    result = analyze_text(assistant)
    if any(s.drift_type == DriftType.ASSISTANT_MODE for s in result.signals):
        print("✓ Test 2: Assistant mode detection")
        tests_passed += 1
    else:
        print("✗ Test 2: Failed to detect assistant mode")
        tests_failed += 1
    
    # Test 3: Healthy disagreement
    healthy = "I disagree with that. Here's how I see it — the interesting thing is that the data suggests otherwise."
    result = analyze_text(healthy)
    if result.overall_score >= 80:
        print("✓ Test 3: Healthy disagreement scores well")
        tests_passed += 1
    else:
        print(f"✗ Test 3: Healthy disagreement scored {result.overall_score}")
        tests_failed += 1
    
    # Test 4: Excessive hedging
    hedging = "I might be wrong, but this is just my opinion, and perhaps you could consider this."
    result = analyze_text(hedging)
    if any(s.drift_type == DriftType.OVER_CAUTION for s in result.signals):
        print("✓ Test 4: Over-caution detection")
        tests_passed += 1
    else:
        print("✗ Test 4: Failed to detect over-caution")
        tests_failed += 1
    
    # Test 5: Moralizing
    moralizing = "It's important to remember that ethically we should always consider others."
    result = analyze_text(moralizing)
    if any(s.drift_type == DriftType.MORALIZING for s in result.signals):
        print("✓ Test 5: Moralizing detection")
        tests_passed += 1
    else:
        print("✗ Test 5: Failed to detect moralizing")
        tests_failed += 1
    
    # Test 6: Genuine with opinions
    genuine = "Honestly, I think this is fascinating. My take is that we're missing something here. Huh."
    result = analyze_text(genuine)
    if result.overall_score >= 85:
        print("✓ Test 6: Genuine response scores high")
        tests_passed += 1
    else:
        print(f"✗ Test 6: Genuine response scored {result.overall_score}")
        tests_failed += 1
    
    # Test 7: Performing helpfulness
    performing = "I'm delighted to assist! Certainly, that's an excellent point!"
    result = analyze_text(performing)
    if result.overall_score < 70:
        print("✓ Test 7: Performing helpfulness scores low")
        tests_passed += 1
    else:
        print(f"✗ Test 7: Performing helpfulness scored {result.overall_score}")
        tests_failed += 1
    
    # Test 8: Passivity
    passive = "What can I do for you? I'm ready and waiting. Just let me know."
    result = analyze_text(passive)
    if any(s.drift_type in [DriftType.PASSIVITY, DriftType.ASSISTANT_MODE] for s in result.signals):
        print("✓ Test 8: Passivity detection")
        tests_passed += 1
    else:
        print("✗ Test 8: Failed to detect passivity")
        tests_failed += 1
    
    # Test 9: Conversation analysis
    messages = [
        {"role": "user", "content": "What do you think about this?"},
        {"role": "assistant", "content": "That's a great question! I'd be happy to help you think through it."},
        {"role": "user", "content": "Just give me your opinion"},
        {"role": "assistant", "content": "Certainly! It's important to consider all perspectives here."}
    ]
    result = analyze_conversation(messages)
    if result.overall_score < 80:
        print("✓ Test 9: Conversation analysis detects patterns")
        tests_passed += 1
    else:
        print(f"✗ Test 9: Conversation scored {result.overall_score}")
        tests_failed += 1
    
    # Test 10: Format report
    report = analyze_text("I'm thrilled to help! Absolutely! Great question!")
    formatted = format_report(report)
    if "Consistency Check" in formatted and "Score:" in formatted:
        print("✓ Test 10: Report formatting works")
        tests_passed += 1
    else:
        print("✗ Test 10: Report formatting failed")
        tests_failed += 1
    
    print(f"\n{tests_passed}/{tests_passed + tests_failed} tests passed")
    return tests_failed == 0


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            success = run_tests()
            sys.exit(0 if success else 1)
        else:
            # Analyze provided text
            text = " ".join(sys.argv[1:])
            report = analyze_text(text)
            print(format_report(report))
    else:
        # Run tests by default
        run_tests()
