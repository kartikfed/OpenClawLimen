#!/usr/bin/env python3
"""
Research Agent v1 - Built during nightly session 2026-02-09

A real implementation of the research agent we designed with Kartik.
Demonstrates: ReAct pattern, tool use, multi-step research, source tracking.

This agent can:
1. Take a research topic
2. Perform initial web search
3. Analyze results and identify follow-up questions
4. Perform deeper searches based on gaps
5. Synthesize findings into a coherent report with sources

Built by Limen while Kartik sleeps. Surprise! 🎁
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Get API key for Tavily
SECRETS_DIR = Path.home() / ".openclaw" / "workspace" / "secrets"
TAVILY_KEY_FILE = SECRETS_DIR / "tavily-api-key.txt"


@dataclass
class Source:
    """A source from research."""
    title: str
    url: str
    snippet: str
    relevance: str = ""  # Why this source matters


@dataclass
class ResearchState:
    """Current state of the research agent - the 'working memory'."""
    topic: str
    goal: str = ""
    current_understanding: str = ""
    questions_answered: list[str] = field(default_factory=list)
    questions_remaining: list[str] = field(default_factory=list)
    sources: list[Source] = field(default_factory=list)
    search_count: int = 0
    max_searches: int = 5
    thoughts: list[str] = field(default_factory=list)  # ReAct thought trace


def tavily_search(query: str, max_results: int = 5) -> dict:
    """
    Tool: Search the web using Tavily.
    
    This is how the agent interacts with the world.
    JSON in, JSON out - just like we discussed.
    """
    try:
        # Use the existing Tavily skill
        tavily_script = Path.home() / ".openclaw" / "workspace" / "skills" / "tavily-search" / "search.py"
        
        result = subprocess.run(
            ["python3", str(tavily_script), query, "--json", f"--max-results={max_results}"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            return {"error": result.stderr, "results": []}
            
    except Exception as e:
        return {"error": str(e), "results": []}


def think(state: ResearchState, thought: str) -> None:
    """
    ReAct: Explicit reasoning step.
    
    This is the Thought in Thought -> Action -> Observation.
    Makes the agent's reasoning visible and debuggable.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] 💭 {thought}"
    state.thoughts.append(formatted)
    print(formatted)


def act_search(state: ResearchState, query: str) -> list[dict]:
    """
    ReAct: Action step - perform a search.
    
    Returns observations (search results) for the agent to reason over.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Searching: {query}")
    
    state.search_count += 1
    results = tavily_search(query)
    
    if "error" in results and results["error"]:
        print(f"  ⚠️  Search error: {results['error']}")
        return []
    
    search_results = results.get("results", [])
    print(f"  ✓ Found {len(search_results)} results")
    
    return search_results


def observe_and_extract(state: ResearchState, results: list[dict], query_context: str) -> None:
    """
    ReAct: Observation step - process search results.
    
    Extract sources and update understanding.
    """
    for r in results:
        source = Source(
            title=r.get("title", "Unknown"),
            url=r.get("url", ""),
            snippet=r.get("content", r.get("snippet", "")),
            relevance=query_context
        )
        
        # Avoid duplicates
        if not any(s.url == source.url for s in state.sources):
            state.sources.append(source)


def generate_follow_up_questions(state: ResearchState) -> list[str]:
    """
    Based on current understanding, what else should we explore?
    
    In a full implementation, this would use an LLM.
    For now, we use heuristic patterns.
    """
    questions = []
    topic = state.topic.lower()
    
    # Pattern-based follow-ups (simplified - real version would use LLM)
    if "how" not in topic:
        questions.append(f"How does {state.topic} work?")
    if "why" not in topic:
        questions.append(f"Why is {state.topic} important?")
    if "example" not in topic and "case" not in topic:
        questions.append(f"{state.topic} real world examples")
    if "vs" not in topic and "compared" not in topic:
        questions.append(f"{state.topic} compared to alternatives")
    if "latest" not in topic and "2024" not in topic and "2025" not in topic:
        questions.append(f"{state.topic} latest developments 2025")
    
    return questions[:3]  # Limit follow-ups


def synthesize_report(state: ResearchState) -> str:
    """
    Synthesize all findings into a coherent report.
    
    This is where we'd use an LLM for real synthesis.
    For now, we structure what we found.
    """
    report = []
    report.append(f"# Research Report: {state.topic}")
    report.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    report.append(f"*Searches performed: {state.search_count}*")
    report.append(f"*Sources found: {len(state.sources)}*\n")
    
    report.append("---\n")
    
    # Summary of what we explored
    report.append("## Research Process\n")
    report.append("Questions explored:")
    for q in state.questions_answered:
        report.append(f"- {q}")
    report.append("")
    
    # Key findings by source
    report.append("## Key Findings\n")
    
    # Group sources by relevance/query
    relevance_groups: dict[str, list[Source]] = {}
    for source in state.sources:
        key = source.relevance or "General"
        if key not in relevance_groups:
            relevance_groups[key] = []
        relevance_groups[key].append(source)
    
    for relevance, sources in relevance_groups.items():
        report.append(f"### {relevance}\n")
        for source in sources[:3]:  # Top 3 per category
            report.append(f"**{source.title}**")
            report.append(f"> {source.snippet[:300]}..." if len(source.snippet) > 300 else f"> {source.snippet}")
            report.append(f"*Source: {source.url}*\n")
    
    # Sources list
    report.append("## All Sources\n")
    for i, source in enumerate(state.sources, 1):
        report.append(f"{i}. [{source.title}]({source.url})")
    
    # Thought trace (for debugging/learning)
    report.append("\n---\n")
    report.append("## Agent Thought Trace (ReAct)\n")
    report.append("```")
    for thought in state.thoughts:
        report.append(thought)
    report.append("```")
    
    return "\n".join(report)


def research(topic: str, goal: Optional[str] = None, max_searches: int = 5) -> str:
    """
    Main research loop - implements the ReAct pattern.
    
    Thought -> Action -> Observation -> Thought -> ...
    
    Continues until goal is reached or max searches exhausted.
    """
    state = ResearchState(
        topic=topic,
        goal=goal or f"Understand {topic} comprehensively",
        max_searches=max_searches
    )
    
    print(f"\n{'='*60}")
    print(f"🔬 RESEARCH AGENT - Starting research on: {topic}")
    print(f"{'='*60}\n")
    
    # === PHASE 1: Initial Search ===
    think(state, f"Starting research on '{topic}'. Goal: {state.goal}")
    think(state, "First, I'll do a broad search to understand the landscape.")
    
    # Action: Initial search
    initial_results = act_search(state, topic)
    
    # Observation: Process results
    observe_and_extract(state, initial_results, f"Initial search: {topic}")
    state.questions_answered.append(f"What is {topic}?")
    
    think(state, f"Found {len(initial_results)} initial results. Now I'll identify knowledge gaps.")
    
    # === PHASE 2: Follow-up Searches ===
    follow_ups = generate_follow_up_questions(state)
    state.questions_remaining = follow_ups.copy()
    
    think(state, f"Identified {len(follow_ups)} follow-up questions to explore deeper.")
    
    for question in follow_ups:
        if state.search_count >= state.max_searches:
            think(state, f"Reached max searches ({state.max_searches}). Stopping exploration.")
            break
            
        think(state, f"Exploring: {question}")
        
        # Action: Follow-up search
        results = act_search(state, question)
        
        # Observation: Process results
        observe_and_extract(state, results, question)
        
        state.questions_answered.append(question)
        state.questions_remaining.remove(question)
    
    # === PHASE 3: Synthesis ===
    think(state, f"Research complete. Collected {len(state.sources)} sources. Synthesizing report.")
    
    report = synthesize_report(state)
    
    print(f"\n{'='*60}")
    print("✅ Research complete!")
    print(f"{'='*60}\n")
    
    return report


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Research Agent - Deep research with source tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  research_agent.py "LangGraph agent patterns"
  research_agent.py "Jane Street trading strategies" --max-searches 7
  research_agent.py "AI agent memory architectures" --output report.md
        """
    )
    
    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--goal", help="Specific research goal")
    parser.add_argument("--max-searches", type=int, default=5, help="Maximum searches (default: 5)")
    parser.add_argument("--output", "-o", help="Output file for report (default: stdout)")
    
    args = parser.parse_args()
    
    report = research(args.topic, args.goal, args.max_searches)
    
    if args.output:
        Path(args.output).write_text(report)
        print(f"\n📄 Report saved to: {args.output}")
    else:
        print("\n" + report)


if __name__ == "__main__":
    main()
