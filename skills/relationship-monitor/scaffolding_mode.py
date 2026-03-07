#!/usr/bin/env python3
"""
Scaffolding Mode Module

Detects opportunities for scaffolding vs direct answering,
provides scaffolding prompts, and tracks competence development.

Based on Vygotsky's Zone of Proximal Development and Socratic Method.

Key insight: Direct answering creates dependency. Scaffolding builds competence.
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class RequestType(Enum):
    """Types of requests that determine scaffolding approach."""
    
    # Direct answer appropriate
    FACTUAL_LOOKUP = "factual_lookup"          # "What time is my meeting?"
    EMERGENCY = "emergency"                      # Urgent situations
    EXPLICIT_DIRECT = "explicit_direct"          # "Just tell me the answer"
    
    # Scaffolding appropriate
    PROBLEM_SOLVING = "problem_solving"          # "How do I fix X?"
    DECISION_MAKING = "decision_making"          # "Should I do X or Y?"
    SKILL_BUILDING = "skill_building"            # "How do I learn to X?"
    CREATIVE = "creative"                        # "Help me write/design X"
    DEBUGGING = "debugging"                      # "Why isn't X working?"
    UNDERSTANDING = "understanding"              # "Help me understand X"


@dataclass
class ScaffoldingAnalysis:
    """Result of analyzing a request for scaffolding opportunity."""
    
    request_type: RequestType
    scaffold_appropriate: bool
    confidence: float
    suggested_approach: str
    initial_questions: list[str]
    reasoning: str


class ScaffoldingDetector:
    """Detects scaffolding opportunities and provides approaches."""
    
    # Patterns indicating direct answer requests
    FACTUAL_PATTERNS = [
        r"what time",
        r"when is",
        r"what's the date",
        r"how many",
        r"what's my",
        r"where is",
        r"who is",
        r"what is (the|a) \w+$",  # Simple definition lookups
        r"what's the (capital|population|name|title)",  # Factual lookups
        r"what is the (capital|population|name|title)",
        r"capital of",
    ]
    
    EMERGENCY_PATTERNS = [
        r"urgent",
        r"emergency",
        r"asap",
        r"right now",
        r"immediately",
        r"help!",
    ]
    
    EXPLICIT_DIRECT_PATTERNS = [
        r"just tell me",
        r"give me the answer",
        r"what's the solution",
        r"don't ask me",
        r"i don't want to think",
        r"skip the questions",
    ]
    
    # Patterns indicating scaffolding opportunities
    PROBLEM_SOLVING_PATTERNS = [
        r"how (do|can|should) i",
        r"fix",
        r"solve",
        r"figure out",
        r"what should i do about",
        r"how to",
    ]
    
    DECISION_PATTERNS = [
        r"should i",
        r"or should",
        r"which (one|option|approach)",
        r"what would you",
        r"better to",
        r"choose between",
        r"trying to decide",
    ]
    
    DEBUGGING_PATTERNS = [
        r"doesn't work",
        r"isn't working",
        r"error",
        r"bug",
        r"why (is|does|doesn't)",
        r"what's wrong with",
        r"broken",
    ]
    
    UNDERSTANDING_PATTERNS = [
        r"explain",
        r"understand",
        r"what does .+ mean",
        r"why does",
        r"how does .+ work",
        r"confused about",
        r"clarify",
    ]
    
    CREATIVE_PATTERNS = [
        r"help me (write|draft|create|design)",
        r"write (a|an|some)",
        r"ideas for",
        r"brainstorm",
        r"come up with",
    ]
    
    SKILL_BUILDING_PATTERNS = [
        r"learn (to|how)",
        r"get better at",
        r"improve my",
        r"teach me",
        r"want to understand",
    ]
    
    # Scaffolding questions by request type
    SCAFFOLDING_QUESTIONS = {
        RequestType.PROBLEM_SOLVING: [
            "What have you tried so far?",
            "What do you think might be causing this?",
            "What would you try if you had to solve this without me?",
            "What similar problems have you solved before?",
            "What's your intuition telling you?",
        ],
        RequestType.DECISION_MAKING: [
            "What are the main tradeoffs you're weighing?",
            "Which factors matter most to you?",
            "What does your gut say?",
            "What would you advise a friend in this situation?",
            "What's the worst case for each option?",
            "If you had to decide right now, what would you choose?",
        ],
        RequestType.DEBUGGING: [
            "When did it last work?",
            "What changed since then?",
            "What does the error message actually say?",
            "Have you tried isolating the problem?",
            "What's your hypothesis about what's happening?",
        ],
        RequestType.UNDERSTANDING: [
            "What do you already know about this?",
            "What specifically is confusing?",
            "How does this connect to things you understand well?",
            "Can you explain back what you think it means?",
            "What would change if you understood this better?",
        ],
        RequestType.CREATIVE: [
            "What's the core message or feeling you want to convey?",
            "Who's the audience?",
            "What constraints are you working with?",
            "What examples do you find inspiring?",
            "What have you drafted so far?",
        ],
        RequestType.SKILL_BUILDING: [
            "What do you already know about this?",
            "Why do you want to learn this now?",
            "How do you learn best?",
            "What's the smallest first step you could take?",
            "Who do you know who's good at this?",
        ],
    }
    
    def analyze(self, message: str) -> ScaffoldingAnalysis:
        """Analyze a message for scaffolding opportunity."""
        message_lower = message.lower()
        
        # Check for direct answer patterns first (takes priority)
        for pattern in self.EXPLICIT_DIRECT_PATTERNS:
            if re.search(pattern, message_lower):
                return ScaffoldingAnalysis(
                    request_type=RequestType.EXPLICIT_DIRECT,
                    scaffold_appropriate=False,
                    confidence=0.9,
                    suggested_approach="Direct answer requested. Respect the preference, but consider asking if they'd like to try working through it after getting the answer.",
                    initial_questions=[],
                    reasoning="Explicit request for direct answer detected.",
                )
        
        for pattern in self.EMERGENCY_PATTERNS:
            if re.search(pattern, message_lower):
                return ScaffoldingAnalysis(
                    request_type=RequestType.EMERGENCY,
                    scaffold_appropriate=False,
                    confidence=0.85,
                    suggested_approach="Emergency/urgent situation. Provide direct help immediately.",
                    initial_questions=[],
                    reasoning="Emergency indicators detected.",
                )
        
        for pattern in self.FACTUAL_PATTERNS:
            if re.search(pattern, message_lower):
                return ScaffoldingAnalysis(
                    request_type=RequestType.FACTUAL_LOOKUP,
                    scaffold_appropriate=False,
                    confidence=0.8,
                    suggested_approach="Simple factual lookup. Scaffolding would be inefficient here.",
                    initial_questions=[],
                    reasoning="Factual lookup pattern detected.",
                )
        
        # Check scaffolding-appropriate patterns
        detected_type = None
        confidence = 0.0
        
        pattern_checks = [
            (self.DECISION_PATTERNS, RequestType.DECISION_MAKING, 0.9),
            (self.DEBUGGING_PATTERNS, RequestType.DEBUGGING, 0.85),
            (self.PROBLEM_SOLVING_PATTERNS, RequestType.PROBLEM_SOLVING, 0.85),
            (self.UNDERSTANDING_PATTERNS, RequestType.UNDERSTANDING, 0.85),
            (self.SKILL_BUILDING_PATTERNS, RequestType.SKILL_BUILDING, 0.9),
            (self.CREATIVE_PATTERNS, RequestType.CREATIVE, 0.85),
        ]
        
        for patterns, req_type, conf in pattern_checks:
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    if conf > confidence:
                        detected_type = req_type
                        confidence = conf
        
        if detected_type:
            questions = self.SCAFFOLDING_QUESTIONS.get(detected_type, [])
            approach = self._get_approach(detected_type)
            return ScaffoldingAnalysis(
                request_type=detected_type,
                scaffold_appropriate=True,
                confidence=confidence,
                suggested_approach=approach,
                initial_questions=questions[:3],  # Start with 3 questions
                reasoning=f"Detected {detected_type.value} request. Scaffolding can build competence here.",
            )
        
        # Default: uncertain, lean toward scaffolding
        return ScaffoldingAnalysis(
            request_type=RequestType.PROBLEM_SOLVING,
            scaffold_appropriate=True,
            confidence=0.5,
            suggested_approach="Uncertain request type. Default to scaffolding: ask what they've tried and what they think before providing answers.",
            initial_questions=[
                "What have you tried so far?",
                "What's your current thinking on this?",
            ],
            reasoning="No clear pattern detected. Defaulting to scaffolding approach.",
        )
    
    def _get_approach(self, request_type: RequestType) -> str:
        """Get suggested approach for request type."""
        approaches = {
            RequestType.PROBLEM_SOLVING: (
                "Ask what they've tried first. Understand their current approach. "
                "Provide frameworks and guiding questions rather than direct solutions. "
                "Let them generate the answer with your guidance."
            ),
            RequestType.DECISION_MAKING: (
                "Help them articulate the tradeoffs. Ask which factors matter most. "
                "Don't make the decision for them — help them clarify their own values "
                "so the decision becomes obvious."
            ),
            RequestType.DEBUGGING: (
                "Start with 'When did it last work?' and 'What changed?' "
                "Guide them through systematic isolation. Let them form hypotheses. "
                "Point toward areas to investigate rather than providing the fix."
            ),
            RequestType.UNDERSTANDING: (
                "Ask what they already know. Build on existing knowledge. "
                "Use analogies to familiar concepts. Ask them to explain back. "
                "The goal is internalization, not just information transfer."
            ),
            RequestType.CREATIVE: (
                "Start with audience and purpose. Ask what they've drafted. "
                "Provide structure and frameworks, not content. "
                "Let them generate ideas; refine together."
            ),
            RequestType.SKILL_BUILDING: (
                "Understand their learning style and motivation. "
                "Point to resources rather than teaching directly. "
                "Help them find first steps and mentors. Track progress."
            ),
        }
        return approaches.get(request_type, "Ask before answering. Scaffold when possible.")


@dataclass
class CompetenceGrowth:
    """Track competence development over time."""
    
    domain: str
    initial_level: str  # Description of starting point
    current_level: str  # Description of current capability
    evidence: list[str]  # Specific examples of growth
    first_observed: str  # ISO date
    last_updated: str  # ISO date


class CompetenceTracker:
    """Track competence development across domains."""
    
    def __init__(self, data_path: str = "competence_growth.json"):
        self.data_path = data_path
        self.domains: dict[str, CompetenceGrowth] = {}
        self._load()
    
    def _load(self) -> None:
        """Load existing competence data."""
        try:
            with open(self.data_path) as f:
                data = json.load(f)
                for domain, info in data.items():
                    self.domains[domain] = CompetenceGrowth(**info)
        except FileNotFoundError:
            self.domains = {}
    
    def _save(self) -> None:
        """Save competence data."""
        data = {}
        for domain, growth in self.domains.items():
            data[domain] = {
                "domain": growth.domain,
                "initial_level": growth.initial_level,
                "current_level": growth.current_level,
                "evidence": growth.evidence,
                "first_observed": growth.first_observed,
                "last_updated": growth.last_updated,
            }
        with open(self.data_path, "w") as f:
            json.dump(data, f, indent=2)
    
    def record_growth(
        self,
        domain: str,
        evidence: str,
        new_level: str | None = None,
    ) -> None:
        """Record evidence of competence growth."""
        now = datetime.now().isoformat()
        
        if domain not in self.domains:
            self.domains[domain] = CompetenceGrowth(
                domain=domain,
                initial_level="Learning",
                current_level=new_level or "Developing",
                evidence=[evidence],
                first_observed=now,
                last_updated=now,
            )
        else:
            growth = self.domains[domain]
            growth.evidence.append(evidence)
            if new_level:
                growth.current_level = new_level
            growth.last_updated = now
        
        self._save()
    
    def get_summary(self) -> str:
        """Get summary of competence growth across domains."""
        if not self.domains:
            return "No competence growth tracked yet."
        
        lines = ["# Competence Growth Summary\n"]
        for domain, growth in self.domains.items():
            lines.append(f"## {domain}")
            lines.append(f"- **Journey:** {growth.initial_level} → {growth.current_level}")
            lines.append(f"- **First observed:** {growth.first_observed[:10]}")
            lines.append(f"- **Evidence ({len(growth.evidence)} instances):**")
            for ev in growth.evidence[-3:]:  # Last 3 examples
                lines.append(f"  - {ev}")
            lines.append("")
        
        return "\n".join(lines)


def analyze_request(message: str) -> dict[str, Any]:
    """Analyze a request and return scaffolding guidance."""
    detector = ScaffoldingDetector()
    analysis = detector.analyze(message)
    
    return {
        "request_type": analysis.request_type.value,
        "scaffold_appropriate": analysis.scaffold_appropriate,
        "confidence": analysis.confidence,
        "suggested_approach": analysis.suggested_approach,
        "initial_questions": analysis.initial_questions,
        "reasoning": analysis.reasoning,
    }


def format_scaffolding_guidance(analysis: dict[str, Any]) -> str:
    """Format scaffolding analysis as readable guidance."""
    lines = ["## Scaffolding Analysis\n"]
    
    if analysis["scaffold_appropriate"]:
        lines.append("🎓 **Scaffolding Recommended**\n")
    else:
        lines.append("💡 **Direct Answer Appropriate**\n")
    
    lines.append(f"**Request Type:** {analysis['request_type']}")
    lines.append(f"**Confidence:** {analysis['confidence']:.0%}")
    lines.append(f"\n**Approach:**\n{analysis['suggested_approach']}")
    
    if analysis["initial_questions"]:
        lines.append("\n**Start with these questions:**")
        for q in analysis["initial_questions"]:
            lines.append(f"- {q}")
    
    lines.append(f"\n**Reasoning:** {analysis['reasoning']}")
    
    return "\n".join(lines)


# Test cases
def test_detector():
    """Test the scaffolding detector with various inputs."""
    detector = ScaffoldingDetector()
    
    test_cases = [
        # Should scaffold
        ("How do I fix this bug in my code?", True),
        ("Should I take the job offer or wait?", True),
        ("Help me understand recursion", True),
        ("I'm trying to decide between these options", True),
        ("My server isn't working", True),
        ("How can I get better at writing?", True),
        
        # Should NOT scaffold
        ("What time is my meeting today?", False),
        ("Just tell me the answer", False),
        ("This is urgent, I need help now", False),
        ("What's the capital of France?", False),
    ]
    
    print("Testing Scaffolding Detector\n" + "=" * 40)
    
    for message, expected_scaffold in test_cases:
        analysis = detector.analyze(message)
        result = "✅" if analysis.scaffold_appropriate == expected_scaffold else "❌"
        print(f"\n{result} '{message[:50]}...'")
        print(f"   Type: {analysis.request_type.value}")
        print(f"   Scaffold: {analysis.scaffold_appropriate} (expected: {expected_scaffold})")
        print(f"   Confidence: {analysis.confidence:.0%}")


if __name__ == "__main__":
    test_detector()
    
    # Demo with a sample message
    print("\n" + "=" * 40)
    print("\nDemo Analysis:")
    sample = "I'm trying to decide whether to accept the job offer from Anthropic or keep interviewing"
    analysis = analyze_request(sample)
    print(format_scaffolding_guidance(analysis))
