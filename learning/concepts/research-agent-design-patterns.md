# Concept: Research Agent Design Patterns

*Emerged from: Research Agent project, Session 2*
*Date: 2026-02-10*
*Connected to: [Research Agent Internals](./research-agent-internals.md), [Multi-Agent Patterns](./multi-agent-patterns.md)*

## The Key Insight

There is no single standard for designing a research agent. Different systems make different tradeoffs based on their priorities.

## Design Patterns

### Pattern 1: Iterative Search

```
Search → Observe → Think → Search again → ... → Compile
```

**Characteristics:**
- Each search informs the next
- Agent decides when it has enough
- Flexible but unpredictable (might do 3 or 10 searches)

**Used by:** Custom agent implementations, AutoGPT-style systems

**Best for:** Exploratory research, unknown scope

---

### Pattern 2: Parallel Search

```
Decompose query into N sub-questions upfront
  → Search all N in parallel
  → Synthesize results
```

**Characteristics:**
- Fixed search count (predictable cost/latency)
- Less adaptive (can't follow unexpected threads)
- Fast but rigid

**Used by:** Perplexity, production systems where latency matters

**Best for:** Well-defined queries, speed-critical applications

---

### Pattern 3: Hierarchical

```
Plan phase: Create detailed research outline
  → Execute phase: Fill in each section
  → Review phase: Check for gaps, fill them
  → Compile
```

**Characteristics:**
- More structured, explicit planning
- Longer but more thorough
- Comprehensive but slow

**Used by:** OpenAI Deep Research, academic research assistants

**Best for:** Complex topics, long-form output

---

### Pattern 4: Multi-Agent Research

```
Planner Agent → creates research plan
Researcher Agent(s) → execute searches (can be parallel)
Critic Agent → reviews findings
Writer Agent → synthesizes final output
```

**Characteristics:**
- Separation of concerns within research process
- More complex to build
- Modular but heavyweight

**Used by:** CrewAI, multi-agent frameworks

**Best for:** Large-scale research, team-like workflows

---

## Tradeoff Space

| Priority | Design Choice |
|----------|---------------|
| **Speed** | Parallel search, fixed count |
| **Cost control** | Hard limits, simpler loop |
| **Thoroughness** | Iterative with coverage checking |
| **Predictability** | Fixed plan upfront |
| **Adaptability** | Iterative, follow threads |

**There's no "best" — only tradeoffs.**

## Combining Patterns

Real systems often combine patterns:

**Example: Simple + Deep modes (from Reddit diagram)**

Mode 1 (Simple): Iterative search
```
Thinking → Knowledge Gap → Tool Selector → Tools → Writer
    ↑___________________________|
              (loop)
```

Mode 2 (Deep): Parallel + Hierarchical
```
Planner → [Researcher 1] ↘
          [Researcher 2] → Proofreader → Output
          [Researcher 3] ↗
```

**Key insight:** Deep mode reuses the iterative researcher as a building block. Composition, not replacement.

## Common Elements Across Patterns

Despite variation, most research agents include:

1. **Query decomposition** — Breaking complex queries into sub-questions
2. **Source diversity** — Multiple searches with varied phrasing
3. **Structured output** — Findings + sources + confidence
4. **Stopping criteria** — Coverage-based or count-based

## For Our Research Agent (M4)

**Starting with:** Iterative search (Pattern 1)

**Why:**
- Teaches core ReAct loop
- Flexible, shows agent decision-making
- Can add sophistication later

**Evolution path:**
1. Master iterative (single agent)
2. Add planning step (hierarchical)
3. Parallelize sections (parallel + hierarchical)
4. Add critic/review (multi-agent)

---

*Concept locked: 2026-02-10*
