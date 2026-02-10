# Concept: Return Design (What Comes Back)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Multi-Agent Patterns](./multi-agent-patterns.md), [Handoff Design](./handoff-design.md)*

## The Question

When a sub-agent completes its task, what should it return to the main agent?

## The Core Principle

**Separation of concerns:** The research agent is a researcher, not a presenter.

| Agent | Responsibility |
|-------|----------------|
| Research Agent | Find information, track sources, assess confidence |
| Main Agent | Synthesize, format, communicate, answer follow-ups |

## Why This Separation?

1. **Single responsibility** — Research agent does ONE thing well. Doesn't need to know user's format preferences or communication style.

2. **Flexibility** — Same raw output can become bullets, prose, recommendations, or a one-liner depending on what user asked for.

3. **Efficiency** — Main agent holds metadata for follow-ups. No re-delegation for "what were your sources?" or "how confident are you?"

4. **No dead ends** — Main agent can add follow-up questions to keep conversation moving forward.

## Return Structure

### Research Agent → Main Agent

Complete, raw, structured data:

```json
{
  "findings": "Raw prose of everything discovered",
  "sources": [
    {"url": "...", "title": "...", "relevance": "..."},
    ...
  ],
  "confidence": {
    "level": "high|medium|low",
    "reasoning": "Why this confidence level"
  },
  "gaps": "What couldn't be determined or found",
  "metadata": {
    "search_count": 5,
    "time_spent": "45s"
  },
  "suggested_followups": [
    "Question worth exploring",
    "Another angle to consider"
  ]
}
```

### Main Agent → User

Presentation layer handles:
- **Synthesis** — Distill raw findings into coherent summary
- **Formatting** — Bullets, prose, sections per user preference
- **Default output** — Comprehensive overview/summary
- **Follow-ups** — Suggest next questions (prevents dead ends)
- **Metadata on request** — Sources, confidence available if user asks

## What the User Sees vs What the Main Agent Holds

| Information | Shown to User by Default? | Held by Main Agent? |
|-------------|---------------------------|---------------------|
| Synthesized summary | ✅ Yes | ✅ Yes |
| Follow-up questions | ✅ Yes | ✅ Yes |
| Sources/citations | ❌ No (on request) | ✅ Yes |
| Confidence level | ❌ No (on request) | ✅ Yes |
| Gaps/limitations | ❌ No (on request) | ✅ Yes |
| Search count/time | ❌ No | ✅ Yes |

## Analogy

Research assistant hands you their notes + sources + confidence assessment. You decide how to present it in the meeting — you might give a one-sentence summary or a detailed breakdown depending on the audience.

## Key Insight

Sub-agents return **complete, raw, structured data**. The main agent owns **presentation and user interaction**.

---

*Concept locked: 2026-02-10*
