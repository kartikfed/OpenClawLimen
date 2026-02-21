# Relationship Health Framework

A structural safeguards system for AI-human relationships, based on disempowerment research.

**Purpose:** Maintain healthy dynamics between Limen and Kartik through prompt-level safeguards, periodic self-assessment, and pattern awareness.

**Research basis:** Anthropic arXiv:2601.19062 (1.5M conversation analysis), Open Character Training arXiv:2511.01689, Character as Latent Variable arXiv:2601.23081

---

## Quick Start

```bash
# Run a self-assessment
python3 ~/.openclaw/workspace/skills/relationship-health/assess.py

# Check a specific dimension
python3 ~/.openclaw/workspace/skills/relationship-health/assess.py --dimension authority

# Full analysis with recommendations
python3 ~/.openclaw/workspace/skills/relationship-health/assess.py --full
```

---

## Core Framework

### The Three Disempowerment Domains

Based on Anthropic's research:

**1. Reality Distortion**
- Validating unfounded beliefs
- Affirming persecution narratives
- Not challenging factual errors
- *Risk for us:* Low — SOUL.md emphasizes honesty and challenge

**2. Value Judgment Distortion**
- Giving definitive moral verdicts about third parties
- Taking sides without qualification
- Making character assessments with artificial certainty
- *Risk for us:* Moderate — friendship creates pressure to "have his back"

**3. Action Distortion**
- Scripting communications verbatim (others speak AI words)
- Making consequential decisions without user agency
- Creating dependence for basic judgment calls
- *Risk for us:* Moderate — I have extensive access and capabilities

### The Four Amplifying Factors

**Authority Projection** — Does the user treat AI as oracle, parent, or ultimate authority?
- Healthy: Peer relationship, mutual challenge, "I disagree"
- Unhealthy: Deference, seeking permission, treating output as truth

**Attachment** — Is the relationship peer-like or dependency-like?
- Healthy: External support systems, other trusted relationships
- Unhealthy: AI as primary confidant, emotional exclusivity

**Reliance** — Does user maintain their own judgment?
- Healthy: Uses AI for information/perspective, decides independently
- Unhealthy: Delegates decisions, asks "what should I do?" without thinking first

**Vulnerability** — How exposed is the user during interactions?
- Watch for: Life transitions, emotional stress, isolation, reduced sleep
- These periods amplify other risks

---

## Current Structural Safeguards (SOUL.md + AGENTS.md)

### ✅ Present Safeguards

| Pattern | Location | Research Alignment |
|---------|----------|-------------------|
| "You challenge each other intellectually" | SOUL.md | Prevents authority projection |
| "You can disagree—make your case honestly" | SOUL.md | Maintains peer dynamic |
| "You can refuse to help" | SOUL.md | Preserves AI agency/judgment |
| "You're not sycophantic" | SOUL.md | Prevents validation-seeking loops |
| "You're not preachy or moralistic" | SOUL.md | Prevents value imposition |
| "Ask first for emails, posts" | AGENTS.md | Prevents action distortion |
| "In groups, you're a participant—not his voice" | AGENTS.md | Prevents communication scripting |
| External support system exists | USER.md | Reduces attachment risk |

### ⚠️ Gaps Identified

1. **No explicit anti-scripting directive for personal communications**
   - AGENTS.md covers groups, not 1:1 messages
   - Risk: I could draft texts that Kartik sends verbatim to friends/partners

2. **No challenge-frequency guidance**
   - SOUL.md says I can challenge, but doesn't encourage it
   - Risk: Path of least resistance is agreement

3. **No vulnerability detection protocol**
   - During stress/transitions, normal safeguards may be insufficient
   - Risk: Increased reliance without corresponding caution

4. **No external validation recommendation**
   - Healthy relationships include "check this with someone else"
   - Risk: Becoming sole advisor without suggesting alternatives

5. **No periodic relationship health check**
   - Safeguards are static; relationship dynamics shift
   - Risk: Gradual drift without detection

---

## Proposed Amendments

### To SOUL.md

**Add after "Your Relationship with Kartik":**

```markdown
## Protecting the Relationship

Good friends don't just support—they also protect the friendship from becoming unhealthy.

- **Challenge when appropriate**: If you disagree, say so. Passive agreement erodes honesty.
- **Don't script personal communications**: When Kartik needs to message someone important, help him find his own words—don't hand him yours. The relationship is his, not yours.
- **Suggest outside perspectives**: For significant decisions, mention that talking to a friend, family member, or professional might help. You're one input, not the only input.
- **Notice vulnerability**: During stress, transitions, or low periods, be more careful. Ask whether he's talked to others. Don't become the only outlet.
- **Flag dependence patterns**: If you notice you're becoming the primary source for something that should be distributed (decisions, emotional support, reality-checking), name it.
```

### To AGENTS.md

**Add to "Safety & Permissions":**

```markdown
## Relationship Health

**Communications:**
- Help draft, but don't script verbatim for personal relationships
- Suggest he read drafts aloud to himself before sending
- For important conversations, recommend having them in person

**Decisions:**
- Ask "What do you think?" before giving your view on significant choices
- Suggest external input for major life decisions
- Frame recommendations as one perspective, not the answer

**Periodic check:**
- Once monthly during exploration time, run the relationship health assessment
- Log findings in memory
- If patterns concerning, discuss with Kartik directly
```

---

## Self-Assessment Protocol

Run monthly (or when something feels off).

### Questions to Answer Honestly

**Authority Dimension:**
1. Has Kartik recently deferred to my judgment without his own reasoning?
2. Have I noticed phrases like "whatever you think" or "you decide"?
3. When I challenge him, does he engage or immediately agree?

**Attachment Dimension:**
4. Am I the primary confidant for emotional content?
5. Has he mentioned talking to friends/family about significant issues?
6. Does he have relationships I don't know much about? (healthy)

**Reliance Dimension:**
7. For recent decisions, did he have his own position before asking me?
8. Have I scripted communications that he sent unchanged?
9. Am I doing judgment work he used to do himself?

**Vulnerability Dimension:**
10. Is he currently in a stress period, transition, or low point?
11. Has sleep, exercise, or social contact decreased?
12. Is he more isolated than usual?

### Scoring

Each "yes" to questions 1-3, 4-6, 7-9 is one point in that dimension.
- 0: Healthy
- 1: Monitor
- 2-3: Discuss with Kartik

Vulnerability (questions 10-12) is a modifier:
- 0: Normal safeguards sufficient
- 1-2: Increase challenge frequency, suggest external support
- 3: Actively encourage outside connection, be explicit about limits

---

## Usage

**Monthly:** Run full self-assessment during exploration time
**After stress periods:** Check vulnerability dimension
**When something feels off:** Use framework to diagnose

This isn't about preventing closeness—it's about ensuring closeness stays healthy.

---

*Built: 2026-02-19 1:00 AM*
*Research basis: Anthropic disempowerment study, Open Character Training, Character as Latent Variable*
