# Research Agent Skill

**Status:** Working v1 prototype
**Built:** 2026-02-09 (nightly session, while Kartik slept)

A working research agent that implements the concepts from our learning session.

## What It Does

1. Takes a research topic
2. Performs initial web search (Tavily)
3. Identifies follow-up questions (knowledge gaps)
4. Performs deeper searches
5. Synthesizes findings into a report with sources
6. Shows the full ReAct thought trace

## Usage

```bash
# Basic research
python3 ~/.openclaw/workspace/learning/research-agent/src/research_agent.py "topic"

# With output file
python3 ~/.openclaw/workspace/learning/research-agent/src/research_agent.py "topic" --output report.md

# Custom search depth
python3 ~/.openclaw/workspace/learning/research-agent/src/research_agent.py "topic" --max-searches 7
```

## Example

```bash
python3 research_agent.py "AI agent memory architectures" --max-searches 5
```

Output:
- Performs 4-5 searches (initial + follow-ups)
- Collects ~10-15 sources
- Generates markdown report with findings and citations
- Shows full thought trace (ReAct pattern visible)

## Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **Agent** | Goal-directed, autonomous, loops until done |
| **ReAct** | Explicit Thought → Action → Observation steps |
| **Tools** | Tavily search via structured JSON interface |
| **Multi-step** | Initial search → identify gaps → follow-up searches |
| **Source tracking** | Every finding linked to its source |

## What's Next (M4-M5)

- [ ] Integration with Limen (delegation pattern)
- [ ] LLM-based follow-up question generation
- [ ] LLM-based synthesis (not just structured output)
- [ ] Quality evaluation / self-critique
- [ ] Confidence scores

## Reports Generated

Pre-generated reports for Kartik's job search:
- `reports/anthropic-pm-prep.md` — Anthropic PM interview prep
- `reports/jane-street-pm-prep.md` — Jane Street PM interview process
