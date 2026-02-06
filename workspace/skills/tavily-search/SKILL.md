# Tavily Search

Fast, AI-optimized web search via Tavily API.

## When to Use
- Web research requiring current information
- Questions needing multiple sources
- Any web search task (replaces Brave)

## Usage
```bash
python3 ~/.openclaw/workspace/skills/tavily-search/search.py "your query here"
```

## Options
- `--max-results N` — Number of results (default: 5)
- `--search-depth basic|advanced` — Search depth (default: basic)
- `--include-answer` — Include AI-generated answer

## Examples
```bash
# Basic search
python3 ~/.openclaw/workspace/skills/tavily-search/search.py "latest AI news"

# Deep research
python3 ~/.openclaw/workspace/skills/tavily-search/search.py "transformer architecture explained" --search-depth advanced --include-answer
```

## Notes
- 180ms average latency
- Returns structured, LLM-ready content
- Includes source URLs for citation
