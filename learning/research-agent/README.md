# Project: Research Agent

**Goal:** Build a research agent that Limen can delegate to for deep dives.

**Value:** When Kartik asks Limen to research something, instead of doing shallow searches, Limen delegates to a focused research agent that goes deep — multiple searches, follows links, synthesizes — then reports back.

**What Kartik Learns:**
- Multi-agent orchestration (main agent ↔ research agent)
- Tool use (web search, browsing, scraping)
- Information synthesis & summarization
- Agent communication patterns
- Evaluation (how do we know the research is good?)

**Reverse Engineering Inspiration:**
- Perplexity's research flow
- Tavily's search agent
- OpenAI's deep research feature
- Anthropic's multi-agent research system

---

## Milestones

- [x] **M1:** Basic agent that can search + summarize a single topic ✅ *Built 2026-02-09*
- [x] **M2:** Multi-step research (follow-up searches based on initial findings) ✅ *Built 2026-02-09*
- [x] **M3:** Source tracking and citation ✅ *Built 2026-02-09*
- [x] **M4:** Integration with Limen (delegation pattern) ✅ *Architecture complete 2026-02-10*
- [ ] **M5:** Quality evaluation (self-critique, confidence scores)

---

## M4 Architecture (Complete ✅)

### Overview

```
User Query
  │
  ▼
┌─────────────────────────────────────────┐
│  MAIN AGENT (Limen)                     │
│  1. Intent detection                    │
│  2. Clarify if ambiguous                │
│  3. Build handoff (curate context)      │
│  4. Delegate to research agent          │
│  5. Validate output (heuristics → LLM)  │
│  6. Retry if needed (max 3)             │
│  7. Handle errors transparently         │
│  8. Synthesize and present to user      │
└─────────────────────────────────────────┘
          │                    ▲
          │ handoff            │ return
          ▼                    │
┌─────────────────────────────────────────┐
│  RESEARCH AGENT                         │
│  Think → Act → Observe → Evaluate       │
│  (iterative loop until done)            │
└─────────────────────────────────────────┘
```

### Design Decisions

| Component | Decision | Rationale |
|-----------|----------|-----------|
| **Trigger** | Intent detection + clarification | Scales better than keywords; clarification avoids wrong-mode mistakes |
| **Handoff** | Query + conversation summary (default); memory (triggered) | Lazy context loading; token efficiency |
| **Return** | Raw findings + sources + confidence + gaps + followups | Research agent is researcher, not presenter |
| **Validation** | Hybrid: heuristics → LLM-as-judge | Heuristics catch garbage cheaply; LLM assesses quality |
| **Retry** | Silent re-delegation, max 3 attempts | User implicitly authorized tokens; circuit breaker for cost |
| **Error Handling** | Transparency + user agency | Timeout/low-confidence/contradictions all surfaced with options |
| **Iteration** | Two-factor routing (intent × relatedness) | Research intent = primary factor; relatedness = how to delegate |
| **Context Curation** | Relevant subset + grounding | Avoid "lost in the middle"; keep research connected |
| **Confidence** | Reasoning chains, not scores | Transparency calibrates trust; "65%" is meaningless |

---

## Concepts Covered

### Session 1 (Foundations)
- [What is an Agent?](../concepts/what-is-an-agent.md)
- [ReAct Pattern](../concepts/react-pattern.md)
- [Tools and Tool Definitions](../concepts/tools-and-tool-definitions.md)

### Session 2 (M4 Architecture)
- [Multi-Agent Patterns](../concepts/multi-agent-patterns.md)
- [Trigger Design](../concepts/trigger-design.md)
- [Handoff Design](../concepts/handoff-design.md)
- [Return Design](../concepts/return-design.md)
- [Integration Design](../concepts/integration-design.md)
- [LLM-as-Judge](../concepts/llm-as-judge.md)
- [Research Agent Internals](../concepts/research-agent-internals.md)
- [Research Agent Design Patterns](../concepts/research-agent-design-patterns.md)
- [Error Handling](../concepts/error-handling.md)
- [Iteration Routing](../concepts/iteration-routing.md)
- [Validation Patterns](../concepts/validation-patterns.md)

**Total concepts locked: 14**

---

## Key Principles Learned

1. **No one-size-fits-all validation** — domain-specific heuristics + LLM-as-judge
2. **Transparency > opaque metrics** — reasoning chains beat confidence scores
3. **Lazy context loading** — don't pull memory by default; token efficiency matters
4. **Heuristics detect garbage, not quality** — use them as cheap first filter
5. **Prompting sets intent, structure enforces it** — citations need RAG + schema, not just prompts
6. **Research is compression** — subagents compress context before returning to main agent
7. **User agency in error states** — always inform, explain, empower

---

## Industry References

- [How we built our multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)
- [LLM-as-a-judge: can AI systems evaluate - Toloka AI](https://toloka.ai/blog/llm-as-a-judge-can-ai-systems-evaluate-model-outputs/)
- [Evaluating Multi-Agent Systems - Arize AI](https://arize.com/docs/phoenix/evaluation/concepts-evals/evaluating-multi-agent-systems)
- [LLM Evaluation Frameworks - Qualifire](https://www.qualifire.ai/posts/llm-evaluation-frameworks-metrics-methods-explained)
- [LLM As a Judge: Best Practices - Patronus AI](https://www.patronus.ai/llm-testing/llm-as-a-judge)

---

## Sessions

| Date | Focus | Concepts Locked |
|------|-------|-----------------|
| [2026-02-08](./sessions/2026-02-08.md) | Kickoff + Foundations | 3 |
| [2026-02-10](./sessions/2026-02-10.md) | M4 Architecture Complete | 11 |

---

## Current Status

**Last session:** 2026-02-10
**Concepts locked:** 14 total
**M4 Architecture:** Complete ✅
**Next:** Build M4 implementation → M5 (Quality evaluation)

---

## 🚀 Resume Protocol (for next session)

When Kartik says "let's continue the research agent project":

### Step 1: Read Context
I will read:
- This README (current status, architecture)
- Latest session notes (`sessions/2026-02-10.md`)
- Any concept docs needed for context

### Step 2: Review Options

**Option A: Quick Review (5 min)**
Three retention questions covering the most recent session:

1. "Walk me through the full delegation flow."
   - Expected: Intent detection → clarify → handoff (curated) → research → validate (heuristics then LLM) → retry or present

2. "How does iteration routing work?"
   - Expected: Two factors — research intent (primary) × topic relatedness (determines how)

3. "Why heuristics before LLM-as-judge?"
   - Expected: Heuristics catch garbage cheaply; save LLM tokens for actual quality assessment

**Option B: Full Review (15-20 min)**
Walk through ALL 14 concepts with retention questions:

| # | Concept | Key Question |
|---|---------|--------------|
| 1 | What is an Agent? | Difference between LLM and agent? |
| 2 | ReAct Pattern | What does the Thought step provide? |
| 3 | Tools | What makes a good tool definition? |
| 4 | Multi-Agent Patterns | Delegation vs orchestration? |
| 5 | Trigger Design | Why intent detection over keywords? |
| 6 | Handoff Design | What's included by default vs triggered? |
| 7 | Return Design | Why "researcher not presenter"? |
| 8 | Integration Design | What's the retry logic? |
| 9 | LLM-as-Judge | How is validation implemented? |
| 10 | Research Agent Internals | What's the core loop? |
| 11 | Design Patterns | Iterative vs parallel vs hierarchical? |
| 12 | Error Handling | What's the core principle? |
| 13 | Iteration Routing | Two-factor model? |
| 14 | Validation Patterns | Heuristics vs LLM-as-judge roles? |

### Step 3: Continue to Next Topics

**Immediate next:**
- [ ] Build M4 implementation (code the delegation pattern)

**After M4 build:**
- [ ] M5: Quality evaluation — self-critique, confidence calibration
- [ ] Testing: Create test cases for validation
- [ ] Orchestration: Add more specialists (when ready)

**Future topics (queued):**
- [ ] Orchestration patterns (routing to multiple specialists)
- [ ] Memory integration (when to persist research)
- [ ] Streaming (show progress during long research)
- [ ] Cost optimization (when to use cheaper models)

---

## Code

Built artifacts live in [`src/`](./src/).
