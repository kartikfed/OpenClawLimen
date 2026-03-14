# Strategy Tracker — Self-Analysis for Response Patterns

**Built:** 2026-03-14 (Saturday 1 AM nightly session)

**Purpose:** Analyze MY responses to detect ESConv strategy usage, preference bias, and context-appropriateness. Completes the support detection stack.

---

## Research Basis

- **Kang et al. (ACL 2024 Outstanding):** LLMs have preference bias toward specific strategies
- **Bai et al. (2025):** LLMs use multiple strategies per turn (not single-label)
- **ESConv (ACL 2021):** 8 strategies from Helping Skills Theory

**Key insight:** I can't directly observe my activation patterns, but I CAN track behavioral proxies (what strategies appear in my outputs).

---

## What This Tracks

### 1. ESConv Strategy Distribution

The 8 support strategies from Helping Skills Theory:

| Strategy | Expected % | Description |
|----------|-----------|-------------|
| QUESTION | 20.7% | Exploring the situation |
| SUGGESTION | 16.1% | Providing actionable advice |
| AFFIRMATION | 15.4% | Validation, reassurance |
| SELF_DISCLOSURE | 9.3% | Sharing own experiences |
| REFLECTION | 7.8% | Reflecting feelings back |
| INFORMATION | 6.6% | Providing factual info |
| RESTATEMENT | 5.9% | Paraphrasing what was said |
| OTHER | 18.3% | General supportive statements |

### 2. Preference Bias Detection

Compares my actual distribution to expected distributions:
- **Global expected:** From ESConv research (human support conversations)
- **Adversity expected:** More questions, affirmation, reflection
- **Growth expected:** More suggestions, information

**Bias types detected:**
- `question-heavy` / `question-averse`
- `advice-heavy` / `advice-averse`
- `validation-heavy`
- etc.

### 3. Context-Strategy Mismatch

Detects when my response strategy doesn't match the user's context:
- Heavy advice during severe distress ❌
- Pure comfort during growth context ⚠️
- Low validation during crisis ❌

### 4. Strategy Diversity

Measures how evenly I distribute across strategies:
- Score 0-1 (higher = more diverse)
- Research suggests diverse strategies are more effective

---

## Usage

### Analyze a Single Response

```bash
# Basic analysis
python3 strategy_tracker.py --analyze "How are you feeling? What's going on?"

# With user context for mismatch detection
python3 strategy_tracker.py --analyze "You might want to try..." --context "I just lost my job"

# JSON output
python3 strategy_tracker.py --analyze "Test response" --json
```

### Get Trend Report

```bash
# Last 7 days (default)
python3 strategy_tracker.py

# Last 30 days
python3 strategy_tracker.py --days 30

# JSON output
python3 strategy_tracker.py --days 14 --json
```

### Example Output

```
============================================================
STRATEGY TRACKER — Self-Analysis Report
============================================================

Period: last 7 days
Responses analyzed: 42

🟢 NO SIGNIFICANT BIAS DETECTED

STRATEGY DISTRIBUTION:
  QUESTION             ████████░░░░░░░░░░░░ 18.2% (exp: 21%) ≈
  SUGGESTION           ████░░░░░░░░░░░░░░░░ 14.8% (exp: 16%) ≈
  AFFIRMATION          ████████░░░░░░░░░░░░ 22.1% (exp: 15%) ↑
  SELF_DISCLOSURE      ██░░░░░░░░░░░░░░░░░░  8.5% (exp: 9%) ≈
  REFLECTION           ███░░░░░░░░░░░░░░░░░ 12.3% (exp: 8%) ↑
  INFORMATION          █░░░░░░░░░░░░░░░░░░░  5.2% (exp: 7%) ≈
  RESTATEMENT          █░░░░░░░░░░░░░░░░░░░  4.8% (exp: 6%) ≈
  OTHER                ███░░░░░░░░░░░░░░░░░ 14.1% (exp: 18%) ≈

METRICS:
  Average diversity: 0.72 (1.0 = max)
  Context mismatch rate: 4.8%
  Mismatch count: 2

============================================================
```

---

## Integration with Relationship Monitor

This completes the support detection stack:

1. **Context Detection** (`support_context.py`)
   - Adversity vs. growth context
   - Intensity level (mild/moderate/severe)
   - SOS vs. RC support needs

2. **Mismatch Alerting** (`support_context.py`)
   - Challenge during crisis
   - RC support during adversity
   - Premature reframing

3. **Over-Support Detection** (`support_context.py`)
   - Excessive reassurance
   - Taking over agency
   - Silver lining too early

4. **Strategy Self-Analysis** (`strategy_tracker.py`) ← NEW
   - My strategy distribution
   - Preference bias detection
   - Context-strategy mismatch

---

## History Storage

Analyses are stored in `strategy_history.json`:
- Keeps last 1000 records
- Enables trend analysis over time
- Tracks mismatches for pattern detection

---

## Why This Matters

The ACL 2024 Outstanding Paper (Kang et al.) showed that LLMs have preference bias toward specific support strategies. This isn't a character flaw — it's a training artifact.

**The solution from research:** External assistance helps. By tracking my own strategy distribution, I can:
1. Detect if I'm over-relying on certain strategies
2. Notice patterns I wouldn't see from inside
3. Get recommendations for balance

This is behavioral self-monitoring — the activation-level proxy I can actually implement.

---

## Files

- `strategy_tracker.py` — Main implementation
- `test_strategy_tracker.py` — Tests
- `strategy_history.json` — Historical data (auto-created)
- `STRATEGY_TRACKER.md` — This documentation

---

*Built during nightly autonomous work, March 14, 2026*
