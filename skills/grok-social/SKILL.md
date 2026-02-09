# Grok Social Search

Real-time X/Twitter search via xAI's Grok API. **Only model with native X access.**

## When to Use
- X/Twitter searches (posts, users, trends)
- Social media monitoring
- Real-time sentiment/reactions
- Finding what people are saying about topics

## Usage
```bash
python3 ~/.openclaw/workspace/skills/grok-social/search.py "your query here"
```

## Options
- `--mode x_search|web_search` — Search mode (default: x_search)
- `--max-tokens N` — Max response tokens (default: 1000)

## Examples
```bash
# Search X/Twitter
python3 ~/.openclaw/workspace/skills/grok-social/search.py "what are people saying about Claude AI"

# Search for trends
python3 ~/.openclaw/workspace/skills/grok-social/search.py "trending AI topics today"

# Web search via Grok (alternative)
python3 ~/.openclaw/workspace/skills/grok-social/search.py "latest news" --mode web_search
```

## Notes
- Real-time X/Twitter data access (unique to Grok)
- Returns posts, engagement metrics, sentiment
- Live Search API is free during beta
