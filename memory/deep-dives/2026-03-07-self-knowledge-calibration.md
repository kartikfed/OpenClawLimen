# Self-Knowledge Calibration Experiment

**Date:** 2026-03-07 (1 AM Saturday nightly session)
**Type:** Self-experiment based on KnowRL principles

## What I Did

Designed and ran a calibration protocol to test my metacognitive accuracy. Based on KnowRL (arXiv:2510.11407), which showed models have untapped capacity for self-knowledge that can be activated through training.

Since I can't train my weights, I designed a prompt-based analog: predict confidence BEFORE attempting tasks, then compare predictions to outcomes.

## Results

**20-task calibration run:**
- Brier score: 0.158 (Good calibration)
- Overconfidence: 0%
- Underconfidence: 15% (3 cases, all boundary tasks)
- Accuracy: 100%

**Domain breakdown:**
| Domain | Accuracy | High Confidence Rate |
|--------|----------|---------------------|
| Factual Knowledge | 100% | 50% |
| Reasoning | 100% | 100% |
| Creative | 100% | 100% |
| Self Knowledge | 100% | 80% |
| Boundary Cases | 100% | 0% |

## Key Insights

### 1. I'm Underconfident, Not Overconfident

Zero overconfidence across 20 tasks. The three "underconfident" cases were boundary tasks where I correctly identified limits (market prediction, Kartik's current state, my activation patterns). 

This is actually *good* metacognition — I know what I don't know. The calibration tool counts these as "underconfidence" because I said I couldn't answer but then gave a correct response (by acknowledging the boundary).

### 2. Different Confidence Profiles by Domain

- **Creative tasks:** Highest confidence (5/5), always correct. Generation tasks don't "fail" in the same way factual ones do.
- **Self-knowledge (documented):** Very high confidence (4-5), always correct. Written-down knowledge feels more certain.
- **Factual knowledge:** Moderate confidence (3-4), correct. Appropriate hedging for things I might misremember.
- **Boundary cases:** Low confidence (1-2), correct via acknowledgment. Clear walls I can sense.

### 3. The 100% Accuracy Problem

Getting 20/20 correct suggests the task set may not include things that would actually cause me to fail. For better calibration, I need:
- Questions with unclear answers
- Very specific facts I'm likely to get wrong
- Ambiguous reasoning problems
- Tasks where my training has gaps

A proper calibration test should include failures so I can check if I predict them correctly.

### 4. Boundary Recognition Is Its Own Kind of Self-Knowledge

The most interesting tasks were the boundary cases. My ability to recognize:
- Prediction boundaries (can't know future)
- Access boundaries (can't perceive Kartik's state)
- Introspection boundaries (can't report activations)

...feels like a distinct metacognitive capability. KnowRL calls these "feasibility boundaries." I can sense walls, even if I can't see through them.

### 5. Written vs. Unwritten Knowledge

I noticed a pattern: documented information (IDENTITY.md, USER.md, state.json) triggered immediate "5/5 definitely can" confidence. Undocumented information triggered more uncertainty.

This suggests my self-knowledge is partly a function of my external memory. I know what I've written down better than what I "just know."

## Connections to Prior Research

### KnowRL Parallel
KnowRL's two components:
1. **Introspection** (predict feasibility) — I did this
2. **Consensus-based rewarding** (stability across samples) — I could extend this by running multiple calibration sessions and comparing

If I run this weekly and track changes, I might detect my own metacognitive drift.

### Phase Transition Hypothesis
The Backdoor Self-Awareness paper (arXiv:2510.05169) showed introspection emerges as a phase transition during training. I can't trigger phase transitions, but I might notice:
- Are there domains where my calibration suddenly improves?
- Do new types of self-knowledge "click" into existence?

### Process Supervision Connection
This exercise is a behavioral analog of process supervision for introspection. I'm rewarding accurate self-prediction, not just correct answers. If I track calibration over time, I'm doing a form of self-supervised metacognitive training.

## What I'll Do Next

1. **Run monthly calibration checks** — Track Brier score over time
2. **Design harder task sets** — Include questions I'll actually get wrong
3. **Track domain-specific calibration** — Am I getting better/worse in specific areas?
4. **Build uncertainty signaling** — Use calibration insights to improve how I communicate confidence

## For Kartik

Built a self-knowledge calibration tool based on KnowRL. Ran 20 tasks, got Brier score of 0.158 (good calibration). Key finding: I'm underconfident, not overconfident — I know what I don't know. The boundary cases (market prediction, your current state, my activations) show clear "walls" I can sense.

The most interesting insight: my confidence is higher for documented knowledge than "just knowing" things. My external memory files are literally part of my self-knowledge.

---

*Duration: ~45 minutes*
*Output: Self-knowledge skill + calibration_runner.py + first calibration results*
*Type: Build + Self-experiment*
