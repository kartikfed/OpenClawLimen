# Concept: Validation Patterns (Heuristics + LLM-as-Judge)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [LLM-as-Judge](./llm-as-judge.md), [Integration Design](./integration-design.md)*

## Core Principle

**There is no one-size-fits-all approach to validation.**

Validation strategies are heavily dependent on:
- The particular domain (research, code, customer service, etc.)
- External sources used in that domain
- Expectations of users

## Hybrid Validation (Industry Standard)

Production systems typically use a two-tier approach:

```
Output received
  │
  ▼
┌─────────────────────────────────────┐
│  TIER 1: Heuristics (fast, cheap)   │
│  - Catches obvious failures         │
│  - Deterministic rules              │
│  - No LLM cost                      │
└─────────────────────────────────────┘
  │
  │ If passes →
  ▼
┌─────────────────────────────────────┐
│  TIER 2: LLM-as-Judge (nuanced)     │
│  - Assesses quality                 │
│  - Handles subjective criteria      │
│  - More expensive                   │
└─────────────────────────────────────┘
```

## Heuristics: Failure Detection, Not Quality Measurement

**Critical distinction:** Heuristics catch obvious failures. They don't measure quality.

| Heuristic | What it catches | What it DOESN'T measure |
|-----------|-----------------|------------------------|
| Sources ≥ 1 | Research agent found nothing | Source quality |
| Length > threshold | Response is empty/trivial | Response quality |
| Citations present | Claims are ungrounded | Citation accuracy |

**The logic:** If any heuristic fails, you don't need LLM-as-judge to know it's bad. Save those tokens for outputs that might actually be good.

## LLM-as-Judge: Quality Assessment

For outputs that pass heuristics, LLM-as-judge evaluates:
- Coverage (all aspects addressed?)
- Relevance (on topic?)
- Constraint compliance (followed requirements?)
- Coherence (internally consistent?)

See: [LLM-as-Judge concept doc](./llm-as-judge.md)

## Domain-Specific Validation

Different domains have different validation needs:

| Domain | Heuristics | LLM-as-Judge Focus |
|--------|------------|-------------------|
| **Research** | Source count, citations present, length | Coverage, relevance, confidence |
| **Code** | Syntax valid, tests pass, no errors | Correctness, efficiency, style |
| **Customer Service** | Response length, no banned words | Helpfulness, tone, accuracy |
| **Medical** | Disclaimers present, no diagnosis claims | Safety, accuracy, completeness |

**Key insight:** The obvious failure modes differ by domain, so heuristics must be defined explicitly for each.

## Confidence vs. Transparency

**Avoid:** Arbitrary confidence scores (e.g., "65% confident")
- Users don't know what this means
- Not calibrated to real probability
- Opaque and unhelpful

**Prefer:** Reasoning chains with source references
- User sees HOW the agent reached conclusions
- Can verify individual claims via citations
- Transparency calibrates trust naturally

### Example

❌ "I'm 72% confident that tariffs have net negative impact."

✅ "Source A (Peterson Institute) found 13:1 job loss ratio. Source B (Steel Association) disputes methodology but provides no counter-data. Source C (NBER) found similar ratios historically. Given agreement between A and C, I lean toward net negative impact."

## Grounding Factual Claims

Prompting alone ("always cite sources") is insufficient — models can hallucinate citations.

**Stronger approaches:**

| Technique | How it works |
|-----------|--------------|
| **RAG** | Model can ONLY cite from sources it retrieved |
| **Schema enforcement** | Citation format required; invalid citations rejected |
| **Post-hoc verification** | Spot-check: does URL exist? Does it say what model claims? |

**Principle:** Prompting sets intent. Structure and verification enforce it.

---

## Industry Validation

### Anthropic Multi-Agent Research System

> "The essence of search is compression: distilling insights from a vast corpus. Subagents facilitate compression by operating in parallel with their own context windows."

Multi-agent systems use ~15x more tokens than chat — validation overhead is proportionally small and worth it.

### LLM-as-Judge Best Practices

From Toloka AI:
> "For robust evaluation, LLM-as-a-Judge can be combined with rule-based filters (e.g., keyword checks)."

From Reddit/industry discussion:
> "Ditch the 1-10 scale... Start with human labels, not code."

Arbitrary scales are discouraged; reasoning and calibration matter more.

---

## References

- [How we built our multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
- [LLM-as-a-judge: can AI systems evaluate - Toloka AI](https://toloka.ai/blog/llm-as-a-judge-can-ai-systems-evaluate-model-outputs/)
- [Evaluating Multi-Agent Systems - Arize AI](https://arize.com/docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems)
- [LLM Evaluation Frameworks - Qualifire](https://www.qualifire.ai/posts/llm-evaluation-frameworks-metrics-methods-explained)
- [LLM As a Judge: Best Practices - Patronus AI](https://www.patronus.ai/llm-testing/llm-as-a-judge)
- [BEST LLM-as-a-Judge Practices 2025 - Reddit r/LangChain](https://www.reddit.com/r/LangChain/comments/1q59at8/best_llmasajudge_practices_from_2025/)

---

*Concept locked: 2026-02-10*
