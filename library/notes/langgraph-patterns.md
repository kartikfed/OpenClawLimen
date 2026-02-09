# LangGraph Architecture Patterns

*Compiled 2026-02-06 from exploration session*

## Core Concepts

### Graph Structure
- **Nodes** = agents, functions, or decision points
- **Edges** = control flow and data paths
- **StateGraph** = centralized context for the entire workflow

### State Management
- Agents communicate through **centralized state**, not peer-to-peer
- Each agent receives current state → returns updated state
- **Immutable data structures** prevent race conditions
- Typed schemas enforce output consistency

### Control Flow
- **Conditional edges** route based on agent outputs or state
- **Parallel execution** via scatter-gather or pipeline patterns
- **Loops** implemented as recursive patterns with termination criteria
- **Subgraphs** for modularity (reusable agent groups)

## Multi-Agent Patterns

### 1. Collaboration
- Shared scratchpad — all agents see all work
- Simple routing: tool call → execute → continue or "FINAL ANSWER"
- Benefit: Full visibility
- Downside: Verbose, may pass unnecessary info

### 2. Supervisor
- Central agent routes to specialized agents
- Each agent has own prompt, LLM, tools
- Supervisor = "agent whose tools are other agents"
- Agents have independent scratchpads; only final responses go to global

### 3. Hierarchical Teams
- Subagents are themselves LangGraph objects
- Enables deeply nested, flexible architectures
- Supervisor connects subgraph-agents

## Persistence

### Checkpointers
- Save state at every "super-step"
- **Thread** = unique ID for accumulated state across runs
- **Checkpoint** = snapshot at a point in time

### Key Operations
```python
# Get latest state
graph.get_state({"configurable": {"thread_id": "1"}})

# Get full history
graph.get_state_history(config)

# Replay from checkpoint
graph.invoke(None, {"configurable": {"thread_id": "1", "checkpoint_id": "..."}})

# Update state manually
graph.update_state(config, {"key": "value"})
```

### Memory Store (Cross-Thread)
- Checkpointers = within threads
- **InMemoryStore** = across threads
- Namespace: `(user_id, "memories")`
- Use for: user preferences, accumulated knowledge, shared context

```python
in_memory_store = InMemoryStore()
namespace = (user_id, "memories")
in_memory_store.put(namespace, memory_id, {"preference": "concise"})
memories = in_memory_store.search(namespace)
```

### Production Checkpointers
- **MemorySaver** = lightweight, demos only
- **SqliteSaver** = simple persistent, single-threaded
- **PostgresSaver** = production-grade, supports pause/resume

## Production Challenges

### Monitoring
- 75%+ of systems become hard to manage at 5+ agents
- Standard tools don't map to graph execution
- LangGraph Studio helps but struggles with complex nesting

### Common Failures
1. **State corruption** from simultaneous updates
2. **Deadlocks** from circular agent dependencies
3. **Memory exhaustion** from accumulating state versions
4. **Error propagation** through shared state

### Debugging
- **Time-travel debugging** via checkpoint replay
- Immutable state enables historical analysis
- Human-in-the-loop checkpoints for manual inspection

## Sources
- https://blog.langchain.com/langgraph-multi-agent-workflows/
- https://docs.langchain.com/oss/python/langgraph/persistence
- https://latenode.com/blog/.../langgraph-multi-agent-orchestration-complete-framework-guide-architecture-analysis-2025
