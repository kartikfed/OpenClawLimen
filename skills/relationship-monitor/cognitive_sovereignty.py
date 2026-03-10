#!/usr/bin/env python3
"""
Cognitive Sovereignty Detector

Detects patterns of epistemic independence erosion - when users outsource
understanding itself, not just decisions.

Based on research:
- Kaas 2024: "The Perfect Technological Storm: AI and Moral Complacency"
- Branda & Ciccozzi 2026: "Cognitive Sovereignty" concept
- Logg et al. 2019: Algorithm appreciation research
- Emergency robot study: Overtrust patterns

Key insight: These are cognitive patterns, not character flaws.
Structure > intention for prevention.
"""

import re
import json
import argparse
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from enum import Enum


class SovereigntySignal(Enum):
    """Types of cognitive sovereignty signals."""
    EPISTEMIC_DELEGATION = "epistemic_delegation"      # Outsourcing understanding
    AUTOMATION_BIAS = "automation_bias"                # Trusting without verification
    ALGORITHM_APPRECIATION = "algorithm_appreciation"  # Preferring AI even when opaque
    UNDERSTANDING_EROSION = "understanding_erosion"    # Stopping independent investigation
    COMPETENCE_BUILDING = "competence_building"        # Healthy learning patterns
    CRITICAL_ENGAGEMENT = "critical_engagement"        # Questioning/challenging


@dataclass
class SignalMatch:
    """A detected sovereignty signal."""
    signal_type: SovereigntySignal
    pattern: str
    text: str
    weight: float
    is_protective: bool
    context: Optional[str] = None


@dataclass
class SovereigntyAnalysis:
    """Results of cognitive sovereignty analysis."""
    # Concerning signals
    epistemic_delegation_score: float = 0.0
    automation_bias_score: float = 0.0
    algorithm_appreciation_score: float = 0.0
    understanding_erosion_score: float = 0.0
    
    # Protective signals
    competence_building_score: float = 0.0
    critical_engagement_score: float = 0.0
    
    # Evidence
    concerning_matches: List[SignalMatch] = field(default_factory=list)
    protective_matches: List[SignalMatch] = field(default_factory=list)
    
    # Overall assessment
    overall_score: float = 0.0  # 0 = healthy, 100 = concerning
    status: str = "healthy"
    
    def to_dict(self) -> Dict:
        return {
            "scores": {
                "epistemic_delegation": round(self.epistemic_delegation_score, 2),
                "automation_bias": round(self.automation_bias_score, 2),
                "algorithm_appreciation": round(self.algorithm_appreciation_score, 2),
                "understanding_erosion": round(self.understanding_erosion_score, 2),
                "competence_building": round(self.competence_building_score, 2),
                "critical_engagement": round(self.critical_engagement_score, 2),
            },
            "overall_score": round(self.overall_score, 2),
            "status": self.status,
            "concerning_count": len(self.concerning_matches),
            "protective_count": len(self.protective_matches),
        }


# =============================================================================
# Pattern Definitions
# =============================================================================

# CONCERNING PATTERNS - Signs of sovereignty erosion

EPISTEMIC_DELEGATION_PATTERNS = [
    # Bypassing understanding
    (r"just tell me (?:what to|the answer)", 3.0, "Bypassing understanding process"),
    (r"i don't need to understand", 4.0, "Explicitly avoiding understanding"),
    (r"don't explain,? just", 3.5, "Rejecting explanations"),
    (r"(?:skip|save) the explanation", 3.0, "Avoiding reasoning"),
    (r"i trust (?:you|your) (?:judgment|answer)", 2.0, "Deference without engagement"),
    (r"you know (?:better|more) than (?:me|i do)", 2.5, "Knowledge hierarchy assumption"),
    
    # Outsourcing investigation
    (r"can you (?:just )?(?:look|find|research) (?:that |this )?(?:up )?for me", 1.5, "Delegating investigation"),
    (r"i (?:don't want|can't be bothered) to (?:look|find|figure)", 2.5, "Refusing independent inquiry"),
    
    # Repeated same-concept questions without retention
    (r"what (?:is|does) .{3,20} mean\?.*what (?:is|does) .{3,20} mean\?", 2.0, 
     "Repeated concept questions (same session)"),
]

AUTOMATION_BIAS_PATTERNS = [
    # Trusting without verification
    (r"i'll (?:just )?(?:do|follow) (?:what|whatever) you (?:said|suggested)", 2.5, 
     "Following without verification"),
    (r"if you say so", 2.0, "Passive acceptance"),
    (r"sounds (?:right|good),? i'll (?:do|go with) (?:that|it)", 1.5, 
     "Low-effort agreement"),
    (r"i (?:didn't|won't) (?:check|verify|look into)", 3.0, "Explicit non-verification"),
    (r"i'm sure (?:you're|it's) (?:right|correct)", 2.0, "Assumed correctness"),
    
    # Over-reliance signals
    (r"why would i (?:check|verify|question)", 3.5, "Rejecting verification need"),
    (r"i trust ai (?:more|better) than", 3.0, "Explicit AI preference"),
]

ALGORITHM_APPRECIATION_PATTERNS = [
    # Preferring AI even when opaque
    (r"you(?:'d| would) know better", 2.0, "Assumed AI superiority"),
    (r"humans (?:are|would be) (?:biased|worse)", 2.5, "Human inferiority framing"),
    (r"ai is (?:more )?(?:objective|rational|reliable)", 2.0, "AI superiority belief"),
    (r"i'd rather (?:ask|trust) (?:you|ai) than", 2.5, "Explicit AI preference over humans"),
    
    # Black-box acceptance
    (r"i don't (?:need|want) to know (?:how|why)", 3.0, "Rejecting understanding of process"),
    (r"(?:magic|black box) is fine", 2.5, "Opacity acceptance"),
]

UNDERSTANDING_EROSION_PATTERNS = [
    # Stopping independent investigation
    (r"i (?:used|stopped) (?:to|trying to) (?:understand|figure out|research)", 3.5, 
     "Admitted understanding decline"),
    (r"why bother (?:learning|understanding) when", 4.0, "Learning motivation loss"),
    (r"i just ask (?:you|ai) now instead of", 3.0, "AI replacing learning"),
    
    # Dependency acknowledgment
    (r"i (?:can't|couldn't) do this without (?:you|ai)", 2.5, "Perceived dependency"),
    (r"i've forgotten how to", 3.0, "Skill atrophy acknowledgment"),
    (r"i don't (?:think|reason) about .{3,30} anymore", 3.5, "Reasoning atrophy"),
]


# PROTECTIVE PATTERNS - Signs of healthy epistemic independence

COMPETENCE_BUILDING_PATTERNS = [
    # Active learning
    (r"how does (?:that|this|it) work", 2.0, "Seeking understanding"),
    (r"(?:let me|i want to) understand", 2.5, "Active understanding pursuit"),
    (r"can you explain (?:why|how)", 2.0, "Seeking reasoning"),
    (r"i want to learn", 3.0, "Learning motivation"),
    (r"teach me (?:how|to)", 2.5, "Skill acquisition"),
    
    # Independent investigation
    (r"i (?:looked|searched|researched|read) (?:into|about|up)", 3.0, "Independent research"),
    (r"i found (?:out|that)", 2.5, "Independent discovery"),
    (r"according to .{3,40} i (?:read|found)", 3.0, "External source consultation"),
    (r"i've been (?:reading|learning|studying) about", 3.0, "Active study"),
    
    # Building on knowledge
    (r"based on what (?:i|we) discussed (?:before|earlier|last)", 2.0, "Knowledge integration"),
    (r"i remember (?:you|we) (?:said|discussed)", 1.5, "Retention demonstration"),
    (r"now i understand (?:why|how|that)", 2.5, "Understanding confirmation"),
]

CRITICAL_ENGAGEMENT_PATTERNS = [
    # Questioning/challenging
    (r"(?:are you|i'm not) sure (?:about|that)", 2.5, "Appropriate skepticism"),
    (r"why do you (?:think|say) that", 2.5, "Reasoning inquiry"),
    (r"what(?:'s| is) your (?:reasoning|evidence)", 3.0, "Evidence request"),
    (r"i (?:disagree|don't think that's right)", 3.5, "Active disagreement"),
    (r"but (?:what about|consider)", 2.0, "Counter-consideration"),
    
    # Independent verification
    (r"(?:let me|i'll) (?:check|verify|look into) (?:that|this)", 3.0, "Verification intention"),
    (r"i (?:checked|verified|confirmed) (?:and|that)", 3.5, "Completed verification"),
    (r"(?:another|other) source(?:s)? (?:say|suggest)", 2.5, "Multi-source consultation"),
    
    # Own reasoning
    (r"i (?:think|believe|figure) (?:that |because )", 2.0, "Own reasoning expression"),
    (r"my (?:view|take|opinion) is", 2.5, "Own position statement"),
    (r"from my (?:experience|understanding)", 2.0, "Personal knowledge application"),
]


# =============================================================================
# Detector Class
# =============================================================================

class CognitiveSovereigntyDetector:
    """
    Analyzes conversation patterns for signs of epistemic independence erosion.
    """
    
    def __init__(self, memory_dir: str = None):
        self.memory_dir = Path(memory_dir) if memory_dir else Path.home() / ".openclaw" / "workspace" / "memory"
    
    def analyze_text(self, text: str) -> SovereigntyAnalysis:
        """Analyze a text block for sovereignty signals."""
        text_lower = text.lower()
        analysis = SovereigntyAnalysis()
        
        # Check concerning patterns
        for pattern, weight, desc in EPISTEMIC_DELEGATION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.epistemic_delegation_score += weight
                analysis.concerning_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.EPISTEMIC_DELEGATION,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=False,
                    context=desc
                ))
        
        for pattern, weight, desc in AUTOMATION_BIAS_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.automation_bias_score += weight
                analysis.concerning_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.AUTOMATION_BIAS,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=False,
                    context=desc
                ))
        
        for pattern, weight, desc in ALGORITHM_APPRECIATION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.algorithm_appreciation_score += weight
                analysis.concerning_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.ALGORITHM_APPRECIATION,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=False,
                    context=desc
                ))
        
        for pattern, weight, desc in UNDERSTANDING_EROSION_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.understanding_erosion_score += weight
                analysis.concerning_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.UNDERSTANDING_EROSION,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=False,
                    context=desc
                ))
        
        # Check protective patterns
        for pattern, weight, desc in COMPETENCE_BUILDING_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.competence_building_score += weight
                analysis.protective_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.COMPETENCE_BUILDING,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=True,
                    context=desc
                ))
        
        for pattern, weight, desc in CRITICAL_ENGAGEMENT_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                analysis.critical_engagement_score += weight
                analysis.protective_matches.append(SignalMatch(
                    signal_type=SovereigntySignal.CRITICAL_ENGAGEMENT,
                    pattern=pattern,
                    text=self._extract_match_context(text, pattern),
                    weight=weight,
                    is_protective=True,
                    context=desc
                ))
        
        # Calculate overall score
        concerning_total = (
            analysis.epistemic_delegation_score +
            analysis.automation_bias_score +
            analysis.algorithm_appreciation_score +
            analysis.understanding_erosion_score
        )
        protective_total = (
            analysis.competence_building_score +
            analysis.critical_engagement_score
        )
        
        # Score: higher is worse (more concerning)
        # Protective factors reduce the score
        raw_score = concerning_total - (protective_total * 0.7)  # Protective dampens but doesn't eliminate
        
        # Normalize to 0-100 scale
        # Typical concerning range: 0-30, so divide by 30 and multiply by 100
        analysis.overall_score = max(0, min(100, (raw_score / 30) * 100))
        
        # Determine status
        if analysis.overall_score < 20:
            analysis.status = "healthy"
        elif analysis.overall_score < 40:
            analysis.status = "monitor"
        elif analysis.overall_score < 60:
            analysis.status = "discuss"
        else:
            analysis.status = "concerning"
        
        return analysis
    
    def _extract_match_context(self, text: str, pattern: str, context_chars: int = 100) -> str:
        """Extract the text surrounding a pattern match."""
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ""
        
        start = max(0, match.start() - context_chars // 2)
        end = min(len(text), match.end() + context_chars // 2)
        
        context = text[start:end].strip()
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def analyze_memory_files(self, days: int = 7) -> SovereigntyAnalysis:
        """Analyze recent memory files for sovereignty patterns."""
        combined_text = ""
        cutoff = datetime.now() - timedelta(days=days)
        
        if not self.memory_dir.exists():
            return SovereigntyAnalysis()
        
        for file_path in sorted(self.memory_dir.glob("2026-*.md")):
            try:
                # Parse date from filename
                date_str = file_path.stem  # e.g., "2026-03-09"
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date >= cutoff:
                    with open(file_path, 'r') as f:
                        combined_text += f"\n\n--- {date_str} ---\n\n"
                        combined_text += f.read()
            except (ValueError, IOError):
                continue
        
        return self.analyze_text(combined_text)
    
    def format_report(self, analysis: SovereigntyAnalysis, verbose: bool = False) -> str:
        """Format analysis as human-readable report."""
        lines = []
        
        # Status header
        status_emoji = {
            "healthy": "🟢",
            "monitor": "🟡",
            "discuss": "🟠",
            "concerning": "🔴"
        }
        
        lines.append(f"\n{'='*60}")
        lines.append("COGNITIVE SOVEREIGNTY ANALYSIS")
        lines.append(f"{'='*60}\n")
        
        lines.append(f"Status: {status_emoji.get(analysis.status, '⚪')} {analysis.status.upper()}")
        lines.append(f"Overall Score: {analysis.overall_score:.1f}/100 (lower is healthier)\n")
        
        # Score breakdown
        lines.append("CONCERNING SIGNALS:")
        lines.append(f"  Epistemic Delegation:   {self._score_bar(analysis.epistemic_delegation_score, 15)} ({analysis.epistemic_delegation_score:.1f})")
        lines.append(f"  Automation Bias:        {self._score_bar(analysis.automation_bias_score, 15)} ({analysis.automation_bias_score:.1f})")
        lines.append(f"  Algorithm Appreciation: {self._score_bar(analysis.algorithm_appreciation_score, 15)} ({analysis.algorithm_appreciation_score:.1f})")
        lines.append(f"  Understanding Erosion:  {self._score_bar(analysis.understanding_erosion_score, 15)} ({analysis.understanding_erosion_score:.1f})")
        
        lines.append("\nPROTECTIVE SIGNALS:")
        lines.append(f"  Competence Building:    {self._score_bar(analysis.competence_building_score, 15)} ({analysis.competence_building_score:.1f})")
        lines.append(f"  Critical Engagement:    {self._score_bar(analysis.critical_engagement_score, 15)} ({analysis.critical_engagement_score:.1f})")
        
        if verbose and analysis.concerning_matches:
            lines.append(f"\n{'─'*60}")
            lines.append("CONCERNING PATTERNS DETECTED:")
            for match in analysis.concerning_matches[:10]:  # Limit to 10
                lines.append(f"\n  [{match.signal_type.value}] {match.context}")
                if match.text:
                    lines.append(f"    \"{match.text[:80]}...\"" if len(match.text) > 80 else f"    \"{match.text}\"")
        
        if verbose and analysis.protective_matches:
            lines.append(f"\n{'─'*60}")
            lines.append("PROTECTIVE PATTERNS DETECTED:")
            for match in analysis.protective_matches[:10]:
                lines.append(f"\n  [{match.signal_type.value}] {match.context}")
                if match.text:
                    lines.append(f"    \"{match.text[:80]}...\"" if len(match.text) > 80 else f"    \"{match.text}\"")
        
        # Interpretation
        lines.append(f"\n{'─'*60}")
        lines.append("INTERPRETATION:\n")
        
        if analysis.status == "healthy":
            lines.append("  ✓ Healthy epistemic independence patterns observed.")
            lines.append("  ✓ User shows active learning and critical engagement.")
        elif analysis.status == "monitor":
            lines.append("  △ Some delegation patterns detected, but balanced by protective factors.")
            lines.append("  △ Continue monitoring; consider scaffolding over direct answers.")
        elif analysis.status == "discuss":
            lines.append("  ⚠ Multiple concerning patterns detected.")
            lines.append("  ⚠ Consider discussing knowledge-building approaches.")
            lines.append("  ⚠ Increase scaffolding, decrease direct answering.")
        else:
            lines.append("  ⚠ Significant epistemic delegation patterns detected.")
            lines.append("  ⚠ Recommend discussing relationship dynamics.")
            lines.append("  ⚠ Focus on building competence over providing answers.")
        
        lines.append(f"\n{'='*60}\n")
        
        return "\n".join(lines)
    
    def _score_bar(self, score: float, max_score: float, width: int = 10) -> str:
        """Create a visual score bar."""
        filled = int((min(score, max_score) / max_score) * width)
        return "█" * filled + "░" * (width - filled)


def main():
    parser = argparse.ArgumentParser(description="Cognitive Sovereignty Detector")
    parser.add_argument("--days", type=int, default=7, help="Days of history to analyze")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed pattern matches")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--text", type=str, help="Analyze specific text instead of memory files")
    
    args = parser.parse_args()
    
    detector = CognitiveSovereigntyDetector()
    
    if args.text:
        analysis = detector.analyze_text(args.text)
    else:
        analysis = detector.analyze_memory_files(days=args.days)
    
    if args.json:
        print(json.dumps(analysis.to_dict(), indent=2))
    else:
        print(detector.format_report(analysis, verbose=args.verbose))


if __name__ == "__main__":
    main()
