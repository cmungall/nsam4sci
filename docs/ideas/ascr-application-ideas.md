# DOE/ASCR Application Ideas

Working note for candidate applications of the Trusty Neurocoder / NSAM4SCI framework. These are biased toward public DOE-relevant codes or datasets that are easy to access and credible for a Phase I proof of concept.

## 1. Verified Autotuning for ECP Proxy Apps

Use small public proxy applications such as XSBench, ExaMiniMD, and miniQMC to learn explicit dispatch or tuning rules while preserving correctness checks already present in the apps. This is a good fit for agent-driven extraction of algorithm choice logic and decompilation back to interpretable policies.

Starting points: Exascale Computing Project Proxy Apps suite, especially XSBench and ExaMiniMD.

## 2. Solver and Preconditioner Selection

Learn a symbolic policy that chooses solver and preconditioner configurations from matrix or mesh features, while correctness remains anchored by residual and convergence tests. This is attractive because the learned object is not the PDE solution itself, but a compact decision rule for scientific software.

Starting points: PETSc KSP tutorial examples, hypre examples, and MFEM examples or miniapps.

## 3. PFLOTRAN Constitutive or Reaction Closure Learning

Extract a small reactive transport or subsurface flow kernel from PFLOTRAN, keep the conservation structure fixed, and learn only uncertain constitutive terms such as permeability, saturation, or reaction submodels. This is close to the structured-surrogate story already demonstrated in this repository, but on a DOE-recognizable code.

Starting points: PFLOTRAN example input decks and regression-style examples.

## 4. In Situ Analysis and I/O Policy Synthesis

Target workflow decisions rather than simulation physics: when to checkpoint, compress, stage, or trigger reduced diagnostics during a run. This is a useful non-simulation application for the framework because the output can be an inspectable policy rather than a black-box controller.

Starting points: ADIOS2 examples and tutorial workflows.

## 5. WarpX / PICSARlite Kernel Augmentation

Use the framework to learn or calibrate small plasma or beam-physics submodels, adaptive diagnostics, or runtime control rules around existing PIC kernels. WarpX is appealing because it is open, DOE-relevant, and already exposes Python extension workflows that lower the barrier to experimentation.

Starting points: WarpX Python extension examples and reduced test problems.

## 6. E3SM Land or Biogeochemistry Calibration Against Public DOE Data

Extract land-model or biogeochemistry kernels and calibrate uncertain functions against public Environmental Systems Science datasets, while preserving mass-balance and variable-role semantics. This is likely the strongest long-term science story, although it is heavier than the proxy-app path.

Starting points: E3SM land components plus public ESS-DIVE datasets exposed through the ESS-DIVE Dataset API.

## Recommended Order

For a low-friction progression: start with ECP proxy apps, then solver/preconditioner selection, then PFLOTRAN or E3SM-land kernel extraction. That sequence moves from software-centric demonstrations toward higher-value science cases without taking on full production-code complexity immediately.
