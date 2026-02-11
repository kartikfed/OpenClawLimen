# Concept: Iteration Routing

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Trigger Design](./trigger-design.md), [Handoff Design](./handoff-design.md)*

## The Question

When a user follows up after receiving research results, how does the main agent decide what to do?

## Two-Factor Decision Model

Iteration routing uses the same intent detection pattern as initial triggers, with an added dimension:

| Factor 1: Research Intent? | Factor 2: Related to Previous? | Action |
|---------------------------|-------------------------------|--------|
| Yes | No (new topic) | **Fresh delegation** |
| Yes | Yes (same topic) | **Build on previous** |
| No | Yes (same topic) | **Main agent handles** |
| No | No | Normal conversation |

## The Key Insight

Research intent is the PRIMARY decision factor. Topic relatedness determines HOW to delegate, not WHETHER to delegate.

## Examples

```
Previous research: Steel tariff impacts

User: "What about the EU's trade policy?"
→ Research intent: YES
→ Related to previous: NO (new topic)
→ Action: Fresh delegation

User: "Dig deeper on the job loss numbers"
→ Research intent: YES
→ Related to previous: YES
→ Action: Build on previous

User: "Can you explain point 3 in simpler terms?"
→ Research intent: NO (clarification)
→ Related to previous: YES
→ Action: Main agent handles

User: "Thanks, what's the weather?"
→ Research intent: NO
→ Related to previous: NO
→ Action: Normal conversation
```

## Intent Classification Output

```json
{
  "research_intent": true | false,
  "topic_continuity": "new" | "continuation" | "clarification"
}
```

---

## Context Curation for "Build on Previous"

When building on previous research, context size matters.

### The Problem

Large context → degraded relevance due to:
- **"Lost in the Middle"** — Models attend more to beginning/end; middle info gets less attention
- **Signal dilution** — More irrelevant context = harder to find what matters
- **Attention drift** — Earlier details fade as model processes

### The Principle

Provide the **relevant subset** PLUS enough **broader context** to understand the relationship.

### Handoff Structure

```json
{
  "query": "Dig deeper on the job loss numbers",
  
  "grounding": {
    "original_topic": "Economic impact of US steel tariffs (2024)",
    "relationship": "Job loss was one finding in the broader analysis",
    "why_it_matters": "User wants deeper understanding of this tradeoff"
  },
  
  "relevant_prior_findings": {
    "excerpt": "Economists estimate 13 jobs lost for every 1 saved...",
    "sources_for_this_point": ["Peterson Institute", "NBER"],
    "confidence_on_this_point": "medium"
  },
  
  "instruction": "Expand on job loss estimates. Find additional sources, methodology details. Keep connected to broader tariff context."
}
```

### What This Achieves

| Component | Purpose |
|-----------|---------|
| `grounding` | Prevents isolation — agent knows broader context |
| `relevant_prior_findings` | Focused subset — only what's relevant |
| `instruction` | Explicit guidance — maintain connection |

### The Analogy

Briefing a human researcher:

❌ "Here's everything from the last report. Now dig into point 3."

✅ "Last time we looked at tariff impacts overall. One finding was the 13:1 job loss ratio. Dig deeper on that specifically. Here's what we found and the sources. Keep it connected to the broader question."

---

## Industry Validation

Anthropic's multi-agent research system uses similar patterns:

> "The essence of search is compression: distilling insights from a vast corpus. Subagents facilitate compression by operating in parallel with their own context windows."

They explicitly manage context size by having subagents work independently before returning compressed findings to the lead agent.

### References

- [How we built our multi-agent research system - Anthropic](https://www.anthropic.com/engineering/multi-agent-research-system)

---

*Concept locked: 2026-02-10*
