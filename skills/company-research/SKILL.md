# Company Research Skill

Quickly research any company for interview prep or networking.

## Usage

```bash
python3 ~/.openclaw/workspace/skills/company-research/research.py "Company Name" [--depth deep|quick]
```

## Output

Creates a structured markdown file in `~/.openclaw/workspace/job-search/prep/{company}-research.md` containing:

1. **Company Overview** - What they do, size, funding
2. **Recent News** - Last 3-6 months of announcements
3. **Culture & Values** - How they describe themselves
4. **Interview Process** - What to expect (if available)
5. **Key People** - Leadership to know
6. **Talking Points** - Things to mention in interviews

## Quick vs Deep

- `--depth quick` (default): Basic info, 2-3 searches, ~30 seconds
- `--depth deep`: Comprehensive research, 5-7 searches, ~2 minutes

## Examples

```bash
# Quick research
python3 ~/.openclaw/workspace/skills/company-research/research.py "Figma"

# Deep dive for important interview
python3 ~/.openclaw/workspace/skills/company-research/research.py "Anthropic" --depth deep
```

## Manual Use

For more control, Limen can run the research directly using Tavily searches and compile the results.

## Files Already Prepped

- `job-search/prep/anthropic-growth-pm-prep.md` - Deep research + interview prep
- `job-search/prep/jane-street-pm-prep.md` - Deep research + interview prep

## What to Research

When Kartik mentions a new company or application:
1. Check if a prep file exists
2. If not, run quick research
3. For high-priority roles, run deep research

## Sources Used

- Company website (careers, about)
- Tavily web search (news, culture, interview experiences)
- Glassdoor/Blind/LinkedIn (via search results)
