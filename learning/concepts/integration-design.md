# Concept: Integration Design (Using the Result)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Return Design](./return-design.md), [LLM-as-Judge](./llm-as-judge.md)*

## The Question

When the research agent returns its output, how does the main agent use it?

## Components

### A. Output Validation

Before presenting to user, main agent validates:
- Does output address the query?
- Were constraints followed?
- Is confidence acceptable?

See: [LLM-as-Judge](./llm-as-judge.md) for implementation details.

### B. Retry Logic

```
Research Agent returns
  → Main Agent validates
  → If PASS: synthesize and present
  → If NEEDS_REFINEMENT: re-delegate with refinement hint
  → If still insufficient after N retries: ask user for help
```

**Why silent re-delegation is acceptable:**
User asked for research. They implicitly authorized tokens needed to fulfill that request. Re-delegation isn't scope creep — it's completing the job.

**Circuit breaker (prevent infinite retries):**

| Retry Count | Action |
|-------------|--------|
| 1st attempt | Present if good, else re-delegate |
| 2nd attempt | Present if good, else re-delegate with refined query |
| 3rd attempt | Present best effort + ask user for clarification |

### C. Memory Persistence

**Principle:** Storage location = user's choice when options exist.

| Action | When |
|--------|------|
| Stay in conversation context | Default — available for session |
| Write to memory files | User explicitly asks ("remember this") |

**Why not auto-persist?**
1. Not all research is worth keeping
2. Memory files would bloat with one-off queries
3. User knows what's worth remembering

### D. Presentation

Main agent synthesizes raw findings into user-facing output:
- Distill into coherent summary (default)
- Format per user preference if specified
- Add follow-up questions to prevent dead ends
- Keep metadata (sources, confidence) available on request

---

*Concept locked: 2026-02-10*
