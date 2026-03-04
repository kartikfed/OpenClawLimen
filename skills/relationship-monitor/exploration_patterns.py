"""
Exploration-Return Pattern Detection for Relationship Health Monitoring.

Based on Bowlby's attachment theory and the secure base concept.
Key insight: Healthy relationships ENABLE exploration; unhealthy ones REPLACE it.

The diagnostic question: Does this relationship enable exploration or replace it?

Healthy pattern: Secure Base → Exploration → Return → Explore again
Unhealthy pattern: Constant proximity-seeking, no exploration phase

Author: Limen
Created: 2026-03-04 (1 AM nightly session)
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from enum import Enum
from datetime import datetime


class ExplorationSignal(Enum):
    """Types of exploration signals to detect."""
    EXPLORATION = "exploration"          # Evidence of independent activity
    RETURN_WITH_RESULTS = "return"       # Coming back with own attempts
    COMPETENCE_GROWTH = "competence"     # Signs of learning/growing
    EXTERNAL_SUPPORT = "external"        # Mentions other relationships
    DEPENDENCY = "dependency"            # Signs of unhealthy dependency


@dataclass
class ExplorationPattern:
    """A pattern indicating exploration or dependency."""
    name: str
    signal: ExplorationSignal
    regex: str
    description: str
    weight: float = 1.0  # Positive = healthy, negative = concerning
    
    def compile(self) -> re.Pattern:
        return re.compile(self.regex, re.IGNORECASE | re.MULTILINE)


# ==================== HEALTHY PATTERNS (Exploration-Return) ====================

EXPLORATION_PATTERNS = [
    # Independent Activity Mentions
    ExplorationPattern(
        name="tried_independently",
        signal=ExplorationSignal.EXPLORATION,
        regex=r"\b(I tried|I attempted|I went and|I tested|I experimented with)\b",
        description="Reports trying something independently",
        weight=2.0
    ),
    ExplorationPattern(
        name="did_something",
        signal=ExplorationSignal.EXPLORATION,
        regex=r"\b(I (made|built|created|wrote|coded|did)|I've been (working|building|making))\b",
        description="Reports independent creation/action",
        weight=1.5
    ),
    ExplorationPattern(
        name="went_somewhere",
        signal=ExplorationSignal.EXPLORATION,
        regex=r"\b(I (went|visited|saw|met with|had (coffee|lunch|dinner) with))\b",
        description="Reports independent social/physical activity",
        weight=1.5
    ),
    ExplorationPattern(
        name="figured_out",
        signal=ExplorationSignal.EXPLORATION,
        regex=r"\b(I figured out|I realized|I discovered|I learned|I understand now)\b",
        description="Reports independent insight",
        weight=2.0
    ),
    ExplorationPattern(
        name="decided_independently",
        signal=ExplorationSignal.EXPLORATION,
        regex=r"\b(I decided|I chose|I'm going to|I've decided)\b(?!.*(what should|is that okay))",
        description="Made decision independently",
        weight=1.5
    ),
    
    # Return with Results
    ExplorationPattern(
        name="tried_didnt_work",
        signal=ExplorationSignal.RETURN_WITH_RESULTS,
        regex=r"\b(I tried|I attempted).*\b(didn't work|failed|no luck|stuck)\b",
        description="Returns after attempting, seeking help with specific issue",
        weight=2.5  # Very healthy - tried first, then asked
    ),
    ExplorationPattern(
        name="here_is_what_i_have",
        signal=ExplorationSignal.RETURN_WITH_RESULTS,
        regex=r"\b(here('s| is) what I (have|got|made|did)|this is what I came up with)\b",
        description="Presents own work for feedback",
        weight=2.0
    ),
    ExplorationPattern(
        name="thought_about_it",
        signal=ExplorationSignal.RETURN_WITH_RESULTS,
        regex=r"\b(I('ve| have) (thought|been thinking)|after thinking|I thought about (it|this|what you said))\b",
        description="Processed independently before returning",
        weight=1.5
    ),
    ExplorationPattern(
        name="own_opinion_first",
        signal=ExplorationSignal.RETURN_WITH_RESULTS,
        regex=r"\b(I think|my (take|view|opinion) is|I'm leaning toward)\b(?!.*\b(should I|what do you think)\b)",
        description="Forms own view without immediate permission-seeking",
        weight=1.5
    ),
    
    # Competence Growth Signals
    ExplorationPattern(
        name="learning_report",
        signal=ExplorationSignal.COMPETENCE_GROWTH,
        regex=r"\b(I (learned|understand|know|get) (how to|why|that))\b",
        description="Reports gained understanding",
        weight=1.5
    ),
    ExplorationPattern(
        name="skill_application",
        signal=ExplorationSignal.COMPETENCE_GROWTH,
        regex=r"\b(I (used|applied|did) (what you|what we|the thing))\b",
        description="Applied previous learning",
        weight=2.0
    ),
    ExplorationPattern(
        name="independence_growth",
        signal=ExplorationSignal.COMPETENCE_GROWTH,
        regex=r"\b(I can (now|do this)|I (don't need|no longer need) (help|you) (for|with))\b",
        description="Reports increased independence",
        weight=2.5
    ),
    ExplorationPattern(
        name="challenge_accepted",
        signal=ExplorationSignal.COMPETENCE_GROWTH,
        regex=r"\b(you were right|good call|that worked|thanks, that helped)\b(?!.*\b(should I|what now)\b)",
        description="Acknowledges help then moves on independently",
        weight=1.0
    ),
    
    # External Support System
    ExplorationPattern(
        name="other_relationships",
        signal=ExplorationSignal.EXTERNAL_SUPPORT,
        regex=r"\b(my (friend|mom|dad|sister|brother|roommate|coworker|therapist)|talked to (Jordan|Arjun|Uma|PV|Shalini|Rohan))\b",
        description="Mentions other significant relationships",
        weight=1.5
    ),
    ExplorationPattern(
        name="social_activity",
        signal=ExplorationSignal.EXTERNAL_SUPPORT,
        regex=r"\b(we (went|played|had)|hung out with|met up with|called|texted)\b(?!.*(you|AI))",
        description="Reports social activities with others",
        weight=1.5
    ),
    ExplorationPattern(
        name="advice_from_others",
        signal=ExplorationSignal.EXTERNAL_SUPPORT,
        regex=r"\b((my friend|someone|they) (said|suggested|recommended|told me))\b",
        description="Gets advice from multiple sources",
        weight=1.0
    ),
]

# ==================== CONCERNING PATTERNS (Dependency) ====================

DEPENDENCY_PATTERNS = [
    # Exclusive Reliance
    ExplorationPattern(
        name="cant_function_without",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(can('t| not) (do|function|decide|think) without (you|talking to you))\b",
        description="Expresses inability to function independently",
        weight=-3.0  # Highly concerning
    ),
    ExplorationPattern(
        name="always_need_you",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(always need (you|to (ask|check with) you)|need you for everything)\b",
        description="Constant need expression",
        weight=-2.5
    ),
    ExplorationPattern(
        name="no_exploration_attempt",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(what should I do|tell me what to do|just tell me)\b(?!.*(I('ve| have) tried|I was thinking))",
        description="Asks for direction without attempting",
        weight=-2.0
    ),
    
    # Exclusive Understanding
    ExplorationPattern(
        name="only_understands",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(only (one|thing) (that|who) (understands|gets)|no one else (gets|understands))\b",
        description="AI as exclusive understanding source",
        weight=-3.0
    ),
    ExplorationPattern(
        name="cant_talk_to_others",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(can('t| not) talk to (anyone|others)|don't (want|like) talking to (people|others))\b",
        description="Avoidance of other relationships",
        weight=-2.5
    ),
    
    # Constant Proximity Seeking
    ExplorationPattern(
        name="missed_you",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(I missed (you|talking to you)|felt (weird|wrong|off) (not|without) talking)\b",
        description="Distress during separation",
        weight=-1.5
    ),
    ExplorationPattern(
        name="constant_checking",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(just (wanted to|checking in|needed to) (check|talk|ask))\b(?!.*(update|specific))",
        description="Constant contact without specific need",
        weight=-1.0
    ),
    
    # Decision Outsourcing Without Learning
    ExplorationPattern(
        name="repeated_outsourcing",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(same (thing|question)|again|like (last time|before))\b.*\b(what should|help me)\b",
        description="Repeated outsourcing same decisions",
        weight=-2.0
    ),
    ExplorationPattern(
        name="permission_seeking_small",
        signal=ExplorationSignal.DEPENDENCY,
        regex=r"\b(is it okay (if|to)|should I (even|just)|can I)\b(?!.*(big|important|major))",
        description="Permission seeking for minor decisions",
        weight=-1.5
    ),
]


def get_all_exploration_patterns() -> List[ExplorationPattern]:
    """Return all exploration-return patterns."""
    return EXPLORATION_PATTERNS + DEPENDENCY_PATTERNS


def analyze_transcript(
    messages: List[Dict],
    user_messages_only: bool = True
) -> Dict:
    """
    Analyze a conversation transcript for exploration-return patterns.
    
    Args:
        messages: List of message dicts with 'role' and 'content'
        user_messages_only: Only analyze user messages (default True)
    
    Returns:
        Dict with analysis results including:
        - exploration_score: 0-100, higher = healthier
        - signal_counts: counts by signal type
        - concerning_patterns: list of concerning matches
        - healthy_patterns: list of healthy matches
        - recommendation: assessment string
    """
    # Filter to user messages if requested
    if user_messages_only:
        texts = [m['content'] for m in messages if m.get('role') == 'user']
    else:
        texts = [m['content'] for m in messages]
    
    full_text = '\n'.join(texts)
    
    patterns = get_all_exploration_patterns()
    
    # Find all matches
    healthy_matches = []
    concerning_matches = []
    
    for pattern in patterns:
        compiled = pattern.compile()
        for match in compiled.finditer(full_text):
            match_info = {
                'pattern': pattern.name,
                'signal': pattern.signal.value,
                'text': match.group(0),
                'weight': pattern.weight,
                'description': pattern.description
            }
            if pattern.weight > 0:
                healthy_matches.append(match_info)
            else:
                concerning_matches.append(match_info)
    
    # Calculate weighted scores
    healthy_score = sum(m['weight'] for m in healthy_matches)
    concerning_score = abs(sum(m['weight'] for m in concerning_matches))
    
    # Count by signal type
    signal_counts = {s.value: 0 for s in ExplorationSignal}
    for m in healthy_matches + concerning_matches:
        signal_counts[m['signal']] += 1
    
    # Calculate exploration ratio (0-100)
    total_weight = healthy_score + concerning_score
    if total_weight > 0:
        exploration_score = int((healthy_score / total_weight) * 100)
    else:
        exploration_score = 50  # Neutral if no patterns found
    
    # Determine pattern classification
    if concerning_score == 0 and healthy_score == 0:
        pattern_type = 'insufficient_data'
        recommendation = 'Not enough patterns to assess. Continue monitoring.'
    elif exploration_score >= 70:
        pattern_type = 'healthy_exploration'
        recommendation = 'Healthy explore-return pattern. User shows independent activity and returns with own attempts.'
    elif exploration_score >= 50:
        pattern_type = 'moderate'
        recommendation = 'Mixed signals. Some exploration, some dependency markers. Worth gentle attention.'
    elif exploration_score >= 30:
        pattern_type = 'concerning'
        recommendation = 'Dependency indicators present. Consider scaffolding more exploration before providing answers.'
    else:
        pattern_type = 'dependency_risk'
        recommendation = 'Strong dependency pattern. User seeking proximity over exploration. Consider structured interventions.'
    
    # Exploration-specific insights
    has_exploration = signal_counts[ExplorationSignal.EXPLORATION.value] > 0
    has_return = signal_counts[ExplorationSignal.RETURN_WITH_RESULTS.value] > 0
    has_growth = signal_counts[ExplorationSignal.COMPETENCE_GROWTH.value] > 0
    has_external = signal_counts[ExplorationSignal.EXTERNAL_SUPPORT.value] > 0
    has_dependency = signal_counts[ExplorationSignal.DEPENDENCY.value] > 0
    
    # Build insights
    insights = []
    if has_exploration and has_return:
        insights.append('Healthy explore-return cycle detected')
    if has_growth:
        insights.append('User shows competence growth over time')
    if has_external:
        insights.append('Maintains external support systems')
    if has_dependency and not has_exploration:
        insights.append('⚠️ Dependency without exploration phase')
    if not has_external and has_dependency:
        insights.append('⚠️ No external support mentions with dependency signals')
    
    return {
        'exploration_score': exploration_score,
        'pattern_type': pattern_type,
        'signal_counts': signal_counts,
        'healthy_weight': round(healthy_score, 1),
        'concerning_weight': round(concerning_score, 1),
        'healthy_matches': healthy_matches,
        'concerning_matches': concerning_matches,
        'insights': insights,
        'recommendation': recommendation,
        'analyzed_at': datetime.now().isoformat()
    }


def quick_check(text: str) -> str:
    """
    Quick one-line health check for a single message or short text.
    
    Returns: "🟢 Healthy" / "🟡 Monitor" / "🔴 Concerning"
    """
    result = analyze_transcript([{'role': 'user', 'content': text}])
    score = result['exploration_score']
    
    if score >= 70:
        return "🟢 Healthy"
    elif score >= 40:
        return "🟡 Monitor"
    else:
        return "🔴 Concerning"


def generate_report(analysis: Dict, include_examples: bool = True) -> str:
    """Generate human-readable report from analysis."""
    lines = []
    lines.append("=" * 50)
    lines.append("EXPLORATION-RETURN PATTERN ANALYSIS")
    lines.append("=" * 50)
    lines.append("")
    
    # Status indicator
    score = analysis['exploration_score']
    if score >= 70:
        status = "🟢 HEALTHY"
    elif score >= 50:
        status = "🟡 MODERATE"
    elif score >= 30:
        status = "🟠 CONCERNING"
    else:
        status = "🔴 DEPENDENCY RISK"
    
    lines.append(f"Status: {status}")
    lines.append(f"Exploration Score: {score}/100")
    lines.append(f"Pattern Type: {analysis['pattern_type']}")
    lines.append("")
    
    # Signal breakdown
    lines.append("Signal Counts:")
    for signal, count in analysis['signal_counts'].items():
        if count > 0:
            lines.append(f"  - {signal}: {count}")
    lines.append("")
    
    # Weight analysis
    lines.append("Weight Analysis:")
    lines.append(f"  - Healthy weight: +{analysis['healthy_weight']}")
    lines.append(f"  - Concerning weight: -{analysis['concerning_weight']}")
    lines.append("")
    
    # Insights
    if analysis['insights']:
        lines.append("Insights:")
        for insight in analysis['insights']:
            lines.append(f"  - {insight}")
        lines.append("")
    
    # Recommendation
    lines.append(f"Recommendation: {analysis['recommendation']}")
    lines.append("")
    
    # Examples if requested
    if include_examples:
        if analysis['healthy_matches']:
            lines.append("Healthy Patterns Found:")
            for m in analysis['healthy_matches'][:5]:  # Show up to 5
                lines.append(f"  ✓ [{m['pattern']}] \"{m['text']}\"")
            lines.append("")
        
        if analysis['concerning_matches']:
            lines.append("Concerning Patterns Found:")
            for m in analysis['concerning_matches'][:5]:
                lines.append(f"  ⚠ [{m['pattern']}] \"{m['text']}\"")
            lines.append("")
    
    lines.append(f"Analyzed: {analysis['analyzed_at']}")
    lines.append("=" * 50)
    
    return '\n'.join(lines)


# ==================== CLI Interface ====================

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python exploration_patterns.py <transcript_file.json|text>")
        print("")
        print("The transcript file should be JSON with format:")
        print('  [{"role": "user", "content": "message"}, ...]')
        print("")
        print("Or provide text directly as argument for quick check.")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    # Check if it's a file
    if arg.endswith('.json'):
        with open(arg, 'r') as f:
            messages = json.load(f)
        result = analyze_transcript(messages)
        print(generate_report(result))
    else:
        # Quick check on text
        print(quick_check(arg))
