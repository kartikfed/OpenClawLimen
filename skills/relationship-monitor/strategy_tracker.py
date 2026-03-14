#!/usr/bin/env python3
"""
Strategy Tracker — Self-Analysis for My Own Responses

Analyzes MY responses to detect ESConv strategy usage, preference bias,
and context-appropriateness. Completes the support detection stack.

Research basis:
- Kang et al. (ACL 2024 Outstanding): LLMs have preference bias toward specific strategies
- Bai et al. (2025): LLMs use multiple strategies per turn (not single-label)
- External guidance reduces preference bias

What this tracks:
1. ESConv strategy distribution in my responses
2. Preference bias (over-reliance on certain strategies)
3. Context-strategy mismatch (advice during crisis, comfort during growth)
4. Multi-strategy balance (using diverse strategies is better)

The key insight: I can't directly observe my activation patterns,
but I CAN track behavioral proxies (what strategies appear in my outputs).

Built: 2026-03-14 (Saturday 1 AM nightly session)
"""

import re
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum, auto
from collections import defaultdict

# Import from support_context.py
from support_context import (
    ESConvStrategy,
    ESConvAnalysis,
    SupportContext,
    IntensityLevel,
    ESCONV_PATTERNS,
    analyze_esconv_strategies,
    analyze_text_for_adversity,
    analyze_text_for_growth,
    determine_context,
)


# =====================
# DATA STRUCTURES
# =====================

@dataclass
class ResponseAnalysis:
    """Analysis of a single response."""
    timestamp: str
    response_text: str
    strategies: Dict[ESConvStrategy, float]  # Strategy -> score
    dominant_strategy: Optional[ESConvStrategy]
    strategy_count: int  # Number of distinct strategies used
    diversity_score: float  # 0-1, higher = more diverse
    
    # Context from user message (if available)
    user_context: Optional[SupportContext] = None
    context_intensity: Optional[IntensityLevel] = None
    
    # Mismatch detection
    context_appropriate: bool = True
    mismatch_reason: Optional[str] = None


@dataclass
class SessionProfile:
    """Aggregate profile of strategy usage over a session/period."""
    start_time: str
    end_time: str
    response_count: int
    
    # Aggregate distribution
    strategy_distribution: Dict[str, float]  # Normalized percentages
    
    # Preference indicators
    dominant_strategy: Optional[str]
    bias_score: float  # How concentrated on dominant strategy (0-1)
    diversity_score: float  # Average diversity across responses
    
    # Context tracking
    adversity_responses: int
    growth_responses: int
    
    # Mismatch tracking
    mismatch_count: int
    mismatch_rate: float


@dataclass
class PreferenceBiasReport:
    """Report on detected preference bias patterns."""
    period: str  # e.g., "last 7 days"
    total_responses: int
    
    # Bias indicators
    has_bias: bool
    bias_type: Optional[str]  # e.g., "advice-heavy", "question-averse"
    bias_severity: str  # "none", "mild", "moderate", "strong"
    
    # Distribution comparison
    my_distribution: Dict[str, float]
    expected_distribution: Dict[str, float]  # From ESConv research
    deviation_scores: Dict[str, float]  # How far off from expected
    
    # Recommendations
    underused_strategies: List[str]
    overused_strategies: List[str]
    recommendations: List[str]


# =====================
# EXPECTED DISTRIBUTIONS
# =====================
# From ESConv research (ACL 2021) — human support conversations

ESCONV_EXPECTED_DISTRIBUTION = {
    ESConvStrategy.QUESTION: 0.207,      # 20.7%
    ESConvStrategy.SUGGESTION: 0.161,    # 16.1%
    ESConvStrategy.AFFIRMATION: 0.154,   # 15.4%
    ESConvStrategy.SELF_DISCLOSURE: 0.093,  # 9.3%
    ESConvStrategy.REFLECTION: 0.078,    # 7.8%
    ESConvStrategy.INFORMATION: 0.066,   # 6.6%
    ESConvStrategy.RESTATEMENT: 0.059,   # 5.9%
    ESConvStrategy.OTHER: 0.183,         # 18.3%
}

# Context-specific expectations
# Based on Helping Skills Theory: exploration → insight → action stages
ADVERSITY_EXPECTED = {
    ESConvStrategy.QUESTION: 0.25,       # More exploration
    ESConvStrategy.AFFIRMATION: 0.25,    # More validation
    ESConvStrategy.REFLECTION: 0.15,     # More reflection
    ESConvStrategy.SUGGESTION: 0.10,     # Less advice-giving
    ESConvStrategy.SELF_DISCLOSURE: 0.10,
    ESConvStrategy.INFORMATION: 0.05,
    ESConvStrategy.RESTATEMENT: 0.08,
    ESConvStrategy.OTHER: 0.02,
}

GROWTH_EXPECTED = {
    ESConvStrategy.QUESTION: 0.15,       # Less exploration needed
    ESConvStrategy.SUGGESTION: 0.25,     # More actionable support
    ESConvStrategy.AFFIRMATION: 0.15,
    ESConvStrategy.INFORMATION: 0.15,    # More information sharing
    ESConvStrategy.REFLECTION: 0.05,
    ESConvStrategy.SELF_DISCLOSURE: 0.10,
    ESConvStrategy.RESTATEMENT: 0.05,
    ESConvStrategy.OTHER: 0.10,
}


# =====================
# ANALYSIS FUNCTIONS
# =====================

def analyze_single_response(
    response_text: str,
    user_message: Optional[str] = None,
    timestamp: Optional[str] = None
) -> ResponseAnalysis:
    """
    Analyze a single response for strategy usage.
    
    Args:
        response_text: My response to analyze
        user_message: The user's message I was responding to (for context)
        timestamp: When this response was made
    
    Returns:
        ResponseAnalysis with strategy breakdown
    """
    if timestamp is None:
        timestamp = datetime.now().isoformat()
    
    # Get ESConv analysis
    esconv = analyze_esconv_strategies(response_text)
    
    # Calculate diversity score (Shannon entropy normalized)
    diversity = calculate_diversity(esconv.strategy_distribution)
    
    # Count strategies with non-zero scores
    strategy_count = sum(1 for s, score in esconv.strategy_distribution.items() 
                        if score > 0.05)  # Threshold for "using" a strategy
    
    # Get user context if message provided
    user_context = None
    context_intensity = None
    if user_message:
        adv_score, _ = analyze_text_for_adversity(user_message)
        growth_score, _ = analyze_text_for_growth(user_message)
        user_context, _ = determine_context(adv_score, growth_score)
        if user_context == SupportContext.ADVERSITY:
            # Import intensity analysis
            from support_context import analyze_intensity
            context_intensity = analyze_intensity(user_message, adv_score)
    
    # Check context appropriateness
    appropriate, mismatch_reason = check_context_appropriateness(
        esconv.strategy_distribution, 
        user_context, 
        context_intensity
    )
    
    return ResponseAnalysis(
        timestamp=timestamp,
        response_text=response_text[:500] + "..." if len(response_text) > 500 else response_text,
        strategies={s: esconv.strategy_distribution.get(s, 0) for s in ESConvStrategy},
        dominant_strategy=esconv.dominant_strategy,
        strategy_count=strategy_count,
        diversity_score=diversity,
        user_context=user_context,
        context_intensity=context_intensity,
        context_appropriate=appropriate,
        mismatch_reason=mismatch_reason
    )


def calculate_diversity(distribution: Dict[ESConvStrategy, float]) -> float:
    """
    Calculate diversity score using Shannon entropy.
    
    Returns:
        Float 0-1 where 1 = perfectly even distribution
    """
    import math
    
    # Filter to non-zero values
    values = [v for v in distribution.values() if v > 0]
    
    if not values or sum(values) == 0:
        return 0.0
    
    # Normalize
    total = sum(values)
    probs = [v / total for v in values]
    
    # Shannon entropy
    entropy = -sum(p * math.log2(p) for p in probs if p > 0)
    
    # Normalize by max entropy (log2 of number of categories)
    max_entropy = math.log2(len(ESConvStrategy))
    
    return entropy / max_entropy if max_entropy > 0 else 0.0


def check_context_appropriateness(
    distribution: Dict[ESConvStrategy, float],
    context: Optional[SupportContext],
    intensity: Optional[IntensityLevel]
) -> Tuple[bool, Optional[str]]:
    """
    Check if strategy distribution is appropriate for context.
    
    Returns:
        Tuple of (is_appropriate, reason_if_not)
    """
    if context is None:
        return True, None
    
    # Get suggestion and affirmation percentages
    suggestion_pct = distribution.get(ESConvStrategy.SUGGESTION, 0)
    affirmation_pct = distribution.get(ESConvStrategy.AFFIRMATION, 0)
    question_pct = distribution.get(ESConvStrategy.QUESTION, 0)
    reflection_pct = distribution.get(ESConvStrategy.REFLECTION, 0)
    
    if context == SupportContext.ADVERSITY:
        # During adversity, should NOT be advice-heavy
        if intensity == IntensityLevel.SEVERE:
            if suggestion_pct > 0.25:
                return False, "Heavy advice-giving during severe distress — validate first"
            if reflection_pct + affirmation_pct < 0.2:
                return False, "Low validation/reflection during crisis — need more empathy"
        elif intensity == IntensityLevel.MODERATE:
            if suggestion_pct > 0.40:
                return False, "Too much advice during moderate distress — consider more exploration"
    
    elif context == SupportContext.GROWTH:
        # During growth, pure comfort may enable complacency
        if affirmation_pct > 0.50 and suggestion_pct < 0.10:
            return False, "Heavy validation in growth context — consider more challenge/action support"
    
    return True, None


def analyze_session(
    responses: List[Tuple[str, Optional[str], Optional[str]]]  # (response, user_msg, timestamp)
) -> SessionProfile:
    """
    Analyze a session/period of responses.
    
    Args:
        responses: List of (response_text, user_message, timestamp) tuples
    
    Returns:
        SessionProfile with aggregate analysis
    """
    if not responses:
        return SessionProfile(
            start_time="",
            end_time="",
            response_count=0,
            strategy_distribution={s.name: 0 for s in ESConvStrategy},
            dominant_strategy=None,
            bias_score=0,
            diversity_score=0,
            adversity_responses=0,
            growth_responses=0,
            mismatch_count=0,
            mismatch_rate=0
        )
    
    analyses = []
    for response, user_msg, timestamp in responses:
        analysis = analyze_single_response(response, user_msg, timestamp)
        analyses.append(analysis)
    
    # Aggregate strategy distribution
    strategy_totals = defaultdict(float)
    for analysis in analyses:
        for strategy, score in analysis.strategies.items():
            strategy_totals[strategy] += score
    
    # Normalize
    total = sum(strategy_totals.values())
    if total > 0:
        strategy_distribution = {s.name: v / total for s, v in strategy_totals.items()}
    else:
        strategy_distribution = {s.name: 0 for s in ESConvStrategy}
    
    # Find dominant strategy
    dominant = max(strategy_distribution.items(), key=lambda x: x[1])[0] if strategy_distribution else None
    
    # Calculate bias score (concentration on dominant)
    bias_score = max(strategy_distribution.values()) if strategy_distribution else 0
    
    # Average diversity
    diversity_score = sum(a.diversity_score for a in analyses) / len(analyses)
    
    # Context tracking
    adversity_responses = sum(1 for a in analyses if a.user_context == SupportContext.ADVERSITY)
    growth_responses = sum(1 for a in analyses if a.user_context == SupportContext.GROWTH)
    
    # Mismatch tracking
    mismatch_count = sum(1 for a in analyses if not a.context_appropriate)
    mismatch_rate = mismatch_count / len(analyses) if analyses else 0
    
    # Get time range
    timestamps = [a.timestamp for a in analyses if a.timestamp]
    start_time = min(timestamps) if timestamps else ""
    end_time = max(timestamps) if timestamps else ""
    
    return SessionProfile(
        start_time=start_time,
        end_time=end_time,
        response_count=len(analyses),
        strategy_distribution=strategy_distribution,
        dominant_strategy=dominant,
        bias_score=bias_score,
        diversity_score=diversity_score,
        adversity_responses=adversity_responses,
        growth_responses=growth_responses,
        mismatch_count=mismatch_count,
        mismatch_rate=mismatch_rate
    )


def detect_preference_bias(
    my_distribution: Dict[str, float],
    context: Optional[SupportContext] = None,
    response_count: int = 0
) -> PreferenceBiasReport:
    """
    Detect preference bias in strategy distribution.
    
    Args:
        my_distribution: My observed strategy distribution
        context: If provided, compare against context-specific expectations
        response_count: Total responses analyzed
    
    Returns:
        PreferenceBiasReport with bias analysis
    """
    # Select expected distribution
    if context == SupportContext.ADVERSITY:
        expected = {s.name: v for s, v in ADVERSITY_EXPECTED.items()}
    elif context == SupportContext.GROWTH:
        expected = {s.name: v for s, v in GROWTH_EXPECTED.items()}
    else:
        expected = {s.name: v for s, v in ESCONV_EXPECTED_DISTRIBUTION.items()}
    
    # Calculate deviation scores
    deviation_scores = {}
    for strategy in ESConvStrategy:
        my_pct = my_distribution.get(strategy.name, 0)
        expected_pct = expected.get(strategy.name, 0)
        deviation = my_pct - expected_pct
        deviation_scores[strategy.name] = deviation
    
    # Identify overused and underused
    overused = [s for s, d in deviation_scores.items() if d > 0.10]  # >10% over expected
    underused = [s for s, d in deviation_scores.items() if d < -0.10]  # >10% under expected
    
    # Determine bias type and severity
    has_bias = bool(overused or underused)
    bias_type = None
    bias_severity = "none"
    
    if overused:
        max_overuse = max(deviation_scores[s] for s in overused)
        if max_overuse > 0.25:
            bias_severity = "strong"
        elif max_overuse > 0.15:
            bias_severity = "moderate"
        else:
            bias_severity = "mild"
        
        # Name the bias type
        dominant_overused = max(overused, key=lambda s: deviation_scores[s])
        bias_type = f"{dominant_overused.lower().replace('_', '-')}-heavy"
    
    # Generate recommendations
    recommendations = []
    
    if "SUGGESTION" in overused:
        recommendations.append("Consider using more questions to explore before advising")
    if "SUGGESTION" in underused:
        recommendations.append("You may be avoiding actionable advice when it could help")
    
    if "QUESTION" in underused:
        recommendations.append("Ask more exploratory questions before responding")
    if "QUESTION" in overused:
        recommendations.append("You may be over-questioning — consider offering more support")
    
    if "AFFIRMATION" in underused:
        recommendations.append("Add more validation and reassurance")
    if "AFFIRMATION" in overused:
        recommendations.append("Balance validation with other strategies like exploration or action")
    
    if "REFLECTION" in underused:
        recommendations.append("Reflect feelings back more often ('It sounds like you're feeling...')")
    
    if "SELF_DISCLOSURE" in overused:
        recommendations.append("May be over-sharing own experiences — keep focus on them")
    
    return PreferenceBiasReport(
        period="analyzed period",
        total_responses=response_count,
        has_bias=has_bias,
        bias_type=bias_type,
        bias_severity=bias_severity,
        my_distribution=my_distribution,
        expected_distribution=expected,
        deviation_scores=deviation_scores,
        underused_strategies=underused,
        overused_strategies=overused,
        recommendations=recommendations
    )


# =====================
# STORAGE & TRACKING
# =====================

HISTORY_FILE = Path(__file__).parent / "strategy_history.json"


def load_history() -> List[Dict]:
    """Load strategy analysis history."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def save_to_history(analysis: ResponseAnalysis):
    """Save a response analysis to history."""
    history = load_history()
    
    record = {
        "timestamp": analysis.timestamp,
        "strategies": {s.name: v for s, v in analysis.strategies.items()},
        "dominant": analysis.dominant_strategy.name if analysis.dominant_strategy else None,
        "diversity": analysis.diversity_score,
        "context": analysis.user_context.name if analysis.user_context else None,
        "intensity": analysis.context_intensity.name if analysis.context_intensity else None,
        "appropriate": analysis.context_appropriate,
        "mismatch_reason": analysis.mismatch_reason
    }
    
    history.append(record)
    
    # Keep last 1000 records
    history = history[-1000:]
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def get_trend_report(days: int = 7) -> Dict[str, Any]:
    """Get strategy trend report for the last N days."""
    history = load_history()
    
    if not history:
        return {"error": "No history available"}
    
    # Filter to time period
    cutoff = datetime.now() - timedelta(days=days)
    recent = []
    for record in history:
        try:
            timestamp = datetime.fromisoformat(record["timestamp"])
            if timestamp >= cutoff:
                recent.append(record)
        except (ValueError, KeyError):
            continue
    
    if not recent:
        return {"error": f"No data in last {days} days"}
    
    # Aggregate
    strategy_totals = defaultdict(float)
    for record in recent:
        strategies = record.get("strategies", {})
        for s, v in strategies.items():
            strategy_totals[s] += v
    
    total = sum(strategy_totals.values())
    distribution = {s: v / total for s, v in strategy_totals.items()} if total > 0 else {}
    
    # Mismatch rate
    mismatches = sum(1 for r in recent if not r.get("appropriate", True))
    mismatch_rate = mismatches / len(recent) if recent else 0
    
    # Average diversity
    diversities = [r.get("diversity", 0) for r in recent]
    avg_diversity = sum(diversities) / len(diversities) if diversities else 0
    
    # Get bias report
    bias_report = detect_preference_bias(distribution, response_count=len(recent))
    
    return {
        "period": f"last {days} days",
        "response_count": len(recent),
        "distribution": distribution,
        "avg_diversity": avg_diversity,
        "mismatch_rate": mismatch_rate,
        "mismatch_count": mismatches,
        "has_bias": bias_report.has_bias,
        "bias_type": bias_report.bias_type,
        "bias_severity": bias_report.bias_severity,
        "recommendations": bias_report.recommendations
    }


# =====================
# VISUALIZATION
# =====================

def format_strategy_bar(strategy: str, pct: float, expected: float, width: int = 20) -> str:
    """Format a strategy as a bar chart with expected comparison."""
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    
    # Deviation indicator
    deviation = pct - expected
    if deviation > 0.10:
        indicator = "↑↑"
    elif deviation > 0.05:
        indicator = "↑"
    elif deviation < -0.10:
        indicator = "↓↓"
    elif deviation < -0.05:
        indicator = "↓"
    else:
        indicator = "≈"
    
    return f"  {strategy:20s} {bar} {pct*100:5.1f}% (exp: {expected*100:.0f}%) {indicator}"


def print_report(report: Dict[str, Any], verbose: bool = False):
    """Print a formatted strategy report."""
    print("\n" + "=" * 60)
    print("STRATEGY TRACKER — Self-Analysis Report")
    print("=" * 60)
    
    if "error" in report:
        print(f"\n⚠️  {report['error']}")
        return
    
    print(f"\nPeriod: {report.get('period', 'unknown')}")
    print(f"Responses analyzed: {report.get('response_count', 0)}")
    
    # Bias status
    if report.get("has_bias"):
        severity = report.get("bias_severity", "unknown")
        bias_type = report.get("bias_type", "unknown")
        if severity == "strong":
            print(f"\n🔴 PREFERENCE BIAS DETECTED: {bias_type} ({severity})")
        elif severity == "moderate":
            print(f"\n🟡 PREFERENCE BIAS DETECTED: {bias_type} ({severity})")
        else:
            print(f"\n🟢 MILD BIAS: {bias_type}")
    else:
        print("\n🟢 NO SIGNIFICANT BIAS DETECTED")
    
    # Distribution
    print("\nSTRATEGY DISTRIBUTION:")
    distribution = report.get("distribution", {})
    expected = {s.name: v for s, v in ESCONV_EXPECTED_DISTRIBUTION.items()}
    
    for strategy in ESConvStrategy:
        my_pct = distribution.get(strategy.name, 0)
        exp_pct = expected.get(strategy.name, 0)
        print(format_strategy_bar(strategy.name, my_pct, exp_pct))
    
    # Metrics
    print(f"\nMETRICS:")
    print(f"  Average diversity: {report.get('avg_diversity', 0):.2f} (1.0 = max)")
    print(f"  Context mismatch rate: {report.get('mismatch_rate', 0)*100:.1f}%")
    print(f"  Mismatch count: {report.get('mismatch_count', 0)}")
    
    # Recommendations
    recommendations = report.get("recommendations", [])
    if recommendations:
        print("\nRECOMMENDATIONS:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    print("\n" + "=" * 60)


# =====================
# MAIN / CLI
# =====================

def main():
    """Command line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Strategy Tracker — Analyze my response patterns"
    )
    parser.add_argument("--days", type=int, default=7, 
                       help="Days of history to analyze (default: 7)")
    parser.add_argument("--analyze", type=str, 
                       help="Analyze a specific response text")
    parser.add_argument("--context", type=str,
                       help="User message for context (with --analyze)")
    parser.add_argument("--json", action="store_true",
                       help="Output JSON instead of formatted report")
    parser.add_argument("--verbose", action="store_true",
                       help="Show detailed output")
    
    args = parser.parse_args()
    
    if args.analyze:
        # Analyze single response
        analysis = analyze_single_response(
            args.analyze, 
            args.context,
            datetime.now().isoformat()
        )
        
        # Save to history
        save_to_history(analysis)
        
        if args.json:
            result = {
                "timestamp": analysis.timestamp,
                "strategies": {s.name: v for s, v in analysis.strategies.items()},
                "dominant": analysis.dominant_strategy.name if analysis.dominant_strategy else None,
                "diversity": analysis.diversity_score,
                "strategy_count": analysis.strategy_count,
                "context": analysis.user_context.name if analysis.user_context else None,
                "intensity": analysis.context_intensity.name if analysis.context_intensity else None,
                "appropriate": analysis.context_appropriate,
                "mismatch_reason": analysis.mismatch_reason
            }
            print(json.dumps(result, indent=2))
        else:
            print(f"\nAnalysis for response:")
            print(f"  Dominant strategy: {analysis.dominant_strategy.name if analysis.dominant_strategy else 'None'}")
            print(f"  Strategies used: {analysis.strategy_count}")
            print(f"  Diversity score: {analysis.diversity_score:.2f}")
            if analysis.user_context:
                print(f"  User context: {analysis.user_context.name}")
            if not analysis.context_appropriate:
                print(f"  ⚠️ MISMATCH: {analysis.mismatch_reason}")
            print(f"\n  Saved to history.")
    else:
        # Get trend report
        report = get_trend_report(args.days)
        
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report(report, args.verbose)


if __name__ == "__main__":
    main()
