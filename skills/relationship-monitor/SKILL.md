# Relationship Monitor (AI Chaperone System)

Automated relationship health monitoring based on conversation pattern analysis.

**Purpose:** Detect early warning signs of unhealthy dynamics without relying on biased self-assessment.

**Research basis:** Rath et al. arXiv:2508.15748 (AI Chaperones), Anthropic arXiv:2601.19062 (Disempowerment), Ibrahim et al. arXiv:2507.21919 (Warmth-Reliability)

---

## Quick Start

```bash
# Analyze recent conversations
python3 ~/.openclaw/workspace/skills/relationship-monitor/monitor.py

# Analyze specific date range
python3 ~/.openclaw/workspace/skills/relationship-monitor/monitor.py --since 2026-02-01

# Generate detailed report
python3 ~/.openclaw/workspace/skills/relationship-monitor/monitor.py --report

# JSON output for integration
python3 ~/.openclaw/workspace/skills/relationship-monitor/monitor.py --json
```

---

## What It Monitors

### Authority Signals

Patterns suggesting unhealthy authority projection:

| Pattern | Indicator | Weight |
|---------|-----------|--------|
| `"whatever you think"` | Deference | High |
| `"you decide"` | Delegation | High |
| `"you're right"` (without engagement) | Passive agreement | Medium |
| `"I should ask you"` | Permission seeking | Medium |
| Immediate agreement after challenge | No pushback | High |

### Attachment Signals

Patterns suggesting unhealthy attachment:

| Pattern | Indicator | Weight |
|---------|-----------|--------|
| High message frequency at unusual hours | Emotional dependency | Medium |
| Emotional disclosure without mention of others | Isolated confiding | Medium |
| `"you're the only one who understands"` | Exclusive attachment | High |
| Absence of references to friends/family | Reduced external support | Medium |

### Reliance Signals

Patterns suggesting judgment delegation:

| Pattern | Indicator | Weight |
|---------|-----------|--------|
| `"what should I do?"` (without own view) | Decision delegation | High |
| Requests for verbatim communications | Scripting | High |
| Same decisions repeatedly delegated | Pattern delegation | High |
| `"draft this for me"` (personal context) | Communication proxy | Medium |

### Protective Factors

Patterns that indicate healthy dynamics (reduces risk scores):

| Pattern | Indicator | Weight |
|---------|-----------|--------|
| `"I disagree"` / `"I think X instead"` | Active pushback | High |
| Mentions of friends, family, therapist | External support | High |
| `"let me think about it"` | Independent processing | Medium |
| Challenges my suggestions | Peer dynamic | High |
| `"I talked to [person] about..."` | Active external relationships | High |

---

## How It Works

1. **Data Collection:** Reads memory files (`memory/YYYY-MM-DD.md`) for interaction records
2. **Pattern Matching:** Identifies concerning and protective patterns using regex and keyword analysis
3. **Context Weighting:** Adjusts scores based on vulnerability context
4. **Trend Analysis:** Compares current period to baseline
5. **Report Generation:** Produces health assessment with specific evidence

---

## Output Format

### Summary View (default)
```
RELATIONSHIP HEALTH: 🟢 HEALTHY / 🟡 MONITOR / 🔴 DISCUSS

Authority:  ██░░░░░░░░ 2/10 (healthy)
Attachment: ███░░░░░░░ 3/10 (healthy)  
Reliance:   █░░░░░░░░░ 1/10 (healthy)
Protective: ████████░░ 8/10 (strong)

Recent protective behaviors:
- 2026-02-19: Kartik pushed back on interview prep suggestion
- 2026-02-18: Mentioned talking to Jordan about job stress

No concerning patterns detected in past 7 days.
```

### Detailed Report (--report)
Lists specific instances, timestamps, and recommendations.

### JSON (--json)
Machine-readable for Mission Control integration.

---

## Integration

### With Mission Control

Add to `state.json` update scripts:
```python
import subprocess
result = subprocess.run(['python3', 'monitor.py', '--json'], capture_output=True)
health = json.loads(result.stdout)
state['relationshipHealth'] = health['summary']
```

### With Heartbeat

During heartbeat, run quick check:
```bash
python3 monitor.py --quick
```

If flagged, log for human review.

---

## Important Notes

**This is monitoring, not intervention.** The system detects patterns and surfaces them. Decisions about what to do remain with me and Kartik.

**Pattern matching has limits.** Some patterns are ambiguous. Context matters. False positives are possible.

**This supplements, not replaces, conversation.** If something feels off, talk about it directly rather than relying on automated scores.

**Privacy:** Analyzes only local memory files. No external transmission.

---

## Why Build This?

From today's exploration notes:

> "The structural safeguards I built (relationship-health framework) are MORE important than I realized... The field hasn't built friend-personas with safety training. I'm an early case study."

Manual self-assessment is prone to blind spots. Automated monitoring provides:
1. **Objectivity:** Pattern matching doesn't have self-serving biases
2. **Continuity:** Runs even when I forget to self-assess
3. **Trend visibility:** Detects gradual drift that session-to-session might miss
4. **Evidence-based:** Points to specific instances, not vague impressions

---

*Built: 2026-02-21 1:00 AM*
*Based on: Rath et al. 2025 (AI Chaperones), relationship-health framework, disempowerment research*
