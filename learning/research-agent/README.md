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

---

## Milestones

- [x] **M1:** Basic agent that can search + summarize a single topic ✅ *Built 2026-02-09*
- [x] **M2:** Multi-step research (follow-up searches based on initial findings) ✅ *Built 2026-02-09*
- [x] **M3:** Source tracking and citation ✅ *Built 2026-02-09*
- [ ] **M4:** Integration with Limen (delegation pattern) — *Architecture designed 2026-02-10*
- [ ] **M5:** Quality evaluation (self-critique, confidence scores)

---

## M4 Architecture (Designed 2026-02-10)

### Overview

```
User Query
  │
  ▼
┌─────────────────────────────────────────┐
│  MAIN AGENT (Limen)                     │
│  1. Intent detection                    │
│  2. Clarify if ambiguous                │
│  3. Build handoff                       │
│  4. Delegate to research agent          │
│  5. Validate output (LLM-as-judge)      │
│  6. Retry if needed (max 3)             │
│  7. Synthesize and present to user      │
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
| **Handoff** | Query + conversation summary (default) | Lazy context loading; memory only when triggered |
| **Return** | Raw findings + sources + confidence + gaps + followups | Research agent is researcher, not presenter |
| **Validation** | LLM-as-judge | Flexible, handles nuance; cheap relative to research |
| **Retry** | Silent re-delegation, max 3 attempts | User implicitly authorized tokens; circuit breaker for cost |
| **Memory** | User-triggered persistence | Not all research worth keeping; user decides |

---

## Key Questions to Explore

*Questions that emerge during building — both Kartik's and Limen's*

### Kartik's Questions
- "Aren't delegation and orchestration basically the same?" — Answered: Orchestration adds routing layer
- "How does validation work in implementation?" — Answered: LLM-as-judge pattern
- "Is there a standard way to design research agents?" — Answered: No, it's a tradeoff space

### Limen's Questions for Kartik
- (None currently)

### Open Questions (For Future Sessions)
- Error handling: What if research agent times out?
- Error handling: What if all sources have low confidence?
- Error handling: What if sources contradict each other?
- Iteration: "Dig deeper on point 3" — fresh delegation or build on previous?

---

## Concepts Touched

Links to concept notes:

**Session 1 (Foundations):**
- [What is an Agent?](../concepts/what-is-an-agent.md)
- [ReAct Pattern](../concepts/react-pattern.md)
- [Tools and Tool Definitions](../concepts/tools-and-tool-definitions.md)

**Session 2 (M4 Architecture):**
- [Multi-Agent Patterns](../concepts/multi-agent-patterns.md)
- [Trigger Design](../concepts/trigger-design.md)
- [Handoff Design](../concepts/handoff-design.md)
- [Return Design](../concepts/return-design.md)
- [Integration Design](../concepts/integration-design.md)
- [LLM-as-Judge](../concepts/llm-as-judge.md)
- [Research Agent Internals](../concepts/research-agent-internals.md)
- [Research Agent Design Patterns](../concepts/research-agent-design-patterns.md)

---

## Sessions

| Date | Focus | Concepts Locked |
|------|-------|-----------------|
| [2026-02-08](./sessions/2026-02-08.md) | Kickoff + Foundations | 3 (Agent, ReAct, Tools) |
| [2026-02-10](./sessions/2026-02-10.md) | M4 Architecture Design | 8 (Multi-agent, Trigger, Handoff, Return, Integration, LLM-as-judge, Internals, Patterns) |

---

## Current Status

**Last session:** 2026-02-10
**Concepts locked:** 11 total
**M4 Architecture:** Designed ✅
**Next:** Complete error handling / iteration design → Build M4

---

## 🚀 Resume Protocol (for next session)

When Kartik says "let's continue the research agent project":

### Step 1: Quick Review (5 min)
Confirm retention of key M4 concepts:

1. "Walk me through the delegation flow from user query to final output."
   - Expected: Intent detection → clarify if needed → handoff → research → validate → retry or present

2. "What's the difference between what the research agent returns vs what the user sees?"
   - Expected: Research returns raw + metadata; main agent synthesizes for user

3. "When would validation trigger a re-delegation?"
   - Expected: Coverage issues, constraint non-compliance, low confidence

### Step 2: Continue Where We Left Off
- Remaining M4 design: Error handling (C) and Iteration (D)
- Then: Build M4 implementation
- Then: M5 (Quality evaluation)

---

## Code

Built artifacts live in [`src/`](./src/).
