# Chemical Classifier Idea

Working note for a chemistry-facing extension of the Trusty Neurocoder framework. Short answer: translating **all** of SMARTS directly into NSAM primitives would be a research project, but using SMARTS as fixed symbolic predicates inside a neuro-symbolic classifier is entirely reasonable.

## Thesis

Do not try to replace RDKit or full subgraph isomorphism on day one. Instead:

1. parse SMILES with RDKit
2. compute a typed molecular feature representation
3. expose fixed predicates such as SMARTS matches as symbolic inputs
4. let the NSAM/Cajal program combine those predicates with a small number of learnable sub-expressions
5. enforce ontology constraints structurally

This keeps the most expensive and mature chemistry logic fixed while still giving us a place for learning, compilation, and verification.

## Proposed Architecture

### 1. Front-end featurization

Build `MolFeatures` from:

- SMARTS hit booleans
- fingerprint bits
- atom and bond counts
- ring, aromaticity, valence, and charge descriptors
- optional ontology metadata

In the current codebase, this would likely be represented as `TyReal(n)` plus some boolean-derived channels rather than a first-class molecular graph type.

### 2. Symbolic classifier skeleton

Represent the classifier as a small program over `MolFeatures`. Example for a primary alcohol:

```text
is_primary_alcohol(feats) =
  if has_ch2oh(feats) then
    if is_saturated(feats) then true else false
  else false
```

Here `has_ch2oh` is a fixed SMARTS-based predicate, while `is_saturated` could be either fixed logic or a learned sub-expression over features.

### 3. Structural constraints

Encode ontology relations as architectural constraints where possible:

- `primary_alcohol => alcohol`
- mutually exclusive classes stay disjoint
- required parent predicates cannot be violated by child predictions

This is the main place where the NSAM framing adds value over a raw LLM-generated RDKit script.

### 4. Tiny ontology wiring example

The point is not to predict three unrelated labels and later check whether they agree. The point is to build the symbolic classifier so agreement is forced by structure before compilation.

Example:

```text
has_oh(feats)          : fixed SMARTS predicate
has_primary_site(feats): fixed SMARTS predicate
has_tertiary_site(feats): fixed SMARTS predicate
passes_alcohol_context(feats): fixed or learnable sub-expression

is_alcohol(feats) =
  has_oh(feats) AND passes_alcohol_context(feats)

is_primary_alcohol(feats) =
  is_alcohol(feats) AND has_primary_site(feats) AND NOT has_tertiary_site(feats)

is_tertiary_alcohol(feats) =
  is_alcohol(feats) AND has_tertiary_site(feats) AND NOT has_primary_site(feats)
```

Consequences:

- `is_primary_alcohol => is_alcohol` by construction
- `is_tertiary_alcohol => is_alcohol` by construction
- primary and tertiary alcohol predictions are structurally disjoint
- only selected sub-terms such as `passes_alcohol_context` need to be learned

In the intended design, these logical dependencies live in the symbolic program and therefore are compiled into the NSAM. The compiled network inherits the constrained hypothesis class rather than learning consistency as a soft preference.

## What Is Feasible Now

Feasible Phase I target:

- fixed SMARTS and RDKit descriptors
- NSAM/Cajal logic over those features
- small learned holes for ambiguous chemistry
- verification against ontology constraints and held-out labels

Not a Phase I target:

- compiling full SMARTS semantics from scratch
- learning raw graph matching end to end
- replacing RDKit as the chemistry engine

## Benchmark Plan

### Phase 1: ChEBI structural classes

Start with ChEBI-style classes that already have reasonably crisp structural definitions:

- alcohol
- primary alcohol
- carboxylic acid
- amide
- ester
- aromatic heterocycle

Baseline comparisons:

- handwritten RDKit or SMARTS rules
- C3PO-style LLM-generated RDKit classifier
- hybrid NSAM classifier with fixed SMARTS predicates

Metrics:

- precision, recall, F1
- ontology consistency
- fraction of predictions with machine-checkable explanations
- number of violated parent or disjointness constraints

### Phase 2: ChEMBL or assay-related labels

Move from pure structure classes to weakly supervised bioactivity or assay-family prediction. The chemistry is less crisp here, so the value of small learned components grows.

## Why This Is Interesting

This is a cleaner testbed for neuro-symbolic classification than many scientific-code examples:

- the symbolic substrate already exists in SMARTS and ontologies
- labels and class hierarchies are available
- explanations are meaningful to domain scientists
- verification targets are concrete

It also connects naturally to prior C3PO work already described in `docs/proposal.md`.

This also suggests a practical C3PO-to-NSAM path: transpile the subset of C3PO classifier programs that can be expressed in a small chemistry DSL, preserve the fixed SMARTS logic, and replace only the ad hoc or ambiguous parts with learnable holes.

## Adjacent Biology/Chemistry Extensions

Once the classifier path works, nearby applications include:

- toxicophore or structural-alert classifiers
- reaction family classifiers from reaction SMARTS
- metabolite or lipid class classification
- microbiome metabolite or enzyme-family classifiers using public DOE-adjacent resources such as NMDC or KBase

## Recommendation

If this direction becomes active work, the first implementation should be a **hybrid RDKit + NSAM classifier**, not a full graph-native Cajal extension. That will let us test the actual scientific value of structural constraints and decompilation before taking on the harder language-design problem.
