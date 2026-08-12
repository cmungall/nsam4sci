# Program Translation as a Neurosymbolic Use Case

Working note on program translation as an application area for agentic and neuro-symbolic methods. The useful framing is not "ask a model to rewrite code into another language." The useful framing is:

- extract a restricted semantic intermediate representation (IR)
- preserve the contracts and invariants in that IR
- generate target-language code from the IR
- verify equivalence or at least contract preservation
- use learning or search only for the underspecified choices

This makes translation a good fit for the broader ideas in this repository.

## Thesis

Program translation is especially promising when the target language encodes a stronger discipline than the source language:

- safety and ownership in [Rust](https://www.rust-lang.org/)
- array-oriented scientific expressivity in [Julia](https://julialang.org/)

The translation problem then becomes partly semantic and partly organizational: preserve behavior, preserve or strengthen constraints, and realize the result idiomatically in the target language.

## Why This Is Interesting

Translation forces the semantic layer to become explicit. That makes it a natural target for:

- extraction of contracts and invariants
- proof obligations
- repair loops after failed compilation or failed checks
- learning to rank multiple valid target-language realizations

It also fits naturally with a Lean-backed or IR-centric workflow.

## Legacy to Rust

This is the safety and maintainability story.

Best targets:

- small C or C++ kernels
- file parsers and data loaders
- workflow or orchestration logic
- utility libraries with explicit tests
- numerics without extreme aliasing or unsafe memory behavior

What should stay symbolic or checkable:

- ownership and borrowing assumptions
- aliasing discipline
- preconditions and postconditions
- error-handling behavior
- state-machine or protocol invariants

What can be left to learned or agentic search:

- data-structure choices
- where to borrow versus clone
- library/API replacement choices
- control-flow rewrites needed to satisfy Rust constraints

## Scientific Kernels to Julia

This is the scientific modernization story.

Best targets:

- Fortran kernels
- MATLAB or NumPy scientific functions
- ODE or PDE update rules
- array transforms and analysis pipelines
- code that may later be differentiated, optimized, or composed in modern workflows

What should stay symbolic or checkable:

- shape and dimension constraints
- indexing semantics
- purity versus mutation boundaries
- kernel-level invariants such as conservation or monotonicity
- units or parameter-role assumptions where available

What can be left to learned or agentic search:

- idiomatic Julia realization
- library selection
- vectorization or broadcasting choices
- performance-oriented but semantics-preserving rewrites

## Translation Through a Common IR

The most promising architecture is:

1. source language -> restricted IR
2. IR -> optional verifier or proof backend
3. IR -> target-language generator
4. tests, contracts, or proofs -> repair loop

A useful IR would likely include:

- typed variables and records
- arithmetic and boolean expressions
- guarded control flow
- loops or iteration patterns
- array operations
- side-effect boundaries
- contracts and invariants

The same IR could potentially support code generation, Lean translation, or selected neurosymbolic backends.

## Possible Project Shapes

### 1. Verified modernization

Translate legacy kernels into Rust or Julia while preserving explicit contracts and tests.

### 2. Contract-aware transpilation

Move between languages while carrying preconditions, postconditions, and invariants through the translation.

### 3. Multi-target code generation

Translate a single extracted IR into more than one target, such as Rust for safety-critical support code and Julia for scientific kernels.

### 4. Translation plus optimization

Generate correct target-language code first, then apply learned ranking or search over equivalent rewrites for performance or readability.

## What Not to Do First

Avoid starting with:

- whole-application translation
- unrestricted Python to Rust or Fortran to Julia across large repos
- MPI, OpenMP, GPU, or distributed runtime semantics as the first target
- exact floating-point equivalence for every program detail

Those are all legitimate long-term directions, but they are bad first demonstrations.

## Recommended Phase I Path

1. Pick one narrow source-to-target pair, such as C to Rust or Fortran kernel to Julia.
2. Restrict scope to small self-contained kernels or support modules.
3. Define a tiny IR with contracts and typed interfaces.
4. Generate target code from the IR.
5. Use tests, static checks, or proof obligations to close the loop.

## Relation to Other Ideas in This Directory

- The [Lean note](./lean-neurosymbolic.md) provides the verification and proof-backend angle.
- The [workflow note](./workflows.md) suggests a similar IR-first approach for workflow languages.
- The [framework-comparison note](./neurosymbolic-framework-options.md) matters if parts of the extracted IR become a learning problem rather than only a translation problem.

## Recommendation

Program translation is a good use case precisely because it forces semantic extraction. The best first projects are not end-to-end rewrites of large systems. They are small verified translations where the IR, contracts, and repair loop are the real deliverables.
