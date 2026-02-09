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

- [ ] **M1:** Basic agent that can search + summarize a single topic
- [ ] **M2:** Multi-step research (follow-up searches based on initial findings)
- [ ] **M3:** Source tracking and citation
- [ ] **M4:** Integration with Limen (delegation pattern)
- [ ] **M5:** Quality evaluation (self-critique, confidence scores)

---

## Key Questions to Explore

*Questions that emerge during building — both Kartik's and Limen's*

### Kartik's Questions
- (None yet — project just started)

### Limen's Questions for Kartik
- (None yet)

### Answered
- (None yet)

---

## Concepts Touched

Links to concept notes as they emerge:

- (Will populate as we build)

---

## Sessions

| Date | Focus | Key Learnings |
|------|-------|---------------|
| [2026-02-08](./sessions/2026-02-08.md) | Kickoff + Foundations | Agent definition, ReAct pattern, Tools |

---

## Current Status

**Last session:** 2026-02-08
**Concepts locked:** 3 (Agent basics, ReAct, Tools)
**Next:** Multi-agent patterns → Architecture design → Build M1

---

## 🚀 Resume Protocol (for next session)

When Kartik says "let's continue the research agent project":

### Step 1: Quick Review (5 min)
Confirm retention of locked concepts with quick questions:

1. "What's the key difference between a basic LLM and an agent?"
   - Expected: Loop (observe-act), goal-directed, tools, autonomy

2. "What does ReAct stand for and why does the Thought step matter?"
   - Expected: Reasoning + Acting; metacognition, debuggability, context continuity

3. "What makes a good tool definition?"
   - Expected: Not just WHAT but WHEN; description is a contract; semantics matter

### Step 2: Continue Where We Left Off
- Next concept: Multi-agent patterns (delegation, orchestration)
- Then: Design research agent architecture together
- Then: Build M1 (basic search + summarize)

---

## Code

Built artifacts live in [`src/`](./src/).
