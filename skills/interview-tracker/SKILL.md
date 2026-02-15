# Interview Tracker Skill

Track job applications, interview stages, and follow-ups in a structured YAML file.

## Location

`~/.openclaw/workspace/skills/interview-tracker/`

## Usage

```bash
# List all applications with status
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py list

# Add a new application
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py add "Anthropic" "Growth PM" --priority high

# Update status (applied → screen → interview → offer → accepted/declined/rejected)
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py update "Anthropic" --status interview --stage "Technical" --next-date 2026-02-20

# Add notes to an application
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py note "Anthropic" "Great culture fit, asked good questions about my agent work"

# View timeline of upcoming deadlines/interviews
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py timeline

# Get stats
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py stats

# Archive old applications
python3 ~/.openclaw/workspace/skills/interview-tracker/tracker.py archive
```

## Data File

Applications stored in `~/.openclaw/workspace/job-search/applications.json`

## Status Flow

```
applied → screen → interview → offer
                            ↘
                              rejected/declined/accepted
```

## Fields Tracked

- Company name
- Role/Position  
- Applied date
- Current status
- Interview stages (with dates)
- Next action & deadline
- Priority (high/medium/low)
- Notes & feedback
- Contact info (recruiter name, email)
- Job posting URL

## Morning Briefing Integration

This tracker integrates with morning calls:
- Mentions upcoming interviews (next 3 days)
- Flags applications needing follow-up (>1 week no response)
- Highlights high-priority roles
