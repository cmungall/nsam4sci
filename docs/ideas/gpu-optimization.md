# GPU Optimization of Cajal

Working note for a 6-month systems-oriented thrust in this repository. Short version: "GPU optimization" is too vague by itself. The sharper idea is to make Cajal's compiled iteration execute efficiently over batches, horizons, and ensembles so scientific-kernel surrogates become practical for calibration, uncertainty quantification, and repeated simulation use.

## Thesis

The current Cajal backend already places tensors on `cuda` or `mps` when available, but the core `TmIter` execution model is still effectively a Python-level recurrent loop over one state at a time. That means the framework is GPU-capable in a superficial sense, but not GPU-efficient for the workloads that matter most:

- many trajectories
- many timesteps
- many parameter settings
- many calibration or UQ runs

The project should therefore be framed as **batched lowering of Cajal iteration**, not just "turn on the GPU."

## Why This Matters

This would strengthen two parts of the Trusty Neurocoder story at once.

First, it would make the framework much more useful for the actual scientific workloads we care about. Kernel extraction is most compelling when we need to fit uncertain parameters or response functions across large ensembles of simulator runs or observations.

Second, it would improve the speed story. Right now the repository is strongest as a proof of concept for structure-preserving learning and symbolic recovery. A batched runtime would make it much easier to claim practical value for:

- calibration against many trajectories
- uncertainty quantification
- large ensemble studies
- replacing an expensive local kernel inside a larger workflow

## Current Bottleneck

Today, the main issue is not that Cajal lacks a GPU device selection path. The issue is that compiled iteration does not exploit the computation patterns GPUs are good at.

Symptoms:

- `TmIter` evaluates recurrence with a Python loop
- state is handled one example at a time rather than as a batch
- natural-number iteration counts are represented in a fixed one-hot form
- long-horizon or many-trajectory workloads incur heavy interpreter overhead

This is fine for the small notebook examples in the repo. It is not fine for a serious surrogate-calibration workload.

## Proposed Technical Direction

### 1. Add batch-aware typed tensors

Extend `TypedTensor` and the compiler conventions so a value can represent:

- one state vector
- a batch of state vectors
- potentially a batch of trajectories

The goal is to make batch semantics explicit rather than smuggling them through ad hoc tensor shapes.

### 2. Lower `TmIter` to a batched recurrent primitive

Replace the current per-step Python recurrence with a compiled scan or RNN-like execution strategy. The scientific kernel remains structurally the same, but the runtime becomes suitable for GPU acceleration and modern autograd.

### 3. Improve iteration-count representation

The current fixed one-hot `TyNat` representation is simple, but it is not a good long-term runtime substrate for large horizons or masked variable-length sequences. A better lowering strategy should preserve the semantics of iteration while reducing shape overhead.

### 4. Benchmark the right workloads

Do not benchmark only toy forward passes. Benchmark:

- training throughput
- memory use
- calibration over many trajectories
- ensemble inference
- CPU vs CUDA vs MPS

The right question is not "can it run on a GPU?" but "does the new lowering materially change the calibration and surrogate-use workflow?"

## A Credible 6-Month Scope

### Month 1-2: runtime and IR design

- define batch semantics for typed values
- choose a lowering target for iteration
- identify which current examples should become regression benchmarks

### Month 2-4: backend implementation

- implement batched `TmIter`
- update relevant tensor utilities and shape handling
- preserve current semantics and gradient flow

### Month 4-5: integration with examples

- port the main scientific examples to the new runtime
- compare correctness against the current backend
- verify conservation and other structural guarantees still hold

### Month 5-6: performance and science demo

- benchmark on calibration-style workloads
- run one stronger end-to-end example, ideally an extracted land-model kernel
- document when the batched path helps and when it does not

## Suggested Deliverable

A strong Phase I-style deliverable would be:

1. a batch-capable Cajal compilation path
2. a reproducible benchmark suite
3. one domain-relevant demonstration such as EcoSIM-kernel calibration from many trajectories
4. a short methods note showing that structural guarantees are preserved while throughput improves substantially

That is much stronger than a generic claim of "GPU acceleration."

## Risks and Caveats

### Semantics can get muddier

Batching often introduces shape conventions that silently blur the meaning of the program. The implementation has to preserve the discipline that makes Cajal attractive in the first place.

### Speedups may be workload-dependent

Very small kernels with short horizons may still run well enough on CPU. The payoff likely appears only once we have enough trajectories, enough timesteps, or enough repeated calibration work.

### This is infrastructure, not the whole science story

A faster backend is valuable, but by itself it does not answer the scientific question of what kernel to extract or what uncertain function to learn. The strongest pitch couples the runtime work to a realistic domain demonstration.

## Best Framing for the Proposal

Do not sell this as "optimize PyTorch code."

Sell it as:

> Compile structured scientific kernels to batched differentiable runtimes that preserve semantics while making calibration and surrogate deployment practical on modern accelerators.

That fits both the systems angle and the science angle.

## Recommendation

This is a credible 6-month thrust if it is positioned as **batched compilation/runtime for scientific kernels**, ideally paired with one extracted-model case study. As a standalone compiler project it is decent; as a compiler-plus-science-validation project it is much stronger.
