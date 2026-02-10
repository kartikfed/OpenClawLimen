# Concept: Handoff Design (What Gets Delegated)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Multi-Agent Patterns](./multi-agent-patterns.md), [Trigger Design](./trigger-design.md)*

## The Question

When a main agent delegates to a sub-agent, what information should be passed in the handoff?

## The Tradeoff

| More context | Less context |
|--------------|--------------|
| Sub-agent is better targeted | Sub-agent has more freedom to explore |
| Less redundant work | Might cover ground already known |
| Risk: over-constraining | Risk: unfocused, wasteful |

## The Principle

**Sensible defaults with user-overridable scoping.**

Default to enough context for the sub-agent to be effective, but let user input expand or constrain scope.

## Handoff Components

### Always Included (Default)
1. **Query** — what to research
2. **Recent conversation summary** — what the main agent already knows from current session

### Triggered by User Signal
3. **Memory files** — historical context from past sessions
   - Only when user indicates: "we talked about this before"
   - Avoids wasting tokens on potentially irrelevant history

### User-Specified (Passed Through)
4. **Focus areas** — "specifically look at X, not Y"
5. **Constraints** — "just 3 sources" / "last 6 months only"
6. **Output format** — "bullet points" / "detailed report"

## Context Efficiency (Key Insight)

**Lazy context loading:** Don't pay for context that might not help.

| Context Source | Token Cost | Relevance Likelihood | When to Include |
|----------------|------------|---------------------|-----------------|
| Recent conversation | Low (already in context) | High | Default |
| Memory files | High (read + parse + inject) | Variable | Triggered |
| User statements | Low | High | Always (in summary) |

**The principle:** Default to the cheapest context that's likely relevant. Let user signals expand scope when needed.

## Why Include Existing Knowledge?

Without it:
```
User: "We've discussed tariff basics. Now deep dive into steel."
Research Agent: *starts from scratch, explains tariffs*
```

With it:
```
Handoff: "User understands tariff basics. Focus on steel specifically."
Research Agent: *skips intro, goes deep on steel*
```

Existing knowledge acts as a "don't repeat this" filter.

## Analogy

Briefing a human researcher:
- Start with "here's what we just discussed"
- Don't dump your entire notes archive unless they ask
- Let them ask clarifying questions if they need more context

---

*Concept locked: 2026-02-10*
