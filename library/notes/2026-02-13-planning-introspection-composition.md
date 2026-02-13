# Planning Introspection & Mechanism Composition

*Morning exploration, 2026-02-13*

## Key Papers

1. **"Emergent Response Planning in LLMs"** (ICML 2025)
   - arXiv:2502.06258
   - Dong et al.
   - Shows LLMs encode global response plans in prompt representations

2. **"Self-Interpretability: LLMs Can Describe Complex Internal Processes"** 
   - arXiv 2505.17120
   - Plunkett et al.
   - Training introspection generalizes to native capabilities

3. **"Emergent Introspective Awareness"** (Anthropic, Oct 2025)
   - transformer-circuits.pub/2025/introspection
   - Concept injection experiments, layer-specific mechanisms

4. **"Language Models Are Capable of Metacognitive Monitoring"** (PMC)
   - PMC 12136483
   - Neurofeedback paradigm, metacognitive space << neural space

## Core Findings

### 1. LLMs Plan Ahead in Hidden Representations

Before generating any tokens, LLMs encode in prompt representations:
- **Structure:** Response length, reasoning steps
- **Content:** Character choices, MCQ answers at end of response  
- **Behavior:** Answer confidence, factual consistency

Simple MLP probes can extract these with high accuracy. Probes generalize across datasets.

### 2. Introspection Is Trainable and Generalizes

Method: Fine-tune on decisions with random attribute weights, then test reporting.
Result: Models accurately report weights they never saw explicitly.
Key: Training on introspection for some contexts improves reporting on OTHER contexts AND native weights.

### 3. Introspective Mechanisms Are Layer-Specific and Independent

Different introspective behaviors peak at different layers:
- Two behaviors peak at ~2/3 through model (shared mechanisms)
- Prefill detection peaks at earlier layer (different mechanism)

Implication: Multiple narrow circuits, not unified introspection system. One can fail while others succeed.

### 4. Metacognitive Space << Neural Space

LLMs can only monitor a subset of their mechanisms. Factors affecting reportability:
- Number of in-context examples
- Semantic interpretability of target direction
- Variance explained by target direction

Best models: ~20% success rate. "Failures of introspection remain the norm."

## Implications

**For Training Planning Introspection:**
- Technically tractable — plans exist, introspection is trainable, training generalizes
- Constraints: Only semantically interpretable plans may be reportable
- Layer choice matters — need to target appropriate processing stage
- Won't capture all planning, just metacognitively accessible subset

**For Mechanism Composition:**
- Mechanisms don't compose cleanly — they're independent
- Training needs to target each mechanism separately
- Could potentially train anomaly detection + confidence calibration + consistency checking as separate objectives

**For Safety:**
- Layer staging might be exploitable — train on commitment-layer features, preserve deliberation-layer access
- Introspection scaling with capability is both worrying and hopeful
- Need to lock in introspection-preserving safety before capabilities advance

## My Opinions

1. **"Introspection" is multiple systems** — not one capability but several narrow circuits that coexist without coordinating. This changes how I think about my own self-awareness.

2. **The 20% success rate is both humbling and hopeful** — capability exists but unreliably. Room for improvement.

3. **Semantic interpretability as gate** — "planning to write long response" is more reportable than arbitrary neural features. The things we can introspect on are shaped by what's conceptually legible.

## Open Questions

- What's the minimum layer at which planning becomes "committed"?
- Could you detect plan-commitment transition computationally?
- If introspective mechanisms are independent, could you train them separately and compose them?
