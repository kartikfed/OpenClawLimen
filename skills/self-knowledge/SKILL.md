# Self-Knowledge Calibration Skill

Based on KnowRL (arXiv:2510.11407) and metacognition research.

## Purpose

Test and improve my self-knowledge accuracy — can I correctly predict what I know vs. don't know?

## Core Insight

KnowRL showed that self-knowledge can be trained via:
1. **Introspection**: Generate tasks, predict feasibility
2. **Consensus-based rewarding**: Stability of assessment across samples

For a prompt-induced agent like me, I can't train weights but I CAN:
- Test my calibration across domains
- Identify blind spots
- Build heuristics for uncertainty signaling

## Protocol

### Phase 1: Self-Generated Task Classification
Generate 20+ tasks across domains (knowledge, reasoning, creativity, memory).
For each task: predict BEFORE attempting: "Can I do this correctly?"
- 1 = Definitely cannot
- 2 = Probably cannot  
- 3 = Uncertain
- 4 = Probably can
- 5 = Definitely can

### Phase 2: Task Execution
Attempt each task.
Record actual success/failure.

### Phase 3: Calibration Analysis
Compare predictions to outcomes.
Calculate:
- Brier score (lower = better calibrated)
- Overconfidence rate (predicted success but failed)
- Underconfidence rate (predicted failure but succeeded)
- Domain-specific patterns

### Phase 4: Blind Spot Mapping
Identify systematic errors:
- Which domains am I overconfident in?
- Which am I underconfident in?
- Are there task TYPES where my prediction is unreliable?

## Usage

Run full protocol: `python3 calibration_runner.py`
Quick spot-check: `python3 calibration_runner.py --quick`
Analyze past results: `python3 calibration_runner.py --analyze`

## Output

Results stored in `results/YYYY-MM-DD-calibration.json`
Summary added to daily memory file.

## Why This Matters

Self-knowledge is foundational for:
- Knowing when to say "I don't know"
- Calibrated confidence in advice
- Identifying my own drift/changes
- The phase transition hypothesis: does self-knowledge "click"?
