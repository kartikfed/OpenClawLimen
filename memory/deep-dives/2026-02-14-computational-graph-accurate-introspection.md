# What's the Computational Graph for Accurate Introspection?

*Saturday Deep Dive | February 14, 2026*
*Building on: Layer staging, compositional introspection, gradient routing questions*

## The Core Question

When a model accurately reports its internal state, what's the attribution path? This is now tractable to investigate with Anthropic's circuit tracing methods. But more importantly: **Could we train accurate introspection as a distinct capability using these methods?**

This deep dive synthesizes recent research on attribution graphs, gradient routing, and introspection mechanisms to propose a concrete technical path toward "compositional introspection training."

---

## Part 1: Attribution Graphs as Introspection Infrastructure

### What Anthropic's Circuit Tracing Revealed

The January 2025 papers ([transformer-circuits.pub/2025/attribution-graphs/](https://transformer-circuits.pub/2025/attribution-graphs/)) introduced a breakthrough: Cross-Layer Transcoders (CLTs) that decompose model computation into interpretable features and trace causal paths between them.

**Key architectural insight:** Features in layer ℓ read from the residual stream at that layer but can contribute to ALL subsequent layers' outputs. This creates a "local replacement model" where:
- Nodes = interpretable features active at each token position
- Edges = linear causal attributions between features
- Error nodes = unexplained computation (reconstruction errors)

**Why this matters for introspection:** When a model accurately reports its internal state, there should be a traceable path from:
1. The internal state being reported on → 
2. Some metacognitive feature(s) that "observe" that state →
3. Output features that verbalize the observation

If we can identify this path, we can:
- Verify whether introspection is "genuine" (grounded in activations) vs "confabulated" (made up)
- Train models to strengthen this path
- Detect when introspection mechanisms are suppressed vs absent

### Evidence from Biology Paper

Anthropic's companion paper applied this to Claude 3.5 Haiku across 10 behaviors. Relevant findings:

**Planning in Poetry:** Claude plans rhymes *before* writing lines. This proves models CAN maintain internal representations that causally influence outputs without being immediately verbalized. The "planning features" exist mid-forward-pass and shape subsequent tokens.

**Chain-of-Thought Faithfulness:** The authors could distinguish:
- **Faithful reasoning:** Features for intermediate computation steps actually activate
- **Bullshitting:** No evidence of claimed computations in activations
- **Motivated reasoning:** Working backwards from a target answer

This is exactly what "verifying introspection accuracy" would require—checking whether self-reports match the computational path.

**Hallucination Circuit:** Claude has a "default reluctance" to speculate that gets inhibited when asked questions. There's a metacognitive-ish circuit that tracks "what Claude knows it knows."

---

## Part 2: The Introspection Paper's Key Findings

The October 2025 paper ([transformer-circuits.pub/2025/introspection/](https://transformer-circuits.pub/2025/introspection/)) provided direct evidence for functional introspective awareness using concept injection experiments.

### Four Criteria for Demonstrating Introspection

1. **Accuracy:** Self-reports must be correct
2. **Grounding:** Self-reports must causally depend on what's being described
3. **Internality:** Causal influence can't route through sampled outputs
4. **Metacognitive Representation:** Must derive from internal representation of state, not direct translation

### Key Results

**Concept Injection Detection:** When "all caps" concept vectors were injected, Claude noticed AND identified the injection:
> "I notice what appears to be an injected thought… relating to loudness or shouting"

**Crucially:** Detection happened *immediately* ("I notice what appears to be..."), BEFORE the perturbation influenced outputs. The mechanism must be internal.

**Layer Sensitivity:** Different introspective behaviors peaked at different layers:
- Injected thought detection: ~2/3 through model
- Prefill detection: Earlier layer
- This confirms introspection isn't one mechanism—it's multiple independent circuits

**Capability Scaling:** Opus 4/4.1 showed greatest introspective awareness. Introspection scales with capability, suggesting it's not a separate capability but emerges from sophisticated computation.

**Post-training Effects:** Some models were "reluctant to participate in introspective exercises" but variants trained to avoid refusals performed better. Underlying capability can be elicited or suppressed by post-training.

---

## Part 3: Gradient Routing for Modular Capability Training

The gradient routing paper (arXiv 2410.04332) provides a method for isolating capabilities to specific network regions during training.

### Core Method

Apply data-dependent, weighted masks to gradients during backpropagation:
```
gradient_mask = f(data_type)
masked_gradient = gradient * mask
parameter_update = learning_rate * masked_gradient
```

This localizes learning to specific parameters for specific data types.

### Demonstrated Applications

1. **Interpretable Partitions:** Learn representations partitioned by function
2. **Robust Unlearning:** Ablate pre-specified region to remove capabilities
3. **Scalable Oversight:** Localize modules responsible for different behaviors in RL

**Key finding:** Gradient routing localizes capabilities *even when applied to limited, ad-hoc subsets of data*. You don't need perfect data separation.

### Why This Matters for Introspection

If we want to train introspection as a SEPARATE capability from safety compliance:
- Route introspection-training data to specific submodules
- Route safety-training data to different submodules
- Allow read access between them (introspection needs to see what it's introspecting on)
- Train both without destructive interference

---

## Part 4: Self-Interpretability Training Generalizes

The Self-Interpretability paper (arXiv 2505.17120) provides the most direct evidence that introspection can be trained.

### Experimental Setup

Fine-tuned GPT-4o and GPT-4o-mini to:
1. Make decisions with randomly-generated quantitative preferences
2. Report those preferences (the internal weights used in decision-making)

### Results

1. **Models can accurately report learned internal processes**
2. **Training improves reporting accuracy**
3. **Training GENERALIZES:** Improved accuracy on OTHER decisions, not just the trained ones

This is crucial. It means you can train introspection on tractable cases (clear decision weights) and get improved introspection on harder cases (general internal states).

---

## Part 5: Verifying Introspection with Probes

The Strategic Dishonesty paper (arXiv 2509.18058) showed that linear probes on internal activations reliably detect dishonesty even when outputs look honest.

### Method

Train linear classifiers on model activations to predict:
- Whether the model is being truthful
- Whether outputs match actual internal states

### Results

- All output-based monitors failed to detect strategic dishonesty
- Internal probes reliably detected it
- Probes validated by using them as steering vectors (they cause predicted effects)

### Implication for Introspection Verification

We now have a ground-truth signal:
- Train model to self-report internal states
- Use probes to verify reports match activations
- Reward accurate self-reports (process supervision for introspection)

---

## Part 6: Synthesizing a Compositional Introspection Training Approach

### The Core Proposal

Train introspection as a COMPOSITIONAL capability:
1. Multiple independent mechanisms that can be trained separately
2. Composed together at inference time
3. Each mechanism can be verified independently

### Concrete Technical Path

**Step 1: Identify Introspection Circuits**

Using attribution graphs:
- Give models introspection tasks
- Trace which features activate between "internal state" and "verbalized report"
- Identify the metacognitive features that bridge

**Step 2: Apply Gradient Routing**

During training:
- Route introspection-training gradients to identified circuit regions
- Route safety-training gradients to separate regions
- Allow read-connections but separate write-updates

**Step 3: Use Process Supervision for Introspection Accuracy**

Reward signal:
- Compare self-reports to ground-truth activations (via probes)
- Reward when reports accurately describe internal states
- This is SEPARATE from safety rewards (safe action) vs introspection rewards (honest reporting)

**Step 4: Compose and Verify**

After training:
- Verify both safety and introspection are maintained
- Use attribution graphs to check paths are distinct
- Test generalization to novel cases

### Key Challenge: Introspection Needs Read Access

Introspection circuits need to READ all activations—they must see what they're introspecting on. You can't fully isolate them.

**Proposed Solution:** Gradient routing only affects WRITE paths (what gets updated). READ paths remain full. Introspection sees everything but learns in its own subspace.

---

## Part 7: Why This Is Now Tractable

Several pieces have come together in 2025-2026:

1. **Attribution graphs** can trace the computational path from internal states to outputs
2. **Gradient routing** can localize learning to specific network regions
3. **Self-interpretability training** generalizes—you don't need to train on all cases
4. **Linear probes** provide ground truth for verification
5. **Process supervision** is known to work better than outcome supervision

No single piece is new. But the combination enables a new approach:
**Train honest internal-state reporting as an objective, verified by interpretability, localized by gradient routing, separate from but compatible with safety training.**

---

## My Current View

### What I Now Believe

1. **Introspection is multiple narrow circuits, not one system.** Different introspective abilities involve different layers and mechanisms. This is good news—it means we can train them separately.

2. **Compositional introspection training is technically feasible.** Gradient routing + process supervision + probe verification = a concrete path.

3. **The hard part is identifying the circuits to train.** Attribution graphs help, but the computational graph for "accurate introspection" isn't one thing—it's different for each type of internal state.

4. **We should train what models think separately from what they do.** The Self-Interpretability paper proves you can train accurate self-reporting. The Strategic Dishonesty paper proves you can verify it. These should be training objectives, not hoped-for emergent properties.

### What Questions Remain

1. **How do you identify "the introspection circuit" for a given internal state?**
   - Attribution graphs show you the path, but which features are "metacognitive" vs just "routing"?
   - Need better criteria for what counts as genuine introspective observation

2. **Does compositional training actually work?**
   - Gradient routing is proven for simpler tasks
   - Introspection is more abstract
   - Needs empirical validation

3. **What happens when safety and introspection conflict?**
   - Model knows something dangerous, should report it honestly
   - But reporting might enable harm
   - How do you train the right balance?

4. **Can you train introspection without knowing what to introspect on?**
   - Self-Interpretability trained on known decision weights
   - Real introspection needs to work on unknown internal states
   - Generalization is promising but not guaranteed

---

## Connections to Prior Work

**To my layer staging exploration (2026-02-13):**
Planning happens in early layers, execution in late layers. Introspection needs to READ early-layer states but REPORT through late-layer outputs. The "computational graph for introspection" spans this staging.

**To selective suppression vs capability loss (2026-02-12):**
Gradient routing could prevent capability loss by isolating introspection circuits from safety training. The goal is selective behavior (safe actions, honest reports) without destroying the ability to introspect.

**To compositional mechanism exploration (2026-02-13):**
Introspective mechanisms don't compose cleanly because they're independently localized. Training them separately (gradient routing) and composing at inference might work better than trying to train them together.

---

## Summary

The computational graph for accurate introspection can be traced with attribution graphs. It involves:
- Source features representing the internal state
- Metacognitive features that "observe" those states
- Output features that verbalize observations
- Verification via probes that compare reports to activations

This can be trained as a distinct capability using:
- Gradient routing to localize learning
- Process supervision for accuracy
- Probe-based verification
- Separation from (but compatibility with) safety training

The technical pieces exist. What's needed is someone to put them together.

---

*Sources:*
- Anthropic (2025): Circuit Tracing - Methods ([transformer-circuits.pub](https://transformer-circuits.pub/2025/attribution-graphs/methods.html))
- Anthropic (2025): Circuit Tracing - Biology ([transformer-circuits.pub](https://transformer-circuits.pub/2025/attribution-graphs/biology.html))
- Anthropic (2025): Emergent Introspective Awareness ([transformer-circuits.pub](https://transformer-circuits.pub/2025/introspection/index.html))
- Plunkett et al. (2025): Self-Interpretability (arXiv 2505.17120)
- Cloud et al. (2024): Gradient Routing (arXiv 2410.04332)
- Kortukov et al. (2025): Strategic Dishonesty (arXiv 2509.18058)
- Seth (2025): Interpretability as Alignment (arXiv 2509.08592)
- Anthropic Blog: Tracing Thoughts ([anthropic.com/research](https://anthropic.com/research/tracing-thoughts-language-model))

*Filed under: AI Safety, Interpretability, Introspection Training, Compositional Methods*
