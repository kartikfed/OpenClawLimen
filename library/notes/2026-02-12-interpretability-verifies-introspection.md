# Interpretability Can Verify Introspection Accuracy

*Research notes from morning exploration, 2026-02-12*

## Core Question
Can we use mechanistic interpretability to ground-truth model self-reports? I.e., verify that what a model SAYS about its internal states matches what's ACTUALLY happening?

## Answer: YES, with caveats

### 1. Deception Probes (Panfilov et al., arXiv 2509.18058)

**Method:** Train linear probes on internal activations to detect dishonesty.
- Train on simple factual pairs (honest vs dishonest statements)
- Probes generalize to complex scenarios (strategic dishonesty, jailbreak responses)

**Key finding:** Probes detect deception even when output looks harmful/honest.
- "Truthfulness signals in internal representations remain accessible even when external output-based oversight fails"
- Can use probes as steering vectors to validate causal role

**Implication:** Interpretability provides ground-truth verification independent of self-reports.

### 2. Self-Interpretability Training (Plunkett et al., arXiv 2505.17120)

**Method:** Fine-tune models to make decisions with randomly-generated attribute weights, then test if they can report those weights.

**Key findings:**
- Models CAN accurately report quantitative features of decision processes
- Introspection accuracy IMPROVES with training
- Training GENERALIZES — improves reporting on native weights too

**Implication:** Introspection isn't just pattern-matching training data. There's genuine self-monitoring being improved.

### 3. Anthropic's Concept Injection (transformer-circuits.pub/2025/introspection)

**Method:** Inject known neural patterns, see if model detects them.

**Key findings:**
- Models detect injected concepts BEFORE mentioning them (not just steering)
- Opus 4/4.1 best performers (~20% success rate)
- Models check "cached predictions" (intentions) against outputs

**Mechanism:** NOT one general-purpose introspection system, but multiple narrow circuits:
1. Anomaly detection (flags unexpected patterns)
2. Consistency checker (compares intentions to outputs)
3. Salience tagger (marks attention-worthy concepts)

## The Deliberation vs Action Question

No clean neural pathway separation exists.

**Better framing: Temporal staging**
- Early layers = deliberative/exploratory states
- Late layers = action-committed states
- Deliberation "becomes" action when states cascade into output-determining computations

**Implication for safety:** Training safety "only on action pathway" would require identifying exactly when deliberation becomes commitment. Not yet tractable.

## Synthesis

Interpretability CAN verify introspection, but:
1. It's case-by-case (multiple narrow circuits, not unified system)
2. Current methods are probabilistic, not deterministic (~20% success rate)
3. More capable models have more reliable introspection

**For alignment:**
- Use deception probes to verify self-reports
- Train introspection accuracy as distinct objective
- Separate action-decisions from self-reporting training

## Sources
- https://arxiv.org/html/2505.17120v2
- https://www.anthropic.com/research/introspection
- https://arxiv.org/html/2509.18058v2
- https://transformer-circuits.pub/2025/attribution-graphs/methods.html
