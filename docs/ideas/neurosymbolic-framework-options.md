# Neurosymbolic Framework Options

Working note on when to use Cajal versus other neuro-symbolic approaches for ideas under discussion in this repository.

## Thesis

Cajal is a strong fit when the object of interest is naturally a **small typed program** with fixed structure and a few learnable holes. It is a weaker fit when the native object is a graph, a relational knowledge base, a sequence of symbolic events, or a large rule system with probabilistic uncertainty.

For chemistry and biology use cases, Cajal should be treated as one option, not the default.

## Where Cajal Fits Best

Best current fit:

- scientific kernels and surrogate models
- small state-update programs
- algorithmic decision logic with strong structural constraints
- settings where exact program-to-network compilation is the main scientific value

Examples in this repo already follow that pattern.

## Where Cajal Is a Stretch

Less natural fit:

- molecular graphs
- ontology-heavy multi-label classification
- biosynthetic gene cluster annotation over domain-order or neighborhood structure
- logic programs with many discrete facts and uncertain predicates

These are not impossible, but they usually require a feature-extraction or transpilation layer first.

## Alternative Frameworks

### DeepProbLog

Best when the problem already looks like a rule program with a few uncertain predicates. This is a strong candidate for C3PO-style classifiers: fixed symbolic rules, neural predicates for ambiguous cases, and explicit logical inference.

Use for:

- chemical class classifiers
- ontology-aware rule repair
- weakly learned predicates inside otherwise symbolic programs

### LTN / LTNtorch

Best when you want learned predicates plus logical constraints, but you do not need exact symbolic execution. Good for fast experiments with ontology consistency, subsumption, and disjointness constraints.

Use for:

- multi-label chemical ontology prediction
- soft logical regularization over embeddings or descriptor models
- quick baseline systems

### NeuraLogic

Best when the native data is relational or graph-structured. This looks like the strongest first option for biology applications involving genes, domains, neighborhoods, and structured interactions.

Use for:

- biosynthetic gene cluster annotation
- reaction or pathway relation prediction
- molecule or gene-neighborhood reasoning over graphs

### DeepStochLog

Best when the symbolic side has sequential or grammar-like structure. This is worth considering for BGCs if cluster types are modeled as gene/domain-order templates rather than only as unordered feature sets.

Use for:

- cluster-type grammars
- domain-order templates
- symbolic sequence models with learned scoring

## Recommendations by Project Idea

### Scientific surrogate kernels

Recommendation: start with Cajal.

Reason: exact compilation and structural guarantees are the point of the exercise.

### C3PO chemical classifiers

Recommendation: start with DeepProbLog or a hybrid RDKit + NSAM/Cajal feature model.

Reason: the core artifact is a rule-based classifier with ontology structure, not a recurrent state-update program. If the C3PO program subset is small and regular enough, transpiling to a restricted Cajal-compatible DSL may still be worthwhile.

### BGC annotation

Recommendation: start with NeuraLogic; consider DeepStochLog if sequence/grammar structure matters more than graph relations.

Reason: BGC annotation is already a mix of curated rules, HMM/domain evidence, and fuzzy contextual decisions over structured biological objects.

## Practical Decision Rule

Choose Cajal when you can write down the target as a compact typed program whose structure you want to preserve exactly.

Choose another framework when the main object is already a relational, logical, or graph reasoning problem and forcing it into a tiny functional core would add more friction than value.

## Short Version

- `Cajal`: best for scientific kernels and structured surrogates
- `DeepProbLog`: best for rule programs with neural predicates
- `LTNtorch`: best for fast logic-constrained learning baselines
- `NeuraLogic`: best for relational and graph-shaped biology problems
- `DeepStochLog`: best for symbolic sequence or grammar structure
