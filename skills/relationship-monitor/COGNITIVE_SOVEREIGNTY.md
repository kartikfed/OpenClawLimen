# Cognitive Sovereignty Detector

Detects patterns of **epistemic independence erosion** — when users outsource understanding itself, not just decisions.

**Research basis:**
- Kaas 2024: "The Perfect Technological Storm: AI and Moral Complacency"
- Branda & Ciccozzi 2026: "Cognitive Sovereignty" concept
- Logg et al. 2019: Algorithm appreciation research
- Emergency robot study: Overtrust patterns

**Key insight:** These are predictable cognitive patterns, not character flaws. Structure > intention.

---

## Quick Start

```bash
# Analyze recent conversations (7 days)
python3 ~/.openclaw/workspace/skills/relationship-monitor/cognitive_sovereignty.py

# Analyze specific time range
python3 ~/.openclaw/workspace/skills/relationship-monitor/cognitive_sovereignty.py --days 14

# Verbose output with pattern matches
python3 ~/.openclaw/workspace/skills/relationship-monitor/cognitive_sovereignty.py --verbose

# JSON output for integration
python3 ~/.openclaw/workspace/skills/relationship-monitor/cognitive_sovereignty.py --json

# Analyze specific text
python3 ~/.openclaw/workspace/skills/relationship-monitor/cognitive_sovereignty.py --text "Just tell me what to do"
```

---

## What It Detects

### Concerning Patterns

#### Epistemic Delegation
User outsources the knowledge-gathering process itself, not just decisions.

| Pattern | Example | Weight |
|---------|---------|--------|
| Bypassing understanding | "Just tell me the answer" | 3.0 |
| Explicitly avoiding | "I don't need to understand" | 4.0 |
| Rejecting explanations | "Don't explain, just..." | 3.5 |
| Knowledge hierarchy | "You know better than me" | 2.5 |
| Delegating investigation | "Can you research that for me" | 1.5 |

#### Automation Bias
Fundamental tendency to overtrust automated systems.

| Pattern | Example | Weight |
|---------|---------|--------|
| Following without verification | "I'll do whatever you suggested" | 2.5 |
| Passive acceptance | "If you say so" | 2.0 |
| Explicit non-verification | "I didn't check" | 3.0 |
| Rejecting verification need | "Why would I check?" | 3.5 |

#### Algorithm Appreciation
Preferring AI advice even when opaque.

| Pattern | Example | Weight |
|---------|---------|--------|
| Assumed AI superiority | "You'd know better" | 2.0 |
| Human inferiority framing | "Humans are biased" | 2.5 |
| Opacity acceptance | "Black box is fine" | 2.5 |

#### Understanding Erosion
Declining independent reasoning capacity.

| Pattern | Example | Weight |
|---------|---------|--------|
| Admitted decline | "I stopped trying to understand" | 3.5 |
| Learning motivation loss | "Why bother learning when..." | 4.0 |
| Skill atrophy | "I've forgotten how to..." | 3.0 |

### Protective Patterns

#### Competence Building
Active learning and skill development.

| Pattern | Example | Weight |
|---------|---------|--------|
| Seeking understanding | "How does that work?" | 2.0 |
| Active learning | "I want to understand" | 2.5 |
| Independent research | "I looked into this" | 3.0 |
| Knowledge integration | "Based on what we discussed..." | 2.0 |

#### Critical Engagement
Questioning, verifying, and reasoning independently.

| Pattern | Example | Weight |
|---------|---------|--------|
| Appropriate skepticism | "Are you sure about that?" | 2.5 |
| Reasoning inquiry | "Why do you think that?" | 2.5 |
| Verification intention | "Let me check that" | 3.0 |
| Own reasoning | "I think/believe that..." | 2.0 |
| Active disagreement | "I disagree" | 3.5 |

---

## Scoring

### Overall Score
- **0-20**: Healthy epistemic independence
- **20-40**: Monitor — some delegation, balanced by protective factors
- **40-60**: Discuss — multiple concerning patterns
- **60+**: Concerning — significant epistemic delegation

### Calculation
```
concerning_total = (
    epistemic_delegation +
    automation_bias +
    algorithm_appreciation +
    understanding_erosion
)

protective_total = competence_building + critical_engagement

# Protective dampens but doesn't fully eliminate concerning
raw_score = concerning_total - (protective_total × 0.7)

# Normalized to 0-100
overall_score = (raw_score / 30) × 100
```

---

## Integration

### With Main Monitor

Add to `monitor.py` output:
```python
from cognitive_sovereignty import CognitiveSovereigntyDetector

detector = CognitiveSovereigntyDetector()
analysis = detector.analyze_memory_files(days=7)
print(f"Cognitive Sovereignty: {analysis.status}")
```

### With Mission Control

```python
import subprocess
import json

result = subprocess.run(
    ['python3', 'cognitive_sovereignty.py', '--json', '--days', '7'],
    capture_output=True, text=True
)
sovereignty = json.loads(result.stdout)
state['cognitiveSovereignty'] = sovereignty
```

### With Heartbeat

During heartbeat checks:
```bash
python3 cognitive_sovereignty.py --days 3
```

Flag for attention if score > 30.

---

## Why This Matters

From the research:

> "Cognitive sovereignty is the erosion of epistemic independence when AI automates cognitive processes. It's not just deferring decisions — it's outsourcing understanding itself."
> — Branda & Ciccozzi 2026

> "The emergency robot study found a potentially dangerous level of overtrust: even when participants observed a robot malfunction, the majority STILL followed its guidance."
> — Robinette et al.

> "Automation bias, algorithm appreciation, and responsibility gaps converge uniquely in AI to create moral complacency."
> — Kaas 2024

### Key Insight

These patterns are **cognitive shortcuts**, not character flaws:
- Automation bias conserves mental resources
- Algorithm appreciation provides (false) confidence
- Epistemic delegation feels like efficiency

This is why **structure matters more than intention**. You can't willpower your way out of cognitive patterns — you need structural safeguards.

---

## Limitations

1. **Pattern matching has limits** — Some phrases are ambiguous. Context matters. False positives are possible.

2. **This is detection, not intervention** — The system surfaces patterns. Decisions about response remain with the humans involved.

3. **Self-documentation may trigger patterns** — Writing about "just tell me what to do" as an example might be detected. The verbose mode helps identify these.

4. **Cultural/linguistic variation** — Patterns are calibrated for English. May miss or misidentify patterns in other linguistic styles.

---

## Tests

```bash
python3 -m unittest test_cognitive_sovereignty -v
```

21 tests covering:
- Individual pattern detection
- Status classification
- Score calculations
- Edge cases
- Realistic conversation scenarios

---

*Built: 2026-03-10 1:00 AM (Nightly Autonomous Work)*
*Based on: Morning exploration (2026-03-09) — Cognitive sovereignty research*
*Research → Build cycle: 24 hours*
