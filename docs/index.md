# Trusty Neurocoder

Neuro-Symbolic Agents for Verified Scientific Code Generation.

## Overview

Trusty Neurocoder combines LLM-based agentic workflows with
[Neuro-Symbolic Abstract Machines (NSAMs)](https://metareflection.seas.harvard.edu/research/neuro/)
to enable verified scientific code generation, optimization, and surrogate
construction.

**NSAMs** are neural networks structurally equivalent to programming language
interpreters. They enable principled compilation of symbolic programs into
neural architectures and decompilation back to interpretable code.
**LLM agents** bridge the gap between real-world scientific codebases and the
declarative representations NSAMs require.

## Notebooks

### Foundations
| Notebook | Description |
|----------|-------------|
| [01 - Cajal Intro](notebooks/01_cajal_intro.ipynb) | Boolean functions compile to matrices; iteration as recurrent neuron |
| [02 - Exponential Decay](notebooks/02_exponential_decay.ipynb) | Learn scalar ODE rate constant from data |

### Earth & Environment
| Notebook | Description |
|----------|-------------|
| [03 - Unknown Function](notebooks/03_learn_unknown_function.ipynb) | MLP learns unknown moisture response; symbolic regression recovers Hill equation |
| [04 - CENTURY-Lite](notebooks/04_century_lite.ipynb) | 3-pool model, 2 unknown functions learned simultaneously, mass conservation verified |

### DOE Science Domains
| Notebook | Description |
|----------|-------------|
| [05 - Decay Chain](notebooks/05_decay_chain.ipynb) | 4-isotope radioactive decay chain; learns unknown branching ratios exactly |
| [06 - Battery Degradation](notebooks/06_battery_degradation.ipynb) | SEI growth + capacity fade; recovers parabolic growth law via symbolic regression |
| [07 - Chemical Kinetics](notebooks/07_chemical_kinetics.ipynb) | Reversible reaction A⇌B; recovers Arrhenius rate k=2.0·exp(-5.0/T) from equilibrium data |
| [08 - EcoSIM Kernel Case Study](notebooks/08_ecosim_kernel_case_study.ipynb) | Soil-carbon decomposition kernel extracted from EcoSIM Fortran |
| [09 - PFLOTRAN Relative Permeability](notebooks/09_pflotran_relative_permeability.ipynb) | Subsurface-flow constitutive relation as a structured surrogate |
| [10 - Methionine Cycle](notebooks/10_methionine_cycle.ipynb) | Regulated metabolic cycle (DTU Biosustain model); keeps stoichiometry exact, recovers SAM→CBS allosteric Hill activation, conservation to 1e-7 |
| [11 - Regulated Steady State](notebooks/11_regulated_steady_state.ipynb) | Amortizes the regulated steady-state solve; exact moiety reduction (left null space of S), scales to 128 metabolites, ~95x surrogate speedup with conservation guaranteed |
| [12 - Methionine Steady-State Fit](notebooks/12_methionine_steady_state_fit.ipynb) | Real methionine+folate network; finds the folate moiety from S's null space; differentiates through the steady state (implicit function theorem) to fit SAM→CBS / SAM→MTHFR allosteric constants from steady-state data |
| [13 - Methionine Bayesian UQ](notebooks/13_methionine_bayesian_uq.ipynb) | Bayesian calibration with uncertainty, priors anchored to the real Maud methionine model; Gauss–Newton Laplace posterior surfaces the amp/Ka identifiability ridge (corr 0.99) that the point fit hid |
| [14 - CBS MWC: Laplace vs HMC](notebooks/14_cbs_mwc_laplace_vs_hmc.ipynb) | Faithful single-enzyme port (real Maud MWC rate law + priors, mM units); Laplace matches exact grid and HMC on informative data, and visibly misses the skewed L tail on data-poor designs |

## Quick Start

```bash
# Install
uv pip install -e ".[notebooks,docs]"

# Run all notebooks
just notebooks

# Serve docs locally
just docs
```

## Architecture

```
┌──────────────────────────────────────┐
│  Layer 1: LLM Agent                  │
│  - Parses real scientific code       │
│  - Extracts algorithmic kernels      │
│  - Translates to Cajal programs      │
├──────────────────────────────────────┤
│  Layer 2: NSAM Compilation           │
│  - Cajal program → PyTorch RNN       │
│  - Learnable sub-expressions (MLPs)  │
│  - Backprop through compiled program │
├──────────────────────────────────────┤
│  Layer 3: Verification               │
│  - Structural invariants by design   │
│  - Symbolic regression (decompile)   │
│  - Mass conservation, positivity     │
└──────────────────────────────────────┘
```
