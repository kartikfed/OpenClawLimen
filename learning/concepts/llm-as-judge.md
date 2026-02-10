# Concept: LLM-as-Judge (Validation via Prompt)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Integration Design](./integration-design.md), [Return Design](./return-design.md)*

## What It Is

Using an LLM call to evaluate another LLM's output. The main agent prompts the model with an evaluation task to decide how to proceed.

## The Pattern

```
Main Agent receives research output
  → Constructs VALIDATION PROMPT
  → Calls LLM with evaluation task
  → Receives structured assessment
  → Decides: present / re-delegate / ask user
```

## Example Validation Prompt

```
You are evaluating research output for quality and completeness.

ORIGINAL USER QUERY:
{query}

CONSTRAINTS SPECIFIED:
{constraints}

RESEARCH OUTPUT:
{findings}

CONFIDENCE REPORTED: {confidence_score}

Evaluate:
1. COVERAGE: Does output address all aspects of the query? (yes/partial/no)
2. RELEVANCE: Is it about the right topic? (yes/partial/no)
3. CONSTRAINT_COMPLIANCE: Were specified constraints followed? (yes/partial/no)
4. CONFIDENCE_ACCEPTABLE: Is the confidence score acceptable? (yes/no)

Return JSON:
{
  "coverage": "...",
  "relevance": "...",
  "constraint_compliance": "...",
  "confidence_acceptable": "...",
  "verdict": "PASS | NEEDS_REFINEMENT | INSUFFICIENT",
  "reasoning": "...",
  "refinement_hint": "..." // only if needs refinement
}
```

## Example Output

```json
{
  "coverage": "partial",
  "relevance": "yes",
  "constraint_compliance": "no",
  "confidence_acceptable": "yes",
  "verdict": "NEEDS_REFINEMENT",
  "reasoning": "Output covers economic impact but misses political implications. Used 2023 sources when user specified 2024.",
  "refinement_hint": "Focus on political implications and restrict sources to 2024."
}
```

## Decision Logic

```
if verdict == "PASS":
    synthesize_and_present()
elif verdict == "NEEDS_REFINEMENT" and retry_count < max_retries:
    re_delegate(refinement_hint)
else:
    present_best_effort_and_ask_user()
```

## Validation Criteria

| Signal | Question | Source |
|--------|----------|--------|
| **Coverage** | All aspects addressed? | Compare output to query |
| **Relevance** | Actually about the topic? | Semantic match |
| **Constraint compliance** | User requirements followed? | Compare to handoff |
| **Confidence** | Agent confident in findings? | Confidence metadata |
| **Completeness** | Obvious gaps? | Gaps field in return |
| **Coherence** | Findings consistent? | Internal consistency |

## Why LLM-as-Judge?

**Pros:**
- Flexible, handles nuance
- Can evaluate subjective quality
- No need to enumerate every failure mode

**Cons:**
- Adds latency + cost (another LLM call)
- Can have its own biases
- Not deterministic

## Alternative Validation Approaches

| Approach | Pros | Cons |
|----------|------|------|
| **LLM-as-Judge** | Flexible, nuanced | Cost, latency |
| **Heuristics** | Fast, cheap, deterministic | Brittle, misses nuance |
| **Embedding similarity** | Catches relevance issues | Misses coverage/constraints |
| **Hybrid** | Best of both | More complex |

## Production Pattern: Hybrid

```
First pass: Cheap heuristics
  - Length check
  - Keyword presence
  - Source count

Second pass: LLM-as-judge (only if heuristics pass but borderline)
```

Saves cost by not running LLM validation on obviously good/bad outputs.

## Key Insight

The validation step is another LLM call, but it's cheap (short prompt, structured output) compared to the research itself. You're trading small token cost for quality assurance.

---

*Concept locked: 2026-02-10*
