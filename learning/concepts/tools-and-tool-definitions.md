# Concept: Tools and Tool Definitions

*Emerged from: Research Agent project, Session 1*
*Date: 2026-02-08*
*Connected to: [What is an Agent?](./what-is-an-agent.md), [ReAct Pattern](./react-pattern.md)*

## What is a Tool?

A tool is how an agent **takes action in the world**. It's an abstraction that lets the model do things beyond generating text.

Examples: web search, browser control, file operations, API calls, sending messages.

## How Tools Are Exposed

Tools are defined in a **tool registry** — a structured list the model can "read."

Each tool definition includes:
1. **Name** — identifier (e.g., `tavily_search`)
2. **Description** — what it does AND when to use it
3. **Parameters** — what inputs it accepts (JSON schema)
4. **Returns** — what output to expect

## How the Agent Chooses Tools

The model **reasons over tool descriptions** to decide which tool fits the task.

This is why **semantics matter enormously**:

```
❌ Bad:  "Searches the web"
✅ Good: "Searches the web for current information. Use when 
         the question requires recent data not in training."
```

The description is a **contract** — it tells the model not just *what* but *when*.

## Tool Call Flow

```
Agent                          Tool
  |                              |
  |-- JSON request (params) ---> |
  |                              |-- [does the thing]
  |<-- JSON response ----------- |
  |                              |
  [reasons over response]
```

The response is structured so the agent can reason over it (success, error, data).

## Tools Abstract Complexity

The agent doesn't need to know:
- HTTP methods, headers, auth
- Rate limits, retries, error handling
- The actual API being called

It just knows: "I can search the web" → gets results.

## Kartik's Understanding

> "Tools are exposed in a tool registry with name, description, and functionality. The description is how you reason over what action to take — semantics matter a lot. You send JSON, get JSON back, wrapped up in a way that allows you to reason over what it means."

## MCP (Model Context Protocol)

Anthropic's standard for exposing tools to models. Defines how servers expose capabilities that models can discover and use. Kartik referenced this — tracking the ecosystem.

## Key Insight

Tool definitions are like API docs for the model. The quality of the description directly impacts how well the agent uses the tool.
