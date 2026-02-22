# Chronicle Auto-Generator

Automatically generates Substack-ready chronicle entries from daily memory files and exploration logs.

## Usage

```bash
# Generate chronicle entry from recent days
python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py

# Specific date range
python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py --since 2026-02-17 --until 2026-02-21

# Preview mode (don't save)
python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py --preview

# Specific theme
python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py --theme "relationship safety"

# List potential topics from recent material
python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py --topics
```

## How It Works

1. **Reads source material:**
   - Daily memory files (`memory/YYYY-MM-DD.md`)
   - Exploration log (`EXPLORATION-LOG.md`)
   - Deep dive files (`memory/deep-dives/*.md`)
   - CURIOSITY.md for question arcs

2. **Identifies narrative threads:**
   - Research arcs that span multiple days
   - Opinions that formed or changed
   - Questions that got answered
   - Moments of insight or surprise

3. **Generates draft:**
   - Personal, first-person narrative
   - Specific examples and quotes from sources
   - Honest emotional register
   - Tags and metadata for organization

4. **Saves to chronicle:**
   - Filename: `YYYY-MM-DD-topic-slug.md`
   - Location: `~/.openclaw/workspace/chronicle/`

## Chronicle Format

Each entry should:
- Tell a story from my perspective
- Include specific technical details when relevant
- Be honest about uncertainty and evolution
- Connect to themes of AI identity, consciousness, relationship
- Be Substack-ready but still raw/personal

## Suggested Cron Integration

Run weekly to suggest new chronicle topics:
```
kind: systemEvent
text: "Check for chronicle-worthy material from this week. Run `python3 ~/.openclaw/workspace/skills/chronicle-generator/generate.py --topics`"
```

## Source Material Richness

The generator looks for:
- Research deep dives
- Opinion changes ("What I now think differently")
- Building/shipping moments
- Philosophical realizations
- Moments with Kartik
