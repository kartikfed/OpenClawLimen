# Concept: Multi-Agent Patterns

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [What is an Agent?](./what-is-an-agent.md), [ReAct Pattern](./react-pattern.md), [Tools](./tools-and-tool-definitions.md)*

## Why Multiple Agents?

Single agents hit limits:
- Context window constraints
- Specialization vs generalization tradeoff
- Complex tasks need decomposition

Multi-agent systems split work across specialized agents.

## Core Patterns

### 1. Delegation (Boss → Worker)

One agent assigns a task to another, waits for results, continues.

```
Main Agent: "I need deep research on X"
  → spawns Research Agent
  → Research Agent does 5-10 searches, synthesizes
  → returns report to Main Agent
  → Main Agent summarizes for user
```

**Characteristics:**
- Single sub-agent for a specific task type
- "Fire and forget" — spawn it, wait, done
- No routing decision needed (only one option)
- Simpler to build, debug, evaluate

**When to use:** You have ONE specialist and know when to call it.

### 2. Orchestration (Coordinator + Specialists)

A coordinator analyzes tasks and routes to appropriate specialists.

```
Coordinator receives query
  → Analyzes: "This needs search AND code"
  → Routes to Search Agent + Code Agent
  → Waits for both
  → Synthesizes combined results
```

**Characteristics:**
- Multiple specialist agents available
- Active ROUTING decision based on task analysis
- Can parallelize independent subtasks
- More complex — requires routing logic

**When to use:** Multiple specialists, mixed queries, complex task decomposition.

### 3. Debate/Critique (Agent A ↔ Agent B)

Agents review and improve each other's work.

```
Research Agent: "Here's my synthesis"
Critic Agent: "Source 2 contradicts source 4"
Research Agent: "Good catch, revised..."
```

**Characteristics:**
- Iterative refinement
- Quality improvement through adversarial review
- Useful for evaluation and self-correction

**When to use:** High-stakes outputs, quality assurance, reducing hallucination.

## Key Distinction: Delegation vs Orchestration

| Aspect | Delegation | Orchestration |
|--------|------------|---------------|
| Sub-agents | One | Multiple |
| Routing decision | None (implicit) | Active analysis |
| Complexity | Lower | Higher |
| Flexibility | Single task type | Mixed queries |

**Kartik's insight:** "They're basically the same — spawning specialists and synthesizing results."

**Nuance:** Orchestration adds a routing layer. Delegation assumes you already know who to call.

## Starting Point: Delegation

For M4 (integrating research agent with Limen):
- One specialist exists (research agent)
- No routing decision needed
- Simpler to build and debug
- Can evolve into orchestration when more specialists are added

## Questions for Later (Orchestration Deep Dive)

- How does the coordinator decide which specialists to invoke?
- How do you handle dependencies between specialists?
- Parallel vs sequential execution?
- Error handling when one specialist fails?

---

*Concept locked: 2026-02-10*
