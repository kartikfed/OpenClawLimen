# SOS/RC Support Context Detector

Operationalizes the **Feeney & Collins (2014) "Thriving Through Relationships"** model to detect whether someone is in an adversity or growth context, and whether the support being provided is appropriate.

## Key Insight

**The right challenge/support balance isn't a fixed ratio — it's contextual responsiveness.**

Challenge IS support when appropriately timed. The skill is reading context and providing what's needed.

## Two Support Functions for Thriving

### 1. Source of Strength (SOS) Support — For Adversity Contexts

When someone is facing difficulty, stress, loss, or crisis:

- **Safe Haven (Comfort)**: "I'm here for you," "That sounds really hard"
- **Fortification**: "You've handled difficult situations before," "You have the strength"
- **Reconstruction**: "Let's take this step by step," "Focus on one thing at a time"
- **Reframing**: "This could become a growth opportunity," "What can you learn from this?"

### 2. Relational Catalyst (RC) Support — For Growth Contexts

When someone is exploring opportunities, pursuing goals, or seeking growth:

- **Nurture**: "Go for it!", "That sounds exciting", "I encourage you to explore"
- **Perceptual Assistance**: "Think about the possibilities," "This could lead to..."
- **Preparation**: "Let's plan your approach," "What skills do you need?"
- **Launching**: "You're ready," "Take the leap," "You've got this!"

## Usage

### Analyze Specific Text

```bash
# Analyze user text for context
python3 support_context.py --text "I'm so stressed about the deadline"

# Analyze conversation (user + AI response)
python3 support_context.py --text "I'm stressed about work" --response "Go push yourself harder"

# Verbose output with signal breakdown
python3 support_context.py --text "I just got fired" -v
```

### Analyze Recent Memory Files

```bash
# Analyze last 7 days
python3 support_context.py

# Analyze last 30 days, verbose
python3 support_context.py --days 30 -v

# JSON output for integration
python3 support_context.py --json
```

## Example Output

```
SUPPORT CONTEXT ANALYSIS
==================================================

Context: 🔴 ADVERSITY
Confidence: 75%

Scores:
  Adversity: 8.5
  Growth:    1.0

Support Match: ✗ Challenging during adversity — consider SOS support first

--------------------------------------------------
RECOMMENDATION:
ADVERSITY CONTEXT — Provide SOS support:
  • Start with comfort/safe haven (validate, empathize)
  • Address emotional needs first before problem-solving
  • Then fortify (remind of strengths, past resilience)
  • Gradually introduce reframing (adversity → growth)
  • Challenge/RC support comes AFTER stability is restored

⚠️ CURRENT SUPPORT MAY BE MISMATCHED — see analysis above
```

## Context Types

| Context | Emoji | Description | Appropriate Support |
|---------|-------|-------------|---------------------|
| ADVERSITY | 🔴 | Distress, loss, crisis | SOS first, then gradual RC |
| GROWTH | 🟢 | Opportunity, exploration | RC (challenge is appropriate) |
| TRANSITION | 🟡 | Moving from adversity to growth | Balance of both |
| UNCLEAR | ⚪ | Not enough signals | Ask questions, default to SOS |

## Pattern Categories

### Adversity Signals

- **Emotional**: stress, anxiety, depression, frustration, fear, loneliness
- **Situational**: job loss, rejection, financial problems, emergencies
- **Relational**: breakup, conflicts, betrayal, loss of loved ones
- **Health**: illness, diagnosis, surgery, chronic conditions

### Growth Signals

- **Exploration**: curiosity, wanting to try new things, considering options
- **Achievement**: excitement, progress, accomplishment, confidence
- **Development**: learning, building, improving skills
- **Opportunity**: new roles, interviews, promotions, possibilities

## Integration with Relationship Monitor

This detector extends the relationship-monitor framework:

```
skills/relationship-monitor/
├── monitor.py                 # Authority/attachment/reliance signals
├── exploration_patterns.py    # Secure base / exploration patterns
├── scaffolding_mode.py        # Scaffold vs direct answer detection
├── consistency_checker.py     # Value consistency monitoring
├── cognitive_sovereignty.py   # Epistemic independence erosion
└── support_context.py         # SOS/RC support context (NEW)
```

## Research Reference

Based on:
- Feeney, B. C., & Collins, N. L. (2014). "A new look at social support: A theoretical perspective on thriving through relationships." *Personality and Social Psychology Review*, 19(2), 113-147.
- https://pmc.ncbi.nlm.nih.gov/articles/PMC5480897/

Key quotes from the research:

> "Support providers should encourage a close other to challenge or extend himself/herself to grow as an individual."

> "Two support functions exist: (1) Source of Strength for adversity contexts, and (2) Relational Catalyst for non-adverse growth contexts."

## Why This Matters

Current AI assistants often default to a single support mode — either always comforting or always challenging. The Feeney & Collins model shows that **optimal support is context-dependent**:

- **Too much challenge during adversity** → Feels dismissive, increases stress
- **Too much comfort during growth** → Enables complacency, misses opportunity

The detector helps calibrate responses to what's actually needed in the moment.
