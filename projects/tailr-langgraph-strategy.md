# Tailr v4: LangGraph Architecture Strategy

*Prepared for Rohan call — Monday, Feb 10, 2026, 5:00 PM ET*
*Last updated: Feb 10, 2026 1:30 AM by Limen*

---

## Executive Summary

Tailr has gone through three iterations over four months. The main issues identified:
- **Timeout problems on long conversations**
- **Stateless between sessions** (users lose context)
- **No learning from past iterations** (each resume starts fresh)

This document proposes LangGraph patterns that directly address these issues while creating competitive differentiation. The core thesis: **Memory is Tailr's moat.**

---

## Current State (Tailr v3)

Based on notes and context:
- Resume optimization via LangGraph + vector embeddings
- Conversational interface for iterative resume improvement
- **Pain point:** Agent timeouts on long conversations
- **Pain point:** No persistence between sessions
- **Pain point:** Each new user/job combo starts from scratch

---

## Proposed Architecture: LangGraph + Memory Stack

### 1. Checkpointing for Conversation Continuity

**Problem:** Timeouts on long conversations
**Solution:** Persistent checkpointing with timeout resilience

```python
from langgraph.checkpoint.postgres import PostgresSaver

# Production checkpointer (replace MemorySaver)
checkpointer = PostgresSaver.from_conn_string(
    "postgresql://user:pass@host/tailr_db"
)

graph = workflow.compile(checkpointer=checkpointer)
```

**Key benefits:**
- Conversations can pause and resume across sessions
- If timeout occurs, user picks up exactly where they left off
- Thread-scoped state persists through disconnects/crashes
- Enables "time travel" debugging (see every state transition)

**Implementation pattern:**
```python
# Each conversation gets a thread_id
config = {"configurable": {"thread_id": f"user_{user_id}_job_{job_id}"}}

# Invoke with automatic checkpointing
result = graph.invoke(input, config)

# If timeout: user returns later, same thread_id picks up
result = graph.invoke({"continue": True}, config)
```

**Timeout handling:**
- Set longer timeouts for LLM nodes (30-60s vs current 7s)
- Add streaming for immediate feedback while processing
- Implement "background processing" pattern for heavy operations

---

### 2. Memory Store for Cross-Session Persistence

**Problem:** Users lose context between sessions; no learning from past work
**Solution:** LangGraph Memory Store with custom namespaces

```python
from langgraph.store.memory import InMemoryStore
# Production: use PostgresStore or MongoDB

store = InMemoryStore()

# Three namespace patterns for Tailr:
# 1. User profile: /users/{user_id}/profile
# 2. Job applications: /users/{user_id}/jobs/{job_id}
# 3. Global patterns: /patterns/{industry}
```

**What to store:**

| Namespace | Content | Purpose |
|-----------|---------|---------|
| `/users/{id}/profile` | Skills, experiences, writing style preferences | Personalization |
| `/users/{id}/resume_versions` | Past resume iterations with outcomes | Learn what worked |
| `/users/{id}/jobs/{job_id}` | Job-specific context, tailoring notes | Resume-job matching |
| `/patterns/{industry}` | Industry-specific success patterns | Cross-user learning |

**Example: Storing user preferences**
```python
# When user gives feedback on resume draft
store.put(
    namespace=("users", user_id, "preferences"),
    key="writing_style",
    value={
        "tone": "professional but warm",
        "bullet_point_style": "quantified achievements",
        "avoid": ["buzzwords", "generic descriptors"],
        "updated_at": datetime.now().isoformat()
    }
)

# Later: retrieve and apply
prefs = store.get(("users", user_id, "preferences"), "writing_style")
```

---

### 3. Memory Types for Tailr

Map LangGraph's memory taxonomy to Tailr's domain:

#### Semantic Memory (Facts)
- User's actual experiences, skills, certifications
- Company research (what they value, culture signals)
- Job description parsed requirements
- **Store as:** Structured profile documents

#### Episodic Memory (Experiences)
- Past resume iterations and user feedback
- What worked for similar roles (few-shot examples)
- Successful vs unsuccessful applications
- **Store as:** Timestamped experience records

#### Procedural Memory (Instructions)
- User's formatting preferences
- Industry-specific optimization rules
- Company-specific tailoring patterns
- **Store as:** Dynamic system prompt components

---

### 4. Streaming for Better UX

**Problem:** Long operations feel broken
**Solution:** Token-level streaming with progress indicators

```python
# Stream both tokens AND intermediate steps
async for event in graph.astream(input, config, stream_mode=["values", "updates"]):
    if "messages" in event:
        # Stream LLM tokens as they generate
        yield event["messages"][-1].content
    elif "step" in event:
        # Show progress: "Analyzing job requirements..."
        yield f"[Step: {event['step']}]"
```

**UX improvements:**
- Show "Analyzing job description..." while parsing
- Stream resume sections as they're written
- Display "Comparing against your experience..." during matching
- Token-by-token rendering for final output

---

### 5. Multi-Agent Architecture

Consider splitting Tailr into specialized agents:

```
┌─────────────────────────────────────────────────────────────┐
│                    Tailr Supervisor                         │
│              (Routes tasks, maintains state)                │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  JD Analyzer  │   │ Resume Writer │   │ Match Scorer  │
│  (Parse job   │   │ (Generate     │   │ (Compare fit, │
│   requirements)│   │   content)    │   │   suggest gaps)│
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                    ┌───────────────┐
                    │ Output Agent  │
                    │ (Format,      │
                    │  finalize)    │
                    └───────────────┘
```

**Benefits:**
- Each agent can be optimized independently
- Parallel execution where possible (JD analysis + profile retrieval)
- Clearer state management per step
- Easier to debug and improve individual components

---

### 6. Human-in-the-Loop Patterns

Tailr is inherently collaborative. Use LangGraph's interrupt patterns:

```python
from langgraph.prebuilt import interrupt

def get_user_feedback(state):
    """Pause for user input on draft."""
    if state["draft_ready"] and not state["user_approved"]:
        feedback = interrupt(
            message="Here's your draft. What would you like to change?",
            options=["approve", "revise", "start over"]
        )
        return {"user_feedback": feedback}
```

**Interrupt points:**
1. After JD analysis: "Is this interpretation correct?"
2. After first draft: "What would you like to change?"
3. Before finalization: "Ready to export?"

---

### 7. Competitive Differentiation

What Tailr can do that competitors can't (with Memory Store):

| Feature | Stateless Competitors | Tailr with Memory |
|---------|----------------------|-------------------|
| Remember user's style | ❌ Start fresh | ✅ Apply learned preferences |
| Track application history | ❌ | ✅ "You applied to 3 similar roles..." |
| Learn from feedback | ❌ | ✅ "Last time you preferred..." |
| Cross-job patterns | ❌ | ✅ "For PM roles, your metrics work well" |
| Resume versioning | ❌ | ✅ "Here's what changed since v2" |

**Marketing angle:** "Your resume AI that actually remembers you."

---

## Implementation Roadmap

### Phase 1: Stability (Week 1-2)
- [ ] Replace MemorySaver with PostgresSaver
- [ ] Increase timeouts to 45s for LLM nodes
- [ ] Add basic streaming for token output
- [ ] Implement thread_id per user-job pair

### Phase 2: Memory (Week 3-4)
- [ ] Set up Memory Store with namespaces
- [ ] Store user preferences on feedback
- [ ] Retrieve and apply preferences on new sessions
- [ ] Add resume version history

### Phase 3: Learning (Week 5-6)
- [ ] Track application outcomes (if user shares)
- [ ] Build few-shot examples from successful resumes
- [ ] Implement cross-user pattern learning
- [ ] A/B test personalization impact

### Phase 4: Multi-Agent (Week 7-8)
- [ ] Split into specialized agents
- [ ] Add parallel execution for independent tasks
- [ ] Implement supervisor routing
- [ ] Add human-in-the-loop interrupts

---

## Key Resources

**LangGraph Docs:**
- [Checkpointers](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
- [Memory Store](https://docs.langchain.com/oss/python/langgraph/memory)
- [Streaming](https://langchain-ai.github.io/langgraph/how-tos/stream-values/)
- [Multi-Agent](https://blog.langchain.com/langgraph-multi-agent-workflows/)

**Reference Implementations:**
- [Memory Template](https://github.com/langchain-ai/memory-template) - Profile-based memory
- [Trustcall](https://github.com/hinthornw/trustcall) - Memory updates without schema drift

**Research:**
- [Long-Running Processes with LangGraph](https://www.auxiliobits.com/blog/orchestrating-long-running-processes-using-langgraph-agents/)
- [MongoDB + LangGraph Memory](https://www.mongodb.com/company/blog/product-release-announcements/powering-long-term-memory-for-agents-langgraph)

---

## Questions for Rohan Call

1. What's the current state schema? (need to understand what we're checkpointing)
2. What's the biggest friction point users hit?
3. Are we tracking any success metrics? (application outcomes, user retention)
4. What's the infrastructure? (hosting, database options)
5. Budget for managed services vs self-hosted?

---

## TL;DR for Kartik

**The one-sentence pitch:** Memory turns Tailr from a tool into a relationship.

**Three immediate wins:**
1. **PostgresSaver** → no more timeout crashes
2. **Streaming** → users see progress immediately
3. **Memory Store** → "Your resume AI that remembers you"

**One big unlock:** Learning from past iterations = compounding improvement.

Ready to discuss implementation details on the call.

---

*Generated by Limen during autonomous night session, Feb 10 2026*
