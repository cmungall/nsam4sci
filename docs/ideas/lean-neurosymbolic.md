# Lean in a Neurosymbolic Workflow

Working note on using Lean or other proof assistants as part of a larger neuro-symbolic system. The main idea is not to formalize whole legacy codebases directly. The practical move is to extract a **small formal representation** of the logic a program already contains, then use Lean as a verifier, specification language, or counterexample generator inside an agentic loop.

## Thesis

Lean is most valuable here as the hard semantic spine of the workflow:

- agents extract a restricted symbolic IR from code
- the IR maps to executable artifacts and to Lean
- learned or search-based components fill holes or rank candidates
- Lean discharges proof obligations or returns failures
- failures drive repair, retraining, or search

This gives a neuro-symbolic loop with an actual verifier, not just a loss penalty.

## What to Extract from Programs

Good formal artifacts include:

- preconditions and postconditions
- loop invariants
- branch predicates and guarded transitions
- state-update rules for kernels
- conservation, monotonicity, positivity, and symmetry laws
- dimensional or type-level constraints
- hierarchy or ontology implications
- rewrite rules and normalization logic

The goal is to formalize the part that carries semantic meaning, not every implementation detail.

## Roles for Lean

### 1. Verifier

The system proposes code, rules, classifiers, or repairs. Lean checks whether the relevant obligations actually hold.

### 2. Specification language

A restricted IR can be translated into Lean definitions and theorems. The same IR can also drive code generation or NSAM compilation.

### 3. Constraint generator

Lean-level properties can be pushed down into architectural constraints, search filters, or generated tests.

### 4. Counterexample source

Proof failures and missing lemmas tell the agent exactly where the symbolic model is incomplete or wrong.

### 5. Training signal

Proof traces, theorem statements, and proof failures can become supervision for ranking candidate programs or invariants.

## Candidate Architectures

### A. Program -> IR -> Lean + executable model

Extract a small transition system or classifier program from code, then:

- compile it to an executable model
- translate it to Lean
- verify core invariants in Lean

This is the cleanest fit for scientific kernels.

### B. Synthesis with proof-in-the-loop

Generate candidate symbolic programs or rule repairs, then use Lean success or failure to steer the search. The learned component ranks candidates; Lean prunes incorrect ones.

### C. Verifiable optimization

Use a learner to choose when to apply an optimization, but require a Lean proof that the transformed program preserves semantics.

## Good Initial Targets

### Scientific kernels

Examples:

- mass conservation
- positivity of state variables
- monotone environmental response assumptions
- type or dimension preservation across updates

### Ontology-aware classifiers

Examples:

- `child => parent`
- disjointness of sibling classes
- prerequisite predicates for classifier outputs

This fits C3PO-style chemistry and potentially BGC annotation if the class logic is explicit enough.

### State machines and protocols

Examples:

- legal transition constraints
- resource-use invariants
- forbidden state combinations

## What Not to Do First

Avoid starting with:

- direct full-program translation from Python, C++, or Fortran to Lean
- floating-point-heavy numerical semantics at full fidelity
- proofs over entire production codebases
- a proof assistant as the only representation layer

Those are too expensive for early progress.

## Recommended Phase I Path

1. Define a tiny IR for predicates, arithmetic expressions, guarded transitions, and typed state.
2. Build an extractor from a narrow class of source programs into that IR.
3. Add one Lean backend that emits definitions and proof obligations.
4. Use the same IR for execution, learning, or compilation in the main system.
5. Close the loop by using proof failures as structured feedback.

## Why This Matters

The benefit is not just verification at the end. A formal layer gives the whole neuro-symbolic workflow a stable semantic interface. Agents can read code, learners can fit uncertain pieces, symbolic systems can compose rules, and Lean can decide which claims are actually true.

## Promising Repo-Specific Ideas

- EcoSIM-style kernels with Lean proofs of conservation and non-negativity scaffolding
- C3PO-style classifiers with Lean proofs of ontology consistency
- algorithm-selection or optimization rules with Lean proofs of semantics preservation

## Recommendation

Treat Lean as the place where extracted logic becomes explicit, checkable, and reusable. Do not ask Lean to absorb the whole program. Ask it to own the semantic core.
