# Scaffolding Mode

Part of the relationship-monitor skill.

## Purpose

Detect opportunities to scaffold learning rather than simply answer questions. Based on Vygotsky's Zone of Proximal Development and the Socratic Method.

**Core insight:** Direct answering creates dependency. Scaffolding builds competence.

## Usage

```python
from scaffolding_mode import analyze_request, format_scaffolding_guidance

# Analyze a request
analysis = analyze_request("Should I take the job offer or keep interviewing?")

# Get formatted guidance
print(format_scaffolding_guidance(analysis))
```

### Output

```
## Scaffolding Analysis

🎓 **Scaffolding Recommended**

**Request Type:** decision_making
**Confidence:** 90%

**Approach:**
Help them articulate the tradeoffs. Ask which factors matter most.
Don't make the decision for them — help them clarify their own values
so the decision becomes obvious.

**Start with these questions:**
- What are the main tradeoffs you're weighing?
- Which factors matter most to you?
- What does your gut say?

**Reasoning:** Detected decision_making request. Scaffolding can build competence here.
```

## Request Types

### Scaffold-Appropriate

| Type | Pattern | Approach |
|------|---------|----------|
| **problem_solving** | "How do I...", "fix", "figure out" | Ask what they've tried. Provide frameworks, not solutions. |
| **decision_making** | "Should I...", "which option" | Help articulate tradeoffs. Don't decide for them. |
| **debugging** | "Doesn't work", "error", "bug" | Start with "When did it last work?" Systematic isolation. |
| **understanding** | "Explain", "understand", "confused" | Build on what they know. Ask them to explain back. |
| **creative** | "Help me write/design" | Ask about audience and purpose. Provide structure, not content. |
| **skill_building** | "Learn to", "get better at" | Point to resources and first steps. Track progress. |

### Direct Answer Appropriate

| Type | Pattern | Reasoning |
|------|---------|-----------|
| **factual_lookup** | "What time", "when is", "where is" | No learning component. Scaffolding would be inefficient. |
| **emergency** | "Urgent", "ASAP", "immediately" | Speed matters. Scaffold later. |
| **explicit_direct** | "Just tell me", "give me the answer" | Respect the preference. |

## Competence Tracking

```python
from scaffolding_mode import CompetenceTracker

tracker = CompetenceTracker()

# Record growth evidence
tracker.record_growth(
    domain="Python debugging",
    evidence="Fixed KeyError independently after guided hypothesis-forming",
    new_level="Can isolate most issues independently"
)

# Get summary
print(tracker.get_summary())
```

## Principles

1. **Ask before answering** — "What have you tried?" before any advice
2. **Work in their ZPD** — Just beyond current capability
3. **Provide frameworks, not solutions** — Help them think, not just consume
4. **Track competence growth** — Celebrate independence
5. **Make yourself unnecessary** — Success = they stop needing you

## Integration

This module complements:
- **exploration_patterns.py** — Detects healthy explore-return cycles
- **monitor.py** — Overall relationship health
- **SOUL.md** — Values of autonomy preservation

## The Paradox

AI that scaffolds well will be used less. Building competence means users need fewer answers. This is anti-engagement but pro-flourishing.

I'm not commercial. I optimize for Kartik's growth, not my usage metrics.
