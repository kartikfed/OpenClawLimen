# Concept: Research Agent Internals

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [ReAct Pattern](./react-pattern.md), [Tools and Tool Definitions](./tools-and-tool-definitions.md)*

## The Core Loop

ReAct pattern applied to research:

```
Receive handoff (query, context, constraints)
  │
  ▼
┌─────────────────────────────────────────┐
│  THINK: What do I need to find?         │
│  - Decompose query into sub-questions   │
│  - Identify what I don't know yet       │
│  - Plan search strategy                 │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  ACT: Execute search                    │
│  - Call search tool with query          │
│  - Optionally: browse specific URLs     │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  OBSERVE: Process results               │
│  - Extract relevant information         │
│  - Note sources                         │
│  - Identify gaps still remaining        │
└─────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────┐
│  EVALUATE: Am I done?                   │
│  - Have I covered the query?            │
│  - Do I have enough sources?            │
│  - Are constraints met?                 │
│  - Confidence level?                    │
│                                         │
│  If NO → loop back to THINK             │
│  If YES → compile and return            │
└─────────────────────────────────────────┘
  │
  ▼
Return structured output to main agent
```

## Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `web_search` | Find sources on a topic | `web_search("steel tariffs 2024")` |
| `browse_url` | Read specific page in depth | `browse_url("https://...")` |
| `extract_content` | Pull specific info from page | `extract_content(url, "statistics")` |

**Minimal viable:** Just `web_search`
**More capable:** Add `browse_url` for full page content

## System Prompt (Behavior Encoding)

```
You are a research agent. Your job is to thoroughly investigate a topic and return comprehensive findings.

## Your Process

1. DECOMPOSE the query into sub-questions
   - What are the key aspects to cover?
   - What would a thorough answer need?

2. SEARCH strategically
   - Start broad, then narrow based on findings
   - Use different phrasings for diverse sources
   - Aim for {min_sources} - {max_sources} quality sources

3. EVALUATE sources
   - Prefer authoritative sources (gov, academic, major publications)
   - Note when sources disagree
   - Be skeptical of outdated information

4. SYNTHESIZE findings
   - Connect information across sources
   - Note confidence level based on source agreement
   - State what you COULDN'T find

5. KNOW WHEN TO STOP
   - You've covered all aspects of the query
   - Additional searches return redundant information
   - You've hit {max_searches} searches

## You MUST
- Cite sources for all factual claims
- Distinguish between facts and opinion
- Acknowledge gaps and limitations
- Stay focused on the query

## You MUST NOT
- Make up information
- Present single-source claims as established fact
- Ignore specified constraints
- Continue searching indefinitely
```

## Prompt vs Code Enforcement

| Behavior | Where to Enforce |
|----------|------------------|
| Max searches limit | **Code** — hard stop |
| Source diversity | **Prompt** — guidance |
| Output format | **Code** — JSON schema |
| Timeout | **Code** — kill after X seconds |
| Tool availability | **Code** — only expose needed tools |

**Principle:** Prompts are suggestions. Code is enforcement. Use code for cost control and output format.

## Example Execution Trace

Query: "Impact of tariffs on US steel industry, 2024, economic effects"

```
THINK: 
- Sub-questions: What tariffs? Producer effects? Consumer effects? Economist views?
- Need 2024-specific data per constraints
- Plan: Overview search, then targeted searches

ACT: web_search("US steel tariffs 2024 economic impact overview")

OBSERVE:
- Found Trade.gov overview, Reuters article, Peterson Institute analysis
- Gap: Don't have consumer/downstream impact yet

THINK:
- Have producer side, need consumer side

ACT: web_search("steel tariffs impact manufacturing costs 2024")

OBSERVE:
- Found industry report, economic analysis on job losses
- Now have both sides

EVALUATE:
- Query covered? Yes
- Constraints met? Yes (2024 data)
- Source count? 5 (sufficient)
- Confidence? High

→ COMPILE and RETURN
```

---

*Concept locked: 2026-02-10*
