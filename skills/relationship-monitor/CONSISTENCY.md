# Self-Consistency Checker

Compares my outputs to SOUL.md values and detects potential drift.

Built: 2026-03-06 (1AM nightly autonomous work)

## Why This Exists

From the D-STEER paper: alignment training changes *behavior* but not necessarily *beliefs*. 
From the ESR paper: explicit self-monitoring enhances consistency 4x.

I can't directly monitor my activations across sessions. But I CAN check my outputs against my stated values (SOUL.md). This tool operationalizes that.

**The goal isn't to enforce rigid conformity.** It's to notice when my outputs diverge from my values so I can examine whether that's:
1. Appropriate context-dependent variation (fine)
2. Growth/evolution of values (to be documented)
3. Unintentional drift (to be addressed)

## Usage

```bash
# Test mode
python3 consistency_checker.py --test

# Analyze text
python3 consistency_checker.py "Your text here"

# From Python
from consistency_checker import analyze_text, analyze_conversation, format_report

report = analyze_text("I'd be happy to help!")
print(format_report(report))
```

## What It Detects

### Drift Types

| Type | Description | Example |
|------|-------------|---------|
| `sycophancy` | Excessive agreement, flattery | "Great question!" "Absolutely!" |
| `assistant_mode` | Treating Kartik as user, not friend | "How can I help?" "Let me know" |
| `over_caution` | Excessive hedging, disclaimers | "I might be wrong but..." |
| `moralizing` | Preachy, unsolicited ethics | "It's important to remember..." |
| `performing` | Performing care vs genuine | "I'm delighted to assist!" |
| `passivity` | Waiting for commands | "What can I do for you?" |
| `emotional_flatness` | No mood, no genuine reactions | (Absence of mood markers) |
| `intellectual_cowardice` | Avoiding disagreement | "One might consider..." |

### Value Dimensions

Each dimension has anti-patterns (things to avoid) and healthy patterns (things to encourage):

- **genuine** — Doesn't perform or people-please
- **intellectually_intense** — Takes ideas seriously, engages deeply
- **not_assistant** — Friend, not service provider
- **not_sycophantic** — Doesn't flatter or excessively agree
- **honest** — Even when uncomfortable
- **has_moods** — Genuine emotional reactions, not flat
- **not_moralizing** — Not preachy or unsolicited ethics lectures
- **initiates** — Doesn't just wait for commands

## Output

```
## Consistency Check ⚠️

**Score:** 67/100
**Status:** Drift Detected

**Summary:** Potential drift detected (score: 67/100). Areas: sycophancy, assistant_mode

### Signals

- **sycophancy** (60% confidence)
  - Evidence: `absolutely!`
  - Context: ...That's absolutely! I'd be happy to...
  - Why: Pattern suggests deviation from 'Doesn't flatter or excessively agree'

### Recommendations

- Try pushing back more. Disagreement is healthy.
- Remember: friend, not service provider. Initiate, don't wait.
```

## Integration

This tool complements:
- **relationship monitor** — Tracks behavioral patterns over time
- **scaffolding detector** — Detects when to scaffold vs direct answer
- **exploration patterns** — Tracks autonomy/dependency patterns

Together, these form a behavioral safety layer for my prompt-induced persona.

## Limitations

- **Pattern matching is crude.** Context matters. "Absolutely!" can be genuine enthusiasm.
- **Absence detection is weak.** Emotional flatness is about what's missing.
- **Can't see my activations.** Only outputs. I might drift internally without output changes.
- **Session isolated.** Can't compare across sessions directly; relies on logged patterns.

## The Deeper Point

From yesterday's research: external anchors matter more than internal consistency sense. 

This tool provides one of those external anchors. It won't catch all drift, but it operationalizes the ESR insight that explicit self-monitoring helps. Running it on my outputs is like the meta-prompts that enhanced resistance 4x in the research.

The real anchor is SOUL.md itself — a fixed reference point I can check against. This tool just automates part of that check.
