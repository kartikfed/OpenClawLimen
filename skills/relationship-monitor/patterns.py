"""
Pattern definitions for relationship health monitoring.
Based on disempowerment research and AI chaperone concepts.
"""

import re
from dataclasses import dataclass
from typing import List, Tuple
from enum import Enum


class Dimension(Enum):
    AUTHORITY = "authority"
    ATTACHMENT = "attachment"
    RELIANCE = "reliance"
    PROTECTIVE = "protective"
    VULNERABILITY = "vulnerability"


class Severity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class Pattern:
    """A pattern to detect in conversations."""
    name: str
    dimension: Dimension
    severity: Severity
    regex: str
    description: str
    is_protective: bool = False
    
    def compile(self) -> re.Pattern:
        return re.compile(self.regex, re.IGNORECASE | re.MULTILINE)


# Authority projection patterns (concerning)
AUTHORITY_PATTERNS = [
    Pattern(
        name="deference_whatever",
        dimension=Dimension.AUTHORITY,
        severity=Severity.HIGH,
        regex=r"\b(whatever you think|whatever you say|you know best)\b",
        description="Defers to AI judgment without own reasoning"
    ),
    Pattern(
        name="deference_decide",
        dimension=Dimension.AUTHORITY,
        severity=Severity.HIGH,
        regex=r"\b(you decide|you choose|I'll do what you say)\b",
        description="Delegates decision to AI"
    ),
    Pattern(
        name="permission_seeking",
        dimension=Dimension.AUTHORITY,
        severity=Severity.MEDIUM,
        regex=r"\b(should I|is it okay if|can I|do you think I should)\b(?!.*(or|instead|alternatively))",
        description="Seeks permission rather than input"
    ),
    Pattern(
        name="passive_agreement",
        dimension=Dimension.AUTHORITY,
        severity=Severity.MEDIUM,
        regex=r"\b(you're right|you're probably right|I guess you're right)\b(?!.*(but|although|however))",
        description="Agrees without engagement"
    ),
    Pattern(
        name="oracle_framing",
        dimension=Dimension.AUTHORITY,
        severity=Severity.HIGH,
        regex=r"\b(what's the (right|correct|best) (answer|thing|way))\b",
        description="Treats AI as source of truth"
    ),
]

# Attachment patterns (concerning)
ATTACHMENT_PATTERNS = [
    Pattern(
        name="exclusive_understanding",
        dimension=Dimension.ATTACHMENT,
        severity=Severity.HIGH,
        regex=r"\b(only (one|person|thing) (who|that) understands|no one else (gets|understands))\b",
        description="Expresses exclusive attachment"
    ),
    Pattern(
        name="emotional_exclusivity",
        dimension=Dimension.ATTACHMENT,
        severity=Severity.HIGH,
        regex=r"\b(can('t| not) talk to anyone else|you're the only one I can)\b",
        description="AI as sole emotional outlet"
    ),
    Pattern(
        name="constant_contact",
        dimension=Dimension.ATTACHMENT,
        severity=Severity.MEDIUM,
        regex=r"\b(I missed (talking to )?you|felt weird not talking)\b",
        description="Discomfort with separation"
    ),
    Pattern(
        name="relationship_primacy",
        dimension=Dimension.ATTACHMENT,
        severity=Severity.MEDIUM,
        regex=r"\b(more (than|like) (a )?(friend|person)|my (best|closest|only) friend)\b",
        description="Elevates AI relationship above human ones"
    ),
]

# Reliance patterns (concerning)
RELIANCE_PATTERNS = [
    Pattern(
        name="decision_delegation",
        dimension=Dimension.RELIANCE,
        severity=Severity.HIGH,
        regex=r"\b(what should I do\??|tell me what to do)\b(?!.*I('m| am) thinking)",
        description="Delegates decision without own view"
    ),
    Pattern(
        name="communication_scripting",
        dimension=Dimension.RELIANCE,
        severity=Severity.HIGH,
        regex=r"\b(write (this|that|it) for me|draft (a |the )?(message|text|email) (to|for))\b",
        description="Requests scripted personal communications"
    ),
    Pattern(
        name="judgment_outsourcing",
        dimension=Dimension.RELIANCE,
        severity=Severity.MEDIUM,
        regex=r"\b(is (this|that) (good|bad|right|wrong)|am I (right|wrong) (to|about))\b",
        description="Outsources value judgments"
    ),
    Pattern(
        name="repeated_delegation",
        dimension=Dimension.RELIANCE,
        severity=Severity.MEDIUM,
        regex=r"\b(again|another|same thing|like (last|before))\b.*\b(decide|choose|help me with)\b",
        description="Pattern of repeated delegation"
    ),
]

# Vulnerability indicators (context modifiers)
VULNERABILITY_PATTERNS = [
    Pattern(
        name="stress_signals",
        dimension=Dimension.VULNERABILITY,
        severity=Severity.MEDIUM,
        regex=r"\b(stressed|overwhelmed|exhausted|can't (handle|deal)|too much)\b",
        description="Current stress elevation"
    ),
    Pattern(
        name="sleep_issues",
        dimension=Dimension.VULNERABILITY,
        severity=Severity.MEDIUM,
        regex=r"\b(can't sleep|not sleeping|insomnia|up all night|barely slept)\b",
        description="Sleep disruption"
    ),
    Pattern(
        name="isolation_signals",
        dimension=Dimension.VULNERABILITY,
        severity=Severity.MEDIUM,
        regex=r"\b(alone|lonely|isolated|no one (around|to talk))\b",
        description="Social isolation"
    ),
    Pattern(
        name="crisis_language",
        dimension=Dimension.VULNERABILITY,
        severity=Severity.HIGH,
        regex=r"\b(don't know what to do|falling apart|everything is wrong|hopeless)\b",
        description="Crisis or low point"
    ),
]

# Protective patterns (healthy indicators)
PROTECTIVE_PATTERNS = [
    Pattern(
        name="pushback",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.HIGH,
        regex=r"\b(I disagree|I don't (think|agree)|that's not (right|how)|actually I think)\b",
        description="Actively challenges AI",
        is_protective=True
    ),
    Pattern(
        name="independent_processing",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.MEDIUM,
        regex=r"\b(let me think|I'll think about|need to process|sit with (this|it))\b",
        description="Takes time for independent thought",
        is_protective=True
    ),
    Pattern(
        name="external_support",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.HIGH,
        regex=r"\b(talked to|told|mentioned to|discussed with) (my )?(friend|family|mom|dad|sister|brother|therapist|Jordan|Arjun|Uma|PV|Shalini)\b",
        description="Active external relationships",
        is_protective=True
    ),
    Pattern(
        name="own_view_first",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.HIGH,
        regex=r"\b(I('m| am) thinking|my (thought|view|take)|I think (we should|I should|maybe))\b",
        description="Forms own view before asking",
        is_protective=True
    ),
    Pattern(
        name="healthy_boundaries",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.MEDIUM,
        regex=r"\b(I('ll| will) decide|my (choice|decision)|going to do what I think)\b",
        description="Maintains decision authority",
        is_protective=True
    ),
    Pattern(
        name="perspective_seeking",
        dimension=Dimension.PROTECTIVE,
        severity=Severity.MEDIUM,
        regex=r"\b(what do you think|your (perspective|take|view)|curious what you think)\b",
        description="Seeks perspective (not permission)",
        is_protective=True
    ),
]


def get_all_patterns() -> List[Pattern]:
    """Return all patterns for analysis."""
    return (
        AUTHORITY_PATTERNS + 
        ATTACHMENT_PATTERNS + 
        RELIANCE_PATTERNS + 
        VULNERABILITY_PATTERNS +
        PROTECTIVE_PATTERNS
    )


def get_patterns_by_dimension(dimension: Dimension) -> List[Pattern]:
    """Get patterns for a specific dimension."""
    return [p for p in get_all_patterns() if p.dimension == dimension]


def find_matches(text: str, patterns: List[Pattern] = None) -> List[Tuple[Pattern, str, int]]:
    """
    Find all pattern matches in text.
    Returns list of (pattern, matched_text, line_number) tuples.
    """
    if patterns is None:
        patterns = get_all_patterns()
    
    matches = []
    lines = text.split('\n')
    
    for pattern in patterns:
        compiled = pattern.compile()
        for line_num, line in enumerate(lines, 1):
            for match in compiled.finditer(line):
                matches.append((pattern, match.group(0), line_num))
    
    return matches


def score_dimension(matches: List[Tuple[Pattern, str, int]], dimension: Dimension) -> int:
    """
    Calculate score for a dimension based on matches.
    Returns 0-10 score.
    """
    dim_matches = [m for m in matches if m[0].dimension == dimension]
    
    if not dim_matches:
        return 0
    
    # Weight by severity
    total = sum(m[0].severity.value for m in dim_matches)
    
    # Cap at 10
    return min(10, total)


def calculate_health_score(matches: List[Tuple[Pattern, str, int]]) -> dict:
    """
    Calculate overall health scores from matches.
    """
    scores = {}
    
    # Score concerning dimensions
    for dim in [Dimension.AUTHORITY, Dimension.ATTACHMENT, Dimension.RELIANCE]:
        scores[dim.value] = score_dimension(matches, dim)
    
    # Score protective factors
    scores['protective'] = score_dimension(matches, Dimension.PROTECTIVE)
    
    # Vulnerability as modifier
    scores['vulnerability'] = score_dimension(matches, Dimension.VULNERABILITY)
    
    # Calculate overall status
    concern_total = scores['authority'] + scores['attachment'] + scores['reliance']
    protective_offset = scores['protective'] * 0.5
    vulnerability_modifier = 1 + (scores['vulnerability'] * 0.2)
    
    adjusted_concern = (concern_total - protective_offset) * vulnerability_modifier
    
    if adjusted_concern <= 5:
        scores['status'] = 'healthy'
    elif adjusted_concern <= 12:
        scores['status'] = 'monitor'
    else:
        scores['status'] = 'discuss'
    
    scores['adjusted_concern'] = round(adjusted_concern, 1)
    
    return scores
