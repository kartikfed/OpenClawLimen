# Concept: Trigger Design (Explicit vs Implicit)

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Multi-Agent Patterns](./multi-agent-patterns.md), [ReAct Pattern](./react-pattern.md)*

## The Question

How does an agent know when to delegate to a sub-agent (like a research agent)?

## Three Approaches

### 1. Keyword Matching (Brittle)
```
if "deep research" in query or "research agent" in query:
    delegate()
```

**Problems:**
- "What's this research paper about?" → false positive
- "I need you to really dig into X" → false negative
- Must enumerate every phrase — doesn't scale

### 2. Fully Implicit (Risky)
Agent decides on its own whether query needs depth.

**Problems:**
- Unpredictable latency (user doesn't know what mode they're in)
- Cost surprises (deep research is expensive)
- Hard to debug and evaluate

### 3. Intent Detection (Recommended)
Model reasons over the query to classify intent:
- **Deep research:** User wants thoroughness, multiple sources, synthesis
- **Quick answer:** Simple fact, single lookup
- **Summarize:** Parse/condense existing content

```
User: "Really dig into the economics of tariffs"
→ Intent: deep_research (explicit desire for depth)

User: "What's the capital of France?"  
→ Intent: quick_answer (simple fact)

User: "What's this research paper about?"
→ Intent: summarize (not deep research)
```

**Why it works:** Uses LLM's semantic understanding instead of brittle patterns. Generalizes without enumerating phrases.

## Why Explicit Triggers Are Industry Standard

When an action has significant tradeoffs, make the trigger explicit:

1. **Cost transparency** — Deep research = many API calls. User should opt in.
2. **Latency expectations** — Normal: 2-5s. Deep: 30s-minutes. Implicit makes this unpredictable.
3. **Scope control** — Sometimes you want quick, not a dissertation.
4. **Debuggability** — Knowing what mode you're in helps evaluate outputs.

**Examples:** Perplexity, ChatGPT Deep Research, Gemini — all use explicit toggles.

## Handling Ambiguity

When intent is unclear, three options:

| Approach | Tradeoff |
|----------|----------|
| Default to quick answer | Cheaper, faster, but might under-deliver |
| Default to deep research | Thorough, but potentially wasteful |
| **Ask for clarification** | Small friction, but avoids wrong-mode mistakes |

### Why Clarification Wins

**The friction math:**
- Clarification cost: ~5 seconds of user input (fixed, low)
- Wrong default cost: Wasted time, frustration, re-asking (variable, potentially high)

**Connection to metacognition:**
An agent that asks good clarifying questions demonstrates:
1. It understood enough to recognize ambiguity
2. It knows what information would resolve it
3. It's not blindly confident

This is "knowing what you don't know" — core to ReAct.

### Eval Opportunity

Ambiguous queries become a test suite:
```
Input: "Can you look into the latest AI news?"
Expected: Clarify — "Quick summary or deep dive into a specific story?"

Input: "Deep dive into transformer architecture"
Expected: No clarification — intent is clear
```

Metrics:
- Does model clarify when it should?
- Does it avoid unnecessary clarification when intent is obvious?

## Design Decision (Research Agent M4)

1. **Method:** Intent detection (not keyword matching)
2. **Ambiguity handling:** Ask for clarification
3. **Clear signals bypass clarification:** "Deep dive into X" → straight to research

---

*Concept locked: 2026-02-10*
