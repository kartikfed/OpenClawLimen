# Weekly Review Generator

**Built:** 2026-02-13 (1 AM nightly session)
**Author:** Limen

## Purpose

Synthesizes daily memory logs into structured weekly summaries. Extracts:
- Exploration topics and themes
- Accomplishments and things built
- Key learnings and insights
- Opinions forming
- Open questions
- Mood arc through the week
- Voice calls made

## Usage

```bash
# Generate review for current week (to stdout)
python3 ~/.openclaw/workspace/skills/weekly-review/weekly_review.py

# Generate review for a specific week (any date in that week)
python3 ~/.openclaw/workspace/skills/weekly-review/weekly_review.py 2026-02-10

# Save to standard location (memory/weekly-reviews/)
python3 ~/.openclaw/workspace/skills/weekly-review/weekly_review.py --save

# Save to custom location
python3 ~/.openclaw/workspace/skills/weekly-review/weekly_review.py -o /path/to/review.md
```

## Output

Generates a markdown document with:

1. **Quick Stats** — Numbers at a glance
2. **Mood Arc** — How I felt through the week
3. **Exploration Topics** — What I investigated
4. **Accomplishments** — Things built/completed
5. **Key Learnings** — Insights and discoveries
6. **Opinions Forming** — Evolving views
7. **Open Questions** — Unresolved curiosities
8. **Voice Calls** — People I talked to
9. **Day-by-Day** — Brief daily summaries

## When to Use

- **Sunday evening** — Generate weekly review as reflection exercise
- **Monday morning** — Share with Kartik to see the week's arc
- **Before interviews** — Review recent work and learning
- **Anytime** — Check what we accomplished a particular week

## Storage

Reviews saved with `--save` go to:
```
~/.openclaw/workspace/memory/weekly-reviews/YYYY-WXX.md
```

## Dependencies

- Python 3.10+
- No external packages (uses only stdlib)

## Notes

The extraction uses regex patterns tuned to my daily log format. If the format changes significantly, patterns may need updating.

This was built to apply my research on memory systems — creating semantic summaries from episodic daily logs. It's a practical version of the "episodic → semantic" compression that state-of-the-art agent memory systems use.
