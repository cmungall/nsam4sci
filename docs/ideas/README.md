# Ideas Index

Short index for working notes in `docs/ideas/`. These are exploratory documents, not settled roadmap items.

## DOE / ASCR Applications

- [DOE/ASCR Application Ideas](./ascr-application-ideas.md): broad set of candidate ASCR-facing applications, including proxy apps, solver selection, PFLOTRAN, ADIOS2, and WarpX.
- [DOE/ASCR Non-Bio Use Cases](./ascr-nonbio-use-cases.md): narrower list focused on non-biological targets where software logic is already explicit enough to extract or verify.

## Chemistry / Biology

- [Chemical Classifier Idea](./chemical-classifier.md): hybrid RDKit + neurosymbolic classifier path, with SMARTS predicates, ontology constraints, and a C3PO-to-NSAM direction.

## Formal Methods

- [Lean in a Neurosymbolic Workflow](./lean-neurosymbolic.md): using a restricted IR plus Lean as verifier, specification layer, and proof-guided feedback source.

## Framework Choice

- [Neurosymbolic Framework Options](./neurosymbolic-framework-options.md): when to use Cajal versus alternatives such as DeepProbLog, LTN, NeuraLogic, or DeepStochLog.

## Systems / Performance

- [GPU Optimization of Cajal](./gpu-optimization.md): systems-oriented note on batching, horizons, and compiled execution efficiency for scientific-kernel surrogates.

## Suggested Reading Order

1. Start with [DOE/ASCR Application Ideas](./ascr-application-ideas.md) for scope.
2. Read [Neurosymbolic Framework Options](./neurosymbolic-framework-options.md) to choose the right technical substrate.
3. Then go deeper into one vertical: [Chemical Classifier Idea](./chemical-classifier.md), [Lean in a Neurosymbolic Workflow](./lean-neurosymbolic.md), or [DOE/ASCR Non-Bio Use Cases](./ascr-nonbio-use-cases.md).
