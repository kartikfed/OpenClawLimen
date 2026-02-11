# Concept: Error Handling in Agent Systems

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Integration Design](./integration-design.md), [Return Design](./return-design.md)*

## Core Principle

In all error/edge cases, the system must:
1. **Inform** — Tell the user what's happening
2. **Explain** — Why, if known
3. **Empower** — Give them options to act

**The opposite of black-box AI** — don't hide problems, don't pretend certainty, give users agency.

---

## Scenario 1: Timeout

Research agent takes too long (network issues, complex query, API rate limits).

### Response Pattern

| Action | Rationale |
|--------|-----------|
| Notify user proactively | Don't leave them wondering |
| Explain cause if known | "API rate limited" vs "complex query" vs "unknown" |
| Offer options | Wait longer / Cancel / Get partial results |

### Example Message

```
"This is taking longer than expected — looks like the search API is slow right now.
Do you want me to keep waiting, or should I return what I have so far?"
```

### Implementation

- **Soft timeout** (e.g., 30s): Notify user, offer choice
- **Hard timeout** (e.g., 60s): Force decision or return partial

---

## Scenario 2: Low Confidence

Research agent returns but confidence is low across all findings.

### Response Pattern

| Action | Rationale |
|--------|-----------|
| Return findings anyway | Something is better than nothing |
| Explicitly flag low confidence | User calibrates trust accordingly |
| Include actionable follow-up | What would improve confidence? |

### Example Message

```
"I found some information, but my confidence is low — sources were sparse
and mostly from 2022. To get better results, I'd need:
- Access to paywalled sources (WSJ, FT)
- A more specific time frame
- Or you could clarify what aspect matters most"
```

### Key Insight

The follow-up should say **what the agent would need** to do better. This turns a failure into a collaborative next step.

---

## Scenario 3: Contradictory Sources

Sources disagree — different experts/data say different things.

### Response Pattern

| Action | Rationale |
|--------|-----------|
| Acknowledge contradiction explicitly | Intellectual honesty |
| Summarize both sides | User sees full picture |
| Take a stance with reasoning (if appropriate) | Add value, don't just punt |
| Offer to dig deeper | User may want to resolve it |

### Example Message

```
"Sources disagree on this:
- Peterson Institute argues tariffs cost more jobs than they save (13:1 ratio)
- American Steel Association claims 15,000 jobs directly saved

My read: The economist consensus leans toward net negative, but industry
groups dispute the methodology. If this matters for your decision, I can
dig deeper into the methodology debate."
```

### Key Insight

The agent **can have an opinion** — but it must:
- Show its reasoning
- Acknowledge disagreement
- Let user decide if they want to go deeper

---

## The Meta-Principle

Agents fail gracefully when they:
1. Don't hide problems
2. Don't pretend certainty they don't have
3. Give users agency to decide next steps

This distinguishes good agent design from black-box AI that just says "I don't know" or silently returns bad results.

---

## Implementation Notes

### Timeout Thresholds

```python
SOFT_TIMEOUT = 30  # seconds - notify user
HARD_TIMEOUT = 60  # seconds - force decision
```

### Confidence Thresholds

```python
HIGH_CONFIDENCE = 0.8+    # Present normally
MEDIUM_CONFIDENCE = 0.5-0.8  # Present with caveat
LOW_CONFIDENCE = <0.5     # Present with explicit warning + improvement suggestions
```

### Contradiction Detection

In validation step, check for:
- Directly opposing claims from different sources
- Statistical disagreements (different numbers for same metric)
- Methodological disputes

Flag in return: `contradictions: [{ claim1, claim2, sources }]`

---

## Industry Validation

These patterns align with production systems:

- **Anthropic's Multi-Agent Research System** uses similar error handling with context preservation and iterative refinement
- **Hybrid validation** (heuristics + LLM-as-judge) is industry standard per Toloka AI and Arize documentation

### References

- [How we built our multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
- [LLM-as-a-judge: can AI systems evaluate - Toloka AI](https://toloka.ai/blog/llm-as-a-judge-can-ai-systems-evaluate-model-outputs/)
- [Evaluating Multi-Agent Systems - Arize AI](https://arize.com/docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems)

---

*Concept locked: 2026-02-10*
