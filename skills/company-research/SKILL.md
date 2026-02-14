# Company Research Skill

Research companies for interview prep, customer discovery calls, or competitive analysis.

## Usage

```bash
# Basic research
python3 ~/.openclaw/workspace/skills/company-research/research.py "Anthropic"

# Focus on a specific aspect
python3 ~/.openclaw/workspace/skills/company-research/research.py "Jane Street" --focus interview

# Include recent news
python3 ~/.openclaw/workspace/skills/company-research/research.py "Figma" --news

# Save output to file
python3 ~/.openclaw/workspace/skills/company-research/research.py "Uber" --save

# Full research (all aspects)
python3 ~/.openclaw/workspace/skills/company-research/research.py "Actively AI" --full
```

## Focus Modes

- **general** (default): Company overview, products, culture, key people
- **interview**: Interview-specific prep, common questions, what they look for
- **discovery**: Customer discovery focus - pain points, opportunities, market position
- **competitive**: Competitive analysis - strengths, weaknesses, market position

## Output Sections

1. **Company Overview** - What they do, mission, size, funding
2. **Products & Services** - What they build/sell
3. **Recent News** - Latest developments (with --news flag)
4. **Culture & Values** - Work environment, what they value
5. **Key People** - Leadership, notable employees
6. **Interview Prep** - What they look for, common questions (interview focus)
7. **Discovery Angles** - Pain points, opportunities (discovery focus)

## Requirements

- Tavily API key (configured via `~/.openclaw/workspace/skills/tavily-search/`)

## Examples

### Interview Prep for Anthropic
```bash
python3 research.py "Anthropic" --focus interview --news
```

Output includes:
- Company overview and mission
- Recent research/product announcements
- What they look for in PMs
- Common interview questions
- Culture insights from Glassdoor/LinkedIn

### Customer Discovery for a Startup
```bash
python3 research.py "Actively AI" --focus discovery --full
```

Output includes:
- Market position and competition
- Target customers
- Potential pain points to explore
- Talking points for discovery calls
