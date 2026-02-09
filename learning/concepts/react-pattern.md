# Concept: ReAct Pattern

*Emerged from: Research Agent project, Session 1*
*Date: 2026-02-08*
*Connected to: [What is an Agent?](./what-is-an-agent.md)*

## What It Stands For

**ReAct = Reasoning + Acting**

A framework from 2022 that formalized the agent loop.

## The Pattern

```
Thought:     I need to find available grooming times
Action:      browser_navigate("nowyoureclean.com/booking")
Observation: [page shows calendar with available slots]
Thought:     I see slots on Saturday. I should check if 2:30pm works.
Action:      browser_click("2:30pm slot")
Observation: [slot selected, proceed button appeared]
...
```

Three components repeating:
1. **Thought** — Reasoning about what to do next
2. **Action** — Actually doing it (using a tool)
3. **Observation** — Seeing the result

## Why the "Thought" Step Matters

### Kartik's framing:
> "Reasoning allows the model to know what it knows and know what it doesn't know (and then ask the right questions or use the right tools)."

This is **metacognition** — self-awareness about one's own knowledge state.

### Additional reasons:
- **Planning** — Formulate approach before jumping in
- **Interpretability** — When things fail, you can see *why* (debug the reasoning)
- **Context continuity** — Holds learned information across steps (working memory)

## Without Reasoning

Agent would just: Act → Observe → Act → Observe

Problems:
- No plan, just reactive
- Doesn't know when to stop and ask for clarification
- Can't assess what information is missing
- Harder to debug when it fails

## Kartik's Summary (Session 1)

> "ReAct loop is the formalization of the concept that training models to reason over the given task before performing actions yields higher quality results. This allows the model to reflect on its own state and understanding of the task before acting."

> "Without reasoning, actions would be pure responses to direct observation — no broader context to assess validity."

## Connection to Chain-of-Thought

Chain-of-thought prompting ("think step by step") is a lightweight version of the same principle. Forcing reasoning grounds subsequent outputs.

## Key Insight

Reasoning isn't overhead — it's what makes agents reliable and debuggable.
