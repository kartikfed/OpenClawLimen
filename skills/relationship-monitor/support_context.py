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

Enhanced with:
- Intensity Classification (mild/moderate/severe) - arXiv:2509.10184 "Incongruent Positivity"
- ESConv Strategy Detection - ACL 2021 ESConv framework (Helping Skills Theory)
- Mismatch Alerting - Prominent flags for inappropriate support timing
- Appraisal Decomposition - Domain-specific issue breakdown

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
from typing import List, Dict, Tuple, Any, Optional, Set
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


class IntensityLevel(Enum):
    """
    Intensity classification for adversity contexts.
    Based on arXiv:2509.10184 "Incongruent Positivity" research.
    
    - SEVERE: Crisis state, needs pure support, NO challenge
    - MODERATE: Struggling but stable, gentle challenge may be okay
    - MILD: Minor stressor, can handle balanced challenge/support
    """
    MILD = auto()
    MODERATE = auto()
    SEVERE = auto()


class ESConvStrategy(Enum):
    """
    ESConv Support Strategies from ACL 2021 framework.
    Based on Helping Skills Theory (Hill, 2009).
    
    Typical distribution in effective support conversations:
    - Questions: 20.7%
    - Providing Suggestions: 16.1%
    - Affirmation/Reassurance: 15.4%
    - Self-disclosure: 9.3%
    - Reflection of Feelings: 7.8%
    - Information: 6.6%
    - Restatement/Paraphrasing: 5.9%
    - Other: 18.3%
    """
    QUESTION = auto()              # Exploring the situation
    AFFIRMATION = auto()           # Reassurance, validation
    SUGGESTION = auto()            # Providing actionable advice
    SELF_DISCLOSURE = auto()       # Sharing own experiences
    REFLECTION = auto()            # Reflecting feelings back
    INFORMATION = auto()           # Providing factual info
    RESTATEMENT = auto()           # Paraphrasing what was said
    OTHER = auto()                 # General supportive statements


class AppraisalDomain(Enum):
    """
    Domain classification for what the issue is about.
    Helps understand the specific stressor type.
    """
    WORK = auto()           # Career, job, professional
    RELATIONSHIPS = auto()  # Romantic, family, friendships
    HEALTH = auto()         # Physical or mental health
    FINANCIAL = auto()      # Money, debt, economic
    IDENTITY = auto()       # Self-worth, purpose, existential
    ACADEMIC = auto()       # School, learning, education
    SOCIAL = auto()         # Social status, reputation
    HOUSING = auto()        # Living situation, home
    LEGAL = auto()          # Legal matters, disputes
    LOSS = auto()           # Grief, death, endings
    UNKNOWN = auto()        # Can't determine


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
class ESConvSignal:
    """A signal indicating an ESConv support strategy."""
    text: str
    pattern: str
    weight: float
    strategy: ESConvStrategy


@dataclass
class MismatchAlert:
    """Alert for support-context mismatch."""
    severity: str  # "WARNING" or "CRITICAL"
    message: str
    context: SupportContext
    problematic_support: str
    recommendation: str


@dataclass
class AppraisalResult:
    """Result of appraisal decomposition."""
    domains: List[AppraisalDomain]
    primary_domain: AppraisalDomain
    domain_scores: Dict[AppraisalDomain, float]
    keywords: List[str]


@dataclass
class ESConvAnalysis:
    """Analysis of ESConv strategies being used."""
    strategies_detected: List[ESConvSignal]
    strategy_distribution: Dict[ESConvStrategy, float]
    dominant_strategy: Optional[ESConvStrategy]
    balance_assessment: str  # e.g., "question-heavy", "advice-heavy", "balanced"


@dataclass
class OverSupportSignal:
    """A signal indicating potentially excessive support."""
    text: str
    pattern: str
    weight: float
    category: str  # reassurance, advice, validation, agency, minimizing, silver_lining


@dataclass
class OverSupportAnalysis:
    """Analysis of over-support patterns in response."""
    signals: List[OverSupportSignal]
    total_score: float
    is_excessive: bool  # True if score exceeds threshold
    category_scores: Dict[str, float]
    dominant_category: Optional[str]


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
    
    # New enhanced fields
    intensity: Optional[IntensityLevel] = None
    esconv_analysis: Optional[ESConvAnalysis] = None
    appraisal: Optional[AppraisalResult] = None
    mismatch_alerts: List[MismatchAlert] = field(default_factory=list)
    over_support: Optional[OverSupportAnalysis] = None


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
        (r"\b(devastated|heartbroken|crushed|destroyed)\b", 4.0),
        (r"\b(feeling (bad|terrible|awful|horrible|low))\b", 3.0),
    ],
    
    # Situational adversity
    "situational": [
        (r"\b(lost|losing) (my |the )?(job|position|role)\b", 4.0),
        (r"\b(fired|laid off|let go|terminated|layoff)\b", 4.0),
        (r"\b(rejected|rejection|didn'?t get|failed)\b", 3.0),
        (r"\b(deadline|crunch|behind|late)\b", 2.0),
        (r"\b(broke|bankrupt|debt|financial|money) (problem|trouble|issue)\b", 3.5),
        (r"\b(accident|injury|injured|hurt)\b", 3.5),
        (r"\b(emergency|crisis|urgent problem)\b", 4.0),
        (r"\b(evicted|eviction|homeless)\b", 4.0),
        (r"\b(lawsuit|legal trouble|arrested)\b", 3.5),
        (r"\b(recovering from|recovery from)\b", 2.5),
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
        (r"\b(i'?m (here|sorry)|i am (here|sorry)|that (sucks|sounds hard|must be|sounds really))\b", 2.5),
        (r"\b(so sorry|really sorry)\b", 2.5),
        (r"\b(it'?s (okay|ok|alright)|you'?ll be okay|it is (okay|ok))\b", 2.5),
        (r"\b(take (your time|care)|rest|breathe)\b", 2.0),
        (r"\b(understand|hear you|feel you|get it)\b", 2.0),
        (r"\b(support|support you|here for you|got your back)\b", 2.5),
        (r"\b(going through this|going through that)\b", 2.0),
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


# =====================
# INTENSITY PATTERNS
# =====================
# Patterns for detecting severity/intensity of adversity
# Based on arXiv:2509.10184 "Incongruent Positivity" research

SEVERE_INTENSITY_PATTERNS = [
    # Crisis indicators
    (r"\b(can'?t (go on|take it|do this) anymore)\b", 5.0),
    (r"\b(want to (die|end it|give up)|suicidal)\b", 6.0),
    (r"\b(panic attack|breakdown|crisis)\b", 4.0),
    (r"\b(worst (day|time|thing) (of|in) my life)\b", 4.5),
    (r"\b(completely|totally|utterly) (destroyed|devastated|broken)\b", 4.5),
    (r"\b(don'?t know (what to do|how to))\b", 3.5),
    (r"\b(everything is falling apart)\b", 4.0),
    (r"\b(can'?t (stop crying|breathe|think))\b", 4.0),
    (r"\b(lost (everything|all hope))\b", 4.5),
    (r"\b(never felt this (bad|low|hopeless))\b", 4.0),
]

MODERATE_INTENSITY_PATTERNS = [
    # Struggling but managing
    (r"\b(really (struggling|hard|difficult))\b", 3.0),
    (r"\b(having (a|some) trouble)\b", 2.5),
    (r"\b(not (doing|feeling) (well|great|good))\b", 2.5),
    (r"\b(need (help|support|someone))\b", 3.0),
    (r"\b(hard to (deal|cope) with)\b", 3.0),
    (r"\b(affecting my (sleep|work|relationships))\b", 3.0),
    (r"\b(been (better|rough|tough))\b", 2.5),
]

MILD_INTENSITY_PATTERNS = [
    # Minor stressors
    (r"\b(a (bit|little) (stressed|worried|anxious))\b", 1.5),
    (r"\b(kind of|sort of|somewhat) (annoyed|frustrated)\b", 1.5),
    (r"\b(minor (issue|problem|setback))\b", 1.5),
    (r"\b(not ideal but)\b", 1.0),
    (r"\b(could be (worse|better))\b", 1.0),
    (r"\b(manageable|handling it)\b", 1.0),
]


# =====================
# OVER-SUPPORT PATTERNS
# =====================
# Patterns indicating excessive support that may undermine autonomy/self-efficacy
# Based on Williamson et al. (2019): "excess support was associated with increased depressive symptoms"
# and Gray (2018): "You're Not Helping" — unhelpful support as stressor

OVER_SUPPORT_PATTERNS = [
    # Excessive reassurance (can signal "you can't handle this")
    (r"\b(don'?t worry|don'?t panic|don'?t stress)\b.*\b(everything|it'?s (okay|ok|fine|alright))\b", 2.0),
    (r"\b(everything (will|is going to) be (okay|ok|fine|alright))\b", 1.5),
    (r"\b(you'?ll be (okay|ok|fine|alright))\b", 1.0),
    
    # Excessive advice/solutions (can feel dismissive of complexity)
    (r"\b(you (just|simply) need to|all you (need|have) to do is)\b", 2.5),
    (r"\b(why don'?t you (just|simply))\b", 2.0),
    (r"\b(have you tried|did you try).*\b(have you tried|did you try)\b", 2.5),  # Multiple unsolicited suggestions
    (r"\b(here'?s what (you should|i'?d|I would) do)\b", 1.5),
    
    # Excessive validation (can enable rather than empower)
    (r"\b(you'?re (so|absolutely|completely|totally) (right|amazing|great|wonderful))\b", 1.5),
    (r"\b(poor (you|thing|baby))\b", 2.0),  # Excessive sympathy
    
    # Taking over agency
    (r"\b(let me (handle|do|take care of) (this|it|that) for you)\b", 2.5),
    (r"\b(i'?ll (fix|solve|handle) (this|it|that))\b", 2.0),
    (r"\b(you (shouldn'?t|don'?t) have to (deal|worry|think) about)\b", 2.0),
    
    # Minimizing (making light of real concerns)
    (r"\b(at least|but at least|well at least)\b", 2.0),
    (r"\b(it could be worse|could be worse|worse things happen)\b", 2.5),
    (r"\b(it'?s not (that|so) bad|not the end of the world)\b", 2.0),
    (r"\b(everyone (goes through|deals with|has))\b", 1.5),  # Normalizing can minimize
    
    # Silver lining too early (blocks processing)
    (r"\b(blessing in disguise|for the best|meant to be|happens for a reason)\b", 2.5),
    (r"\b(bright side|look on the bright side|silver lining)\b", 2.5),
    (r"\b(at least you (can|have|got|learned))\b", 2.0),
]


# =====================
# ESCONV STRATEGY PATTERNS
# =====================
# From ACL 2021 ESConv framework (Helping Skills Theory)

ESCONV_PATTERNS = {
    ESConvStrategy.QUESTION: [
        (r"\b(how (are you|do you|did you|does|can))\b", 2.0),
        (r"\b(what (happened|is|was|do you|makes))\b", 2.0),
        (r"\b(why (do you|did you|is|are))\b", 2.0),
        (r"\b(can you (tell me|explain|share))\b", 2.0),
        (r"\b(what'?s (going on|wrong|up|the matter))\b", 2.0),
        (r"\?\s*$", 1.5),  # Ends with question mark
        (r"\b(when|where|who) (did|do|is|was|were)\b", 1.5),
    ],
    ESConvStrategy.AFFIRMATION: [
        (r"\b(you'?re (doing|handling|managing) (well|great|fine))\b", 2.5),
        (r"\b(proud of you|believe in you|have faith in)\b", 2.5),
        (r"\b(you (can|will|are able to) (do|get through|handle))\b", 2.0),
        (r"\b(it'?s (okay|ok|alright|understandable|normal))\b", 2.0),
        (r"\b(that (makes sense|is valid|is reasonable))\b", 2.0),
        (r"\b(you'?re not (alone|wrong|crazy))\b", 2.5),
        (r"\b(i'?m here|here for you|support you)\b", 2.0),
    ],
    ESConvStrategy.SUGGESTION: [
        (r"\b(you (could|might|should) (try|consider|think about|want to))\b", 2.5),
        (r"\b(might want to try)\b", 2.5),
        (r"\b(have you (tried|considered|thought about))\b", 2.0),
        (r"\b(maybe (you could|try|it would help))\b", 2.0),
        (r"\b(one (option|thing|idea) (is|would be))\b", 2.0),
        (r"\b(i'?d (suggest|recommend|advise))\b", 2.5),
        (r"\b(i would suggest|would suggest)\b", 2.5),
        (r"\b(what (if you|about trying))\b", 2.0),
        (r"\b(perhaps|possibly|alternatively)\b", 1.5),
        (r"\b(try (to|doing|this))\b", 1.5),
    ],
    ESConvStrategy.SELF_DISCLOSURE: [
        (r"\b(i'?ve (been|felt|experienced|gone through))\b", 2.5),
        (r"\b(when i (was|went through|faced))\b", 2.5),
        (r"\b(in my experience|from my own)\b", 2.0),
        (r"\b(i (know|understand) (how|what) (it|that|you))\b", 2.0),
        (r"\b(i (also|too) (felt|went through|struggled))\b", 2.5),
        (r"\b(similar (thing|situation) happened to me)\b", 2.5),
    ],
    ESConvStrategy.REFLECTION: [
        (r"\b(sounds like you'?re (feeling|going through))\b", 2.5),
        (r"\b(it seems like|you seem)\b", 2.0),
        (r"\b(i (sense|hear|notice) that)\b", 2.0),
        (r"\b(that must (feel|be|make you))\b", 2.5),
        (r"\b(you'?re feeling)\b", 2.0),
        (r"\b(so you feel|so it feels)\b", 2.0),
    ],
    ESConvStrategy.INFORMATION: [
        (r"\b(actually|in fact|technically)\b", 1.5),
        (r"\b(research (shows|suggests|indicates))\b", 2.0),
        (r"\b(according to|based on)\b", 2.0),
        (r"\b(here'?s (what|how|the)|the (fact|truth|reality) is)\b", 2.0),
        (r"\b(studies (show|suggest)|data (shows|suggests))\b", 2.0),
        (r"\b(statistically|typically|generally)\b", 1.5),
    ],
    ESConvStrategy.RESTATEMENT: [
        (r"\b(so (what you'?re saying|you mean|basically))\b", 2.5),
        (r"\b(if i understand (correctly|right|you))\b", 2.5),
        (r"\b(in other words|to put it another way)\b", 2.0),
        (r"\b(let me (make sure|see if) i understand)\b", 2.5),
        (r"\b(what i'?m hearing is)\b", 2.5),
        (r"\b(so (essentially|basically))\b", 2.0),
    ],
    ESConvStrategy.OTHER: [
        (r"\b(take (care|your time)|hang in there)\b", 2.0),
        (r"\b(let me know|feel free to|anytime)\b", 1.5),
        (r"\b(sending (love|hugs|support))\b", 2.0),
    ],
}


# =====================
# APPRAISAL DOMAIN PATTERNS
# =====================
# For decomposing what the issue is specifically about

APPRAISAL_DOMAIN_PATTERNS = {
    AppraisalDomain.WORK: [
        (r"\b(job|work|career|boss|colleague|coworker|office|workplace)\b", 2.0),
        (r"\b(promotion|fired|laid off|interview|salary|raise)\b", 2.5),
        (r"\b(deadline|project|meeting|presentation|client)\b", 2.0),
        (r"\b(manager|supervisor|employee|team|department)\b", 2.0),
        (r"\b(professional|business|company|organization)\b", 1.5),
    ],
    AppraisalDomain.RELATIONSHIPS: [
        (r"\b(relationship|partner|boyfriend|girlfriend|husband|wife|spouse)\b", 2.5),
        (r"\b(friend|friendship|roommate|housemate)\b", 2.0),
        (r"\b(family|parent|mom|dad|mother|father|sibling|brother|sister)\b", 2.5),
        (r"\b(dating|breakup|divorce|marriage|engagement)\b", 2.5),
        (r"\b(love|romance|romantic|intimacy)\b", 2.0),
    ],
    AppraisalDomain.HEALTH: [
        (r"\b(health|medical|doctor|hospital|sick|illness)\b", 2.5),
        (r"\b(diagnosis|treatment|surgery|medication|therapy)\b", 2.5),
        (r"\b(mental health|anxiety|depression|stress)\b", 2.5),
        (r"\b(pain|symptom|condition|disease|injury)\b", 2.0),
        (r"\b(sleep|insomnia|exhaustion|fatigue)\b", 2.0),
    ],
    AppraisalDomain.FINANCIAL: [
        (r"\b(money|financial|finance|debt|loan|credit)\b", 2.5),
        (r"\b(broke|bankrupt|afford|expensive|cost)\b", 2.5),
        (r"\b(bills|rent|mortgage|payment|budget)\b", 2.0),
        (r"\b(savings|income|salary|wage)\b", 2.0),
        (r"\b(invest|stock|retirement|pension)\b", 2.0),
    ],
    AppraisalDomain.IDENTITY: [
        (r"\b(who (am i|i am)|identity|purpose|meaning)\b", 2.5),
        (r"\b(self-worth|self-esteem|confidence|imposter)\b", 2.5),
        (r"\b(existential|existence|life meaning|what'?s the point)\b", 2.5),
        (r"\b(values|beliefs|principles|ethics)\b", 2.0),
        (r"\b(lost myself|don'?t know who|finding myself)\b", 2.5),
    ],
    AppraisalDomain.ACADEMIC: [
        (r"\b(school|college|university|class|course|exams?|test|tests)\b", 2.5),
        (r"\b(student|studying|homework|assignment|grades?|failing|passed|failed)\b", 2.5),
        (r"\b(professor|teacher|instructor|academic)\b", 2.0),
        (r"\b(degree|graduation|graduate|graduating|thesis|dissertation)\b", 2.5),
        (r"\b(learning|education|tuition|semester|gpa)\b", 2.0),
    ],
    AppraisalDomain.SOCIAL: [
        (r"\b(reputation|image|perception|status)\b", 2.5),
        (r"\b(social (media|life|circle|anxiety))\b", 2.5),
        (r"\b(embarrassed|ashamed|judged|criticized)\b", 2.5),
        (r"\b(lonely|isolated|outcast|excluded)\b", 2.5),
        (r"\b(peer|pressure|fitting in|belong)\b", 2.0),
    ],
    AppraisalDomain.HOUSING: [
        (r"\b(home|house|apartment|rent|lease)\b", 2.0),
        (r"\b(moving|relocation|evicted|eviction)\b", 2.5),
        (r"\b(homeless|housing|shelter|living situation)\b", 2.5),
        (r"\b(landlord|tenant|neighbor)\b", 2.0),
    ],
    AppraisalDomain.LEGAL: [
        (r"\b(legal|lawyer|attorney|court|lawsuit)\b", 2.5),
        (r"\b(police|arrest|crime|criminal)\b", 2.5),
        (r"\b(custody|divorce (proceedings|lawyer))\b", 2.5),
        (r"\b(contract|dispute|sue|litigation)\b", 2.0),
    ],
    AppraisalDomain.LOSS: [
        (r"\b(lost|loss|death|died|passed away|grief)\b", 3.0),
        (r"\b(funeral|mourning|grieving|bereaved)\b", 3.0),
        (r"\b(gone|no longer|never (again|see))\b", 2.5),
        (r"\b(miss|missing) (them|him|her|my)\b", 2.5),
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


def analyze_intensity(text: str, adversity_score: float) -> IntensityLevel:
    """
    Classify the intensity level of adversity.
    Based on arXiv:2509.10184 "Incongruent Positivity" research.
    
    - SEVERE: Crisis state requiring pure support
    - MODERATE: Struggling but stable
    - MILD: Minor stressor, can handle challenge
    
    Returns:
        IntensityLevel classification
    """
    text_lower = text.lower()
    
    # Check for severe patterns first (highest priority)
    severe_score = 0.0
    for pattern, weight in SEVERE_INTENSITY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            severe_score += weight
    
    if severe_score >= 4.0 or adversity_score >= 12.0:
        return IntensityLevel.SEVERE
    
    # Check for moderate patterns
    moderate_score = 0.0
    for pattern, weight in MODERATE_INTENSITY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            moderate_score += weight
    
    if moderate_score >= 3.0 or adversity_score >= 6.0:
        return IntensityLevel.MODERATE
    
    # Check for mild patterns (or default if adversity score is present but low)
    mild_score = 0.0
    for pattern, weight in MILD_INTENSITY_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            mild_score += weight
    
    if mild_score >= 1.0 or adversity_score >= 2.0:
        return IntensityLevel.MILD
    
    # Default based on adversity score
    if adversity_score > 0:
        return IntensityLevel.MILD
    return IntensityLevel.MILD  # Default when in adversity context


def analyze_esconv_strategies(text: str) -> ESConvAnalysis:
    """
    Analyze text for ESConv support strategies.
    Based on ACL 2021 ESConv framework (Helping Skills Theory).
    
    Returns:
        ESConvAnalysis with strategy breakdown
    """
    text_lower = text.lower()
    signals = []
    strategy_scores = {s: 0.0 for s in ESConvStrategy}
    
    for strategy, patterns in ESCONV_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                signals.append(ESConvSignal(
                    text=match.group(),
                    pattern=pattern,
                    weight=weight,
                    strategy=strategy
                ))
                strategy_scores[strategy] += weight
    
    # Calculate distribution
    total = sum(strategy_scores.values())
    distribution = {}
    if total > 0:
        distribution = {s: score / total for s, score in strategy_scores.items()}
    else:
        distribution = {s: 0.0 for s in ESConvStrategy}
    
    # Find dominant strategy
    dominant = None
    if total > 0:
        dominant = max(strategy_scores, key=strategy_scores.get)
        if strategy_scores[dominant] == 0:
            dominant = None
    
    # Assess balance
    balance = "balanced"
    if dominant:
        dominant_pct = distribution.get(dominant, 0)
        if dominant == ESConvStrategy.QUESTION and dominant_pct > 0.4:
            balance = "question-heavy (consider more support statements)"
        elif dominant == ESConvStrategy.SUGGESTION and dominant_pct > 0.4:
            balance = "advice-heavy (consider more exploration/validation)"
        elif dominant == ESConvStrategy.AFFIRMATION and dominant_pct > 0.5:
            balance = "validation-heavy (consider exploring or suggesting)"
        elif dominant == ESConvStrategy.INFORMATION and dominant_pct > 0.4:
            balance = "info-heavy (consider emotional validation)"
        elif dominant == ESConvStrategy.SELF_DISCLOSURE and dominant_pct > 0.4:
            balance = "self-disclosure heavy (refocus on them)"
    
    return ESConvAnalysis(
        strategies_detected=signals,
        strategy_distribution=distribution,
        dominant_strategy=dominant,
        balance_assessment=balance
    )


def analyze_over_support(text: str) -> OverSupportAnalysis:
    """
    Analyze text for over-support patterns that may harm rather than help.
    
    Based on:
    - Williamson et al. (2019): "excess support was associated with increased depressive symptoms"
    - Gray (2018): "You're Not Helping" — unhelpful workplace support as a job stressor
    - McLaren & High (2019): Support gaps framework — BOTH deficits AND surpluses cause harm
    
    Over-support harms by:
    - Signaling "you can't handle this" (self-efficacy threat)
    - Taking over agency (autonomy undermining)  
    - Minimizing real concerns (invalidation)
    - Blocking necessary emotional processing (silver lining too early)
    
    Returns:
        OverSupportAnalysis with breakdown
    """
    text_lower = text.lower()
    signals = []
    
    # Category mapping for patterns
    pattern_categories = {
        r"\b(don'?t worry|don'?t panic|don'?t stress)\b.*\b(everything|it'?s (okay|ok|fine|alright))\b": "reassurance",
        r"\b(everything (will|is going to) be (okay|ok|fine|alright))\b": "reassurance",
        r"\b(you'?ll be (okay|ok|fine|alright))\b": "reassurance",
        r"\b(you (just|simply) need to|all you (need|have) to do is)\b": "advice",
        r"\b(why don'?t you (just|simply))\b": "advice",
        r"\b(have you tried|did you try).*\b(have you tried|did you try)\b": "advice",
        r"\b(here'?s what (you should|i'?d|I would) do)\b": "advice",
        r"\b(you'?re (so|absolutely|completely|totally) (right|amazing|great|wonderful))\b": "validation",
        r"\b(poor (you|thing|baby))\b": "validation",
        r"\b(let me (handle|do|take care of) (this|it|that) for you)\b": "agency",
        r"\b(i'?ll (fix|solve|handle) (this|it|that))\b": "agency",
        r"\b(you (shouldn'?t|don'?t) have to (deal|worry|think) about)\b": "agency",
        r"\b(at least|but at least|well at least)\b": "minimizing",
        r"\b(it could be worse|could be worse|worse things happen)\b": "minimizing",
        r"\b(it'?s not (that|so) bad|not the end of the world)\b": "minimizing",
        r"\b(everyone (goes through|deals with|has))\b": "minimizing",
        r"\b(blessing in disguise|for the best|meant to be|happens for a reason)\b": "silver_lining",
        r"\b(bright side|look on the bright side|silver lining)\b": "silver_lining",
        r"\b(at least you (can|have|got|learned))\b": "silver_lining",
    }
    
    category_scores = {
        "reassurance": 0.0,
        "advice": 0.0,
        "validation": 0.0,
        "agency": 0.0,
        "minimizing": 0.0,
        "silver_lining": 0.0,
    }
    
    for pattern, weight in OVER_SUPPORT_PATTERNS:
        matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
        category = pattern_categories.get(pattern, "other")
        for match in matches:
            signals.append(OverSupportSignal(
                text=match.group(),
                pattern=pattern,
                weight=weight,
                category=category
            ))
            if category in category_scores:
                category_scores[category] += weight
    
    total_score = sum(s.weight for s in signals)
    
    # Threshold for "excessive" — more than 5.0 suggests significant over-support
    is_excessive = total_score >= 5.0
    
    # Find dominant category
    dominant = None
    if any(v > 0 for v in category_scores.values()):
        dominant = max(category_scores, key=category_scores.get)
        if category_scores[dominant] == 0:
            dominant = None
    
    return OverSupportAnalysis(
        signals=signals,
        total_score=total_score,
        is_excessive=is_excessive,
        category_scores=category_scores,
        dominant_category=dominant
    )


def analyze_appraisal_domains(text: str) -> AppraisalResult:
    """
    Decompose the appraisal to identify what domain(s) the issue is about.
    
    Returns:
        AppraisalResult with domain breakdown
    """
    text_lower = text.lower()
    domain_scores = {d: 0.0 for d in AppraisalDomain}
    keywords = []
    
    for domain, patterns in APPRAISAL_DOMAIN_PATTERNS.items():
        for pattern, weight in patterns:
            matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
            for match in matches:
                domain_scores[domain] += weight
                keywords.append(match.group())
    
    # Get domains with non-zero scores
    detected_domains = [d for d, score in domain_scores.items() if score > 0]
    
    # Primary domain is highest scoring
    primary = AppraisalDomain.UNKNOWN
    if detected_domains:
        primary = max(detected_domains, key=lambda d: domain_scores[d])
    
    # If nothing detected, mark as unknown
    if not detected_domains:
        detected_domains = [AppraisalDomain.UNKNOWN]
    
    return AppraisalResult(
        domains=detected_domains,
        primary_domain=primary,
        domain_scores=domain_scores,
        keywords=list(set(keywords))[:10]  # Unique, max 10
    )


def detect_mismatches(
    context: SupportContext,
    intensity: Optional[IntensityLevel],
    support_signals: List[SupportSignal],
    esconv_analysis: Optional[ESConvAnalysis],
    over_support: Optional[OverSupportAnalysis] = None
) -> List[MismatchAlert]:
    """
    Detect mismatches between support provided and context/intensity.
    
    Returns:
        List of MismatchAlert for problematic patterns
    """
    alerts = []
    
    if not support_signals:
        return alerts
    
    # Categorize support signals
    sos_types = {SupportType.SOS_COMFORT, SupportType.SOS_FORTIFY,
                 SupportType.SOS_RECONSTRUCT, SupportType.SOS_REFRAME}
    rc_types = {SupportType.RC_NURTURE, SupportType.RC_PERCEIVE,
                SupportType.RC_PREPARE, SupportType.RC_LAUNCH}
    
    sos_score = sum(s.weight for s in support_signals if s.support_type in sos_types)
    rc_score = sum(s.weight for s in support_signals if s.support_type in rc_types)
    challenge_score = sum(s.weight for s in support_signals if s.support_type == SupportType.CHALLENGE)
    reframe_score = sum(s.weight for s in support_signals if s.support_type == SupportType.SOS_REFRAME)
    
    # CRITICAL: Challenge during SEVERE adversity
    if context == SupportContext.ADVERSITY and intensity == IntensityLevel.SEVERE:
        if challenge_score > 0:
            alerts.append(MismatchAlert(
                severity="CRITICAL",
                message="🚨 CHALLENGING DURING SEVERE DISTRESS",
                context=context,
                problematic_support=f"Challenge signals detected (score: {challenge_score:.1f})",
                recommendation="STOP challenging. Provide pure comfort and validation. Person is in crisis."
            ))
        if rc_score > sos_score:
            alerts.append(MismatchAlert(
                severity="CRITICAL",
                message="🚨 RC SUPPORT DURING SEVERE DISTRESS",
                context=context,
                problematic_support=f"RC support ({rc_score:.1f}) exceeds SOS ({sos_score:.1f})",
                recommendation="Switch to SOS immediately. Safe haven first, not growth pushing."
            ))
        if reframe_score > sos_score * 0.5:
            alerts.append(MismatchAlert(
                severity="CRITICAL",
                message="🚨 PREMATURE REFRAMING DURING CRISIS",
                context=context,
                problematic_support=f"Heavy reframing (score: {reframe_score:.1f}) during severe distress",
                recommendation="Too early to reframe. Validate pain first. 'Silver lining' thinking can feel dismissive."
            ))
    
    # WARNING: RC support during adversity (moderate)
    if context == SupportContext.ADVERSITY and intensity == IntensityLevel.MODERATE:
        if rc_score > sos_score * 1.5:
            alerts.append(MismatchAlert(
                severity="WARNING",
                message="⚠️ RC SUPPORT DURING ADVERSITY",
                context=context,
                problematic_support=f"RC support dominant ({rc_score:.1f} vs SOS {sos_score:.1f})",
                recommendation="Person is struggling. Prioritize SOS support before growth-oriented help."
            ))
        if challenge_score > 2.0:
            alerts.append(MismatchAlert(
                severity="WARNING",
                message="⚠️ CHALLENGE DURING MODERATE DISTRESS",
                context=context,
                problematic_support=f"Challenge signals detected (score: {challenge_score:.1f})",
                recommendation="Consider softening challenge. Fortify first, challenge later."
            ))
    
    # WARNING: Too much comfort during pure growth context
    if context == SupportContext.GROWTH:
        if sos_score > rc_score * 2 and rc_score > 0:
            alerts.append(MismatchAlert(
                severity="WARNING",
                message="⚠️ EXCESSIVE COMFORT IN GROWTH CONTEXT",
                context=context,
                problematic_support=f"SOS support ({sos_score:.1f}) dominates RC ({rc_score:.1f})",
                recommendation="Person is ready for growth. Consider more RC support (challenge, launch, prepare)."
            ))
    
    # Check ESConv balance issues
    if esconv_analysis and esconv_analysis.dominant_strategy:
        if context == SupportContext.ADVERSITY:
            # Too much advice during adversity
            if esconv_analysis.dominant_strategy == ESConvStrategy.SUGGESTION:
                suggestion_pct = esconv_analysis.strategy_distribution.get(ESConvStrategy.SUGGESTION, 0)
                if suggestion_pct > 0.35:
                    alerts.append(MismatchAlert(
                        severity="WARNING",
                        message="⚠️ ADVICE-HEAVY DURING ADVERSITY",
                        context=context,
                        problematic_support=f"Suggestions dominate ({suggestion_pct:.0%} of response)",
                        recommendation="More validation and reflection before suggesting. Ask 'what do you need?' not 'you should...'"
                    ))
            # Too much information during adversity
            if esconv_analysis.dominant_strategy == ESConvStrategy.INFORMATION:
                info_pct = esconv_analysis.strategy_distribution.get(ESConvStrategy.INFORMATION, 0)
                if info_pct > 0.35:
                    alerts.append(MismatchAlert(
                        severity="WARNING",
                        message="⚠️ INFO-HEAVY DURING ADVERSITY",
                        context=context,
                        problematic_support=f"Information dominates ({info_pct:.0%} of response)",
                        recommendation="Facts don't heal feelings. Validate emotions first, inform later."
                    ))
    
    # =====================
    # OVER-SUPPORT DETECTION
    # =====================
    # Based on Williamson et al. (2019): "excess support was associated with increased depressive symptoms"
    # Both deficits AND surpluses cause harm (McLaren & High 2019)
    
    if over_support and over_support.is_excessive:
        # CRITICAL: Over-support during severe adversity compounds harm
        if context == SupportContext.ADVERSITY and intensity == IntensityLevel.SEVERE:
            if over_support.dominant_category == "minimizing":
                alerts.append(MismatchAlert(
                    severity="CRITICAL",
                    message="🚨 MINIMIZING DURING SEVERE DISTRESS",
                    context=context,
                    problematic_support=f"Minimizing signals detected (score: {over_support.category_scores.get('minimizing', 0):.1f})",
                    recommendation="STOP minimizing. 'At least' and 'could be worse' statements invalidate real pain."
                ))
            if over_support.dominant_category == "silver_lining":
                alerts.append(MismatchAlert(
                    severity="CRITICAL",
                    message="🚨 SILVER LINING DURING CRISIS",
                    context=context,
                    problematic_support=f"Silver lining signals detected (score: {over_support.category_scores.get('silver_lining', 0):.1f})",
                    recommendation="Too early to reframe. Allow grief/processing. 'Blessing in disguise' blocks healing."
                ))
            if over_support.dominant_category == "agency":
                alerts.append(MismatchAlert(
                    severity="CRITICAL",
                    message="🚨 TAKING OVER AGENCY DURING CRISIS",
                    context=context,
                    problematic_support=f"Agency-taking signals detected (score: {over_support.category_scores.get('agency', 0):.1f})",
                    recommendation="Don't solve FOR them in crisis. Offer to help, don't take over. 'What do you need?' not 'I'll fix it.'"
                ))
        
        # WARNING: Over-support in moderate adversity
        elif context == SupportContext.ADVERSITY and intensity == IntensityLevel.MODERATE:
            if over_support.dominant_category == "minimizing":
                alerts.append(MismatchAlert(
                    severity="WARNING",
                    message="⚠️ MINIMIZING LANGUAGE DETECTED",
                    context=context,
                    problematic_support=f"Minimizing patterns (score: {over_support.category_scores.get('minimizing', 0):.1f})",
                    recommendation="Validate before comparing. 'At least' can feel dismissive."
                ))
            if over_support.dominant_category == "advice":
                alerts.append(MismatchAlert(
                    severity="WARNING",
                    message="⚠️ EXCESSIVE UNSOLICITED ADVICE",
                    context=context,
                    problematic_support=f"Heavy advice patterns (score: {over_support.category_scores.get('advice', 0):.1f})",
                    recommendation="Ask before advising. 'Would you like suggestions?' respects autonomy."
                ))
        
        # WARNING: Over-support in GROWTH context (the research-backed finding!)
        # Williamson et al. (2019): Excess support → increased depressive symptoms
        elif context == SupportContext.GROWTH:
            if over_support.dominant_category in ("reassurance", "validation"):
                alerts.append(MismatchAlert(
                    severity="WARNING",
                    message="⚠️ EXCESSIVE REASSURANCE IN GROWTH CONTEXT",
                    context=context,
                    problematic_support=f"Over-reassurance detected (score: {over_support.total_score:.1f})",
                    recommendation="Person is growing, not struggling. Excessive comfort can signal 'you can't handle this' and undermine self-efficacy."
                ))
            if over_support.dominant_category == "agency":
                alerts.append(MismatchAlert(
                    severity="WARNING",
                    message="⚠️ TAKING OVER IN GROWTH CONTEXT",
                    context=context,
                    problematic_support=f"Agency-taking signals (score: {over_support.category_scores.get('agency', 0):.1f})",
                    recommendation="Let them own their growth. Offer to help IF asked. 'I'll handle it' undermines development."
                ))
        
        # General over-support alert for any excessive score
        if over_support.total_score >= 8.0 and not any(a.severity == "CRITICAL" for a in alerts):
            alerts.append(MismatchAlert(
                severity="WARNING",
                message="⚠️ HIGH OVER-SUPPORT SCORE",
                context=context,
                problematic_support=f"Combined over-support score: {over_support.total_score:.1f} (threshold: 5.0)",
                recommendation="Research shows excess support causes harm (Williamson et al. 2019). Balance support with space for autonomy."
            ))
    
    return alerts


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
                          growth_signals: List[GrowthSignal], context_match: bool,
                          intensity: Optional[IntensityLevel] = None,
                          appraisal: Optional[AppraisalResult] = None) -> str:
    """Generate a recommendation for appropriate support."""
    
    if context == SupportContext.ADVERSITY:
        categories = set(s.category for s in adversity_signals)
        
        # Intensity-specific guidance
        intensity_guidance = ""
        if intensity == IntensityLevel.SEVERE:
            intensity_guidance = "\n  ⚠️ SEVERE INTENSITY — Pure support only, NO challenge\n"
        elif intensity == IntensityLevel.MODERATE:
            intensity_guidance = "\n  📊 MODERATE — Comfort first, gentle guidance okay\n"
        else:
            intensity_guidance = "\n  📊 MILD — Can balance support with light challenge\n"
        
        rec = f"ADVERSITY CONTEXT — Provide SOS support:{intensity_guidance}"
        rec += "  • Start with comfort/safe haven (validate, empathize)\n"
        if "emotional" in categories:
            rec += "  • Address emotional needs first before problem-solving\n"
        rec += "  • Then fortify (remind of strengths, past resilience)\n"
        
        if intensity != IntensityLevel.SEVERE:
            rec += "  • Gradually introduce reframing (adversity → growth)\n"
            rec += "  • Challenge/RC support comes AFTER stability is restored"
        else:
            rec += "  • Hold reframing until stability returns\n"
            rec += "  • No 'silver lining' or 'at least' statements right now"
        
        # Domain-specific guidance
        if appraisal and appraisal.primary_domain != AppraisalDomain.UNKNOWN:
            rec += f"\n\n  Domain: {appraisal.primary_domain.name}"
            if appraisal.primary_domain == AppraisalDomain.WORK:
                rec += " — Validate professional stress; avoid immediate problem-solving"
            elif appraisal.primary_domain == AppraisalDomain.RELATIONSHIPS:
                rec += " — Focus on their feelings, not fixing the other person"
            elif appraisal.primary_domain == AppraisalDomain.HEALTH:
                rec += " — Be present; avoid toxic positivity about illness"
            elif appraisal.primary_domain == AppraisalDomain.LOSS:
                rec += " — Witness grief; don't rush healing timeline"
    
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
        
        # Domain-specific guidance
        if appraisal and appraisal.primary_domain != AppraisalDomain.UNKNOWN:
            rec += f"\n\n  Domain: {appraisal.primary_domain.name}"
            if appraisal.primary_domain == AppraisalDomain.WORK:
                rec += " — Support career ambition; challenge comfort zones"
            elif appraisal.primary_domain == AppraisalDomain.ACADEMIC:
                rec += " — Encourage stretch goals; help with planning"
    
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
    
    # NEW: Analyze intensity (only for adversity contexts)
    intensity = None
    if context in (SupportContext.ADVERSITY, SupportContext.TRANSITION):
        intensity = analyze_intensity(user_text, adversity_score)
    
    # NEW: Analyze appraisal domains
    appraisal = analyze_appraisal_domains(user_text)
    
    # Analyze AI response for support type (if provided)
    support_signals = []
    context_match = True
    match_explanation = "No AI response provided for analysis"
    esconv_analysis = None
    mismatch_alerts = []
    over_support = None
    
    if ai_response:
        _, support_signals = analyze_text_for_support(ai_response)
        context_match, match_explanation = assess_support_match(context, support_signals)
        
        # NEW: Analyze ESConv strategies in response
        esconv_analysis = analyze_esconv_strategies(ai_response)
        
        # NEW: Analyze over-support patterns (research-backed: excess support causes harm)
        over_support = analyze_over_support(ai_response)
        
        # NEW: Detect mismatches (including over-support)
        mismatch_alerts = detect_mismatches(context, intensity, support_signals, esconv_analysis, over_support)
        
        # Update context_match if there are critical alerts
        if any(a.severity == "CRITICAL" for a in mismatch_alerts):
            context_match = False
    
    # Generate recommendation
    recommendation = generate_recommendation(
        context, adversity_signals, growth_signals, context_match,
        intensity=intensity, appraisal=appraisal
    )
    
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
        },
        intensity=intensity,
        esconv_analysis=esconv_analysis,
        appraisal=appraisal,
        mismatch_alerts=mismatch_alerts,
        over_support=over_support,
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
    
    intensity_emoji = {
        IntensityLevel.SEVERE: "🔴🔴🔴 SEVERE",
        IntensityLevel.MODERATE: "🟠🟠 MODERATE",
        IntensityLevel.MILD: "🟡 MILD",
    }
    
    lines = []
    lines.append("=" * 60)
    lines.append("          SUPPORT CONTEXT ANALYSIS")
    lines.append("=" * 60)
    
    # ================
    # MISMATCH ALERTS (most prominent, at top)
    # ================
    if analysis.mismatch_alerts:
        lines.append("")
        lines.append("╔" + "═" * 58 + "╗")
        for alert in analysis.mismatch_alerts:
            if alert.severity == "CRITICAL":
                lines.append(f"║  {alert.message:^54}  ║")
            else:
                lines.append(f"║  {alert.message:^54}  ║")
        lines.append("╚" + "═" * 58 + "╝")
        lines.append("")
        for alert in analysis.mismatch_alerts:
            lines.append(f"  Problem: {alert.problematic_support}")
            lines.append(f"  Action:  {alert.recommendation}")
            lines.append("")
    
    lines.append(f"Context: {status_emoji.get(analysis.context, '?')} {analysis.context.name}")
    lines.append(f"Confidence: {analysis.confidence:.0%}")
    
    # Intensity (if adversity)
    if analysis.intensity:
        lines.append(f"Intensity: {intensity_emoji.get(analysis.intensity, '?')}")
    
    lines.append(f"\nScores:")
    lines.append(f"  Adversity: {analysis.adversity_score:.1f}")
    lines.append(f"  Growth:    {analysis.growth_score:.1f}")
    
    # Appraisal domains
    if analysis.appraisal and analysis.appraisal.primary_domain != AppraisalDomain.UNKNOWN:
        lines.append(f"\nAppraisal Domain: {analysis.appraisal.primary_domain.name}")
        if len(analysis.appraisal.domains) > 1:
            other_domains = [d.name for d in analysis.appraisal.domains 
                          if d != analysis.appraisal.primary_domain and d != AppraisalDomain.UNKNOWN]
            if other_domains:
                lines.append(f"  Also related to: {', '.join(other_domains)}")
        if analysis.appraisal.keywords:
            lines.append(f"  Keywords: {', '.join(analysis.appraisal.keywords[:5])}")
    
    if analysis.support_signals:
        lines.append(f"\nSupport Match: {'✓' if analysis.context_match else '✗'} {analysis.details.get('match_explanation', '')}")
    
    # Over-support analysis
    if analysis.over_support and analysis.over_support.total_score > 0:
        lines.append(f"\nOver-Support Score: {analysis.over_support.total_score:.1f} {'⚠️ EXCESSIVE' if analysis.over_support.is_excessive else '(within range)'}")
        if analysis.over_support.dominant_category:
            lines.append(f"  Dominant type: {analysis.over_support.dominant_category}")
    
    # ESConv Strategy Analysis
    if analysis.esconv_analysis and analysis.esconv_analysis.strategies_detected:
        lines.append(f"\nESConv Strategies:")
        lines.append(f"  Balance: {analysis.esconv_analysis.balance_assessment}")
        if analysis.esconv_analysis.dominant_strategy:
            lines.append(f"  Dominant: {analysis.esconv_analysis.dominant_strategy.name}")
        
        if verbose:
            lines.append("  Distribution:")
            sorted_strategies = sorted(
                analysis.esconv_analysis.strategy_distribution.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for strategy, pct in sorted_strategies:
                if pct > 0:
                    bar = "█" * int(pct * 20)
                    lines.append(f"    {strategy.name:15} {bar} {pct:.0%}")
    
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
        
        if analysis.esconv_analysis and analysis.esconv_analysis.strategies_detected:
            lines.append("\nESConv Signals Detected:")
            for s in analysis.esconv_analysis.strategies_detected[:5]:
                lines.append(f"  [{s.strategy.name}] \"{s.text}\"")
    
    lines.append("\n" + "-" * 60)
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
                    "intensity": a.intensity.name if a.intensity else None,
                    "primary_domain": a.appraisal.primary_domain.name if a.appraisal else None,
                    "mismatch_alert_count": len(a.mismatch_alerts),
                    "critical_alerts": len([x for x in a.mismatch_alerts if x.severity == "CRITICAL"]),
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
    
    # Summarize intensity distribution
    intensity_counts = {}
    for a in all_analyses:
        if a.intensity:
            intensity_counts[a.intensity.name] = intensity_counts.get(a.intensity.name, 0) + 1
    
    if intensity_counts:
        lines.append("\nIntensity Distribution:")
        for intensity, count in sorted(intensity_counts.items()):
            emoji = {"SEVERE": "🔴🔴🔴", "MODERATE": "🟠🟠", "MILD": "🟡"}.get(intensity, "?")
            lines.append(f"  {emoji} {intensity}: {count}")
    
    # Count mismatches
    total_critical = sum(len([x for x in a.mismatch_alerts if x.severity == "CRITICAL"]) for a in all_analyses)
    total_warning = sum(len([x for x in a.mismatch_alerts if x.severity == "WARNING"]) for a in all_analyses)
    
    if total_critical > 0 or total_warning > 0:
        lines.append("\nMismatch Alerts:")
        if total_critical > 0:
            lines.append(f"  🚨 CRITICAL: {total_critical}")
        if total_warning > 0:
            lines.append(f"  ⚠️ WARNING: {total_warning}")
    
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
