# Concept: What is an Agent?

*Emerged from: Research Agent project, Session 1*
*Date: 2026-02-08*

## The Core Distinction

**Basic LLM:** Text in → Text out. One-shot. Environment limited to the conversation.

**Agent:** Goal in → Observe-Think-Act loop → Outcome. Autonomous. Environment includes external tools and systems.

```
Basic LLM:  Input → Output (done)

Agent:      Input → Think → Act → Observe → Think → Act → ... → Output
```

## What Makes Something "Agentic"

1. **Goal-directed** — Working toward an outcome, not just responding
2. **Tool use** — Can take actions in external systems
3. **Observe-Act loop** — Sees results of actions, decides next step
4. **Autonomy** — Continues without explicit instruction until goal achieved or stuck

## Kartik's Understanding (in his words)

> "An agent can observe the output of their own actions and decide what to do next. It's goal oriented and autonomously figures out what it needs to do to reach that goal."

> "You continue to move on (without me telling you to) until you've confirmed the appointment has been made or you run into an unavoidable error state."

## Concrete Example: Mochi Grooming Booking

| Component | In Practice |
|-----------|-------------|
| **Goal** | Book a grooming appointment for Mochi |
| **Tools** | Browser (navigate site), messaging (ask clarifying questions) |
| **Observe** | Page content, calendar availability, form states |
| **Act** | Click, fill forms, select time slots |
| **Loop** | Continue through booking flow, react to what's on screen |
| **Autonomy** | Keep going until confirmed or genuinely stuck |

## Key Insight

The "loop" is what makes it agentic. Not just more capabilities — the ability to **observe results and adapt**.
