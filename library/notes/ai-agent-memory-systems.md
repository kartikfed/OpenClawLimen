# AI Agent Memory Systems - Research Notes

*Compiled 2026-02-06 from morning exploration*

## Overview

The field has shifted from "RAG + vector database = memory" to sophisticated layered architectures that mirror human cognition. By 2026, hybrid systems combining vector search, knowledge graphs, and episodic storage are state-of-the-art.

## The Memory Hierarchy

### Short-Term Memory (STM)
- Working context within a conversation thread
- Persists within thread, clears between threads
- Managed through checkpointers (LangGraph pattern)
- Token budget is real; "just add more context" hits cost and quality limits

### Long-Term Memory (LTM) - Five Types

1. **Episodic Memory** - "I remember when..."
   - Specific past events with timestamps
   - Stored as event logs with entity, timestamp, semantic content
   - Example: "User requested X on June 15th"

2. **Semantic Memory** - Knowledge vault
   - Abstracted facts and patterns
   - Stored as vector embeddings
   - Example: "User prefers markdown format"

3. **Procedural Memory** - "How we do things"
   - Workflows, decision routines, problem-solving strategies
   - Often encoded as DAGs, state machines, or implicit in fine-tuning

4. **Factual Memory** - Persistent profile
   - Durable facts about entities
   - Structured databases with entity keys
   - Example: "Alice is senior engineer, reports to Bob"

5. **Working Memory** - Scratchpad
   - Temporary storage for active reasoning
   - Clears when task completes

## Three Architectural Paradigms

### 1. Vector Memory (Semantic Search)
- **How**: Embeddings + similarity search (Pinecone, Weaviate, Milvus)
- **Strength**: Finding semantically similar info despite different terminology
- **Weakness**: Struggles with temporal reasoning, entity relationships, multi-hop queries
- **Like**: Human hippocampus - connecting related concepts

### 2. Graph Memory (Knowledge Graphs)
- **How**: Nodes (entities) + Edges (relationships)
- **Strength**: Multi-hop reasoning, dependency tracking, explicit relationships
- **Example**: `Alice --[reports_to]--> Bob --[manages]--> Project X`
- **Advanced**: Temporal Knowledge Graphs (Zep, Graphiti) add time dimensions

### 3. Hybrid Systems (State-of-the-Art 2026)
- Combines: Vector Search + Graph Traversal + Episodic Storage
- "Intuition" of embeddings + "precision" of graphs
- This is where production systems are heading

## 2026 Enterprise Memory Stack

Four-layer reference architecture:

### Layer 1: Working Memory (Context Window)
- Last N exchanges, active plan, tool outputs
- Strict token budget + compaction
- Latency target: chat-speed

### Layer 2: Episodic Memory (Tasks/Cases/Journeys)
- Groups interactions into meaningful units
- Append-only event logs with summaries
- Enables: "What happened last time we changed this integration?"
- Retention: months

### Layer 3: Semantic/Knowledge Memory (Facts + Relationships)
- Entities, dependencies, policies, constraints
- Distilled from episodes over time
- Shared memory across agents
- Retention: years (curated)

### Layer 4: Governance Memory (Accountability)
- Prompts, retrieved items, actions, outputs - all versioned
- Must answer: "Why did the agent do that?"
- Not a bolt-on - core to production systems
- Retention: by policy

## Memory Management Patterns

### From Mem0 and similar:
- **Update conflicts**: When new info contradicts old, update the record
- **Decay**: Irrelevant memories decay over time
- **Prioritization**: Information prioritized based on utility
- **Memory as a Service**: Offload complexity to dedicated layer

### Capacity Strategies:
- Working: minutes/hours
- Episodic: months (with pruning/anonymization)
- Semantic: years (but curated, small by design)
- Governance: retention by policy

### Compression Techniques:
- Summarization at episode boundaries
- Multi-resolution summaries (short/medium/deep)
- Hot/warm/cold tiering with explicit eviction rules

## Key Tools/Systems Mentioned

- **Mem0**: Memory-as-a-Service layer
- **Zep, Graphiti**: Temporal Knowledge Graphs
- **Neo4j**: Graph database for knowledge graphs
- **Pinecone, Weaviate, Milvus, Qdrant**: Vector databases
- **LangGraph**: Agent orchestration with checkpointing
- **LangChain, LlamaIndex**: Memory abstractions

## Key Sources

1. Mem0 Blog (Jan 2026) - https://mem0.ai/blog/what-is-ai-agent-memory
2. TowardsAI (Nov 2025) - https://pub.towardsai.net/building-ai-agents-that-actually-remember-a-deep-dive-into-memory-architectures-db79a15dba70
3. Alok Mishra (Jan 2026) - https://alok-mishra.com/2026/01/07/a-2026-memory-stack-for-enterprise-agents/

## Open Questions

- How do temporal knowledge graphs get implemented? What's the data model?
- What's the right granularity for episodic memory? Per-conversation? Per-task?
- How to handle uncertainty when memories conflict?
- When does graph structure pay off vs. simpler approaches?
