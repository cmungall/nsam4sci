# DOE/ASCR Non-Bio Use Cases

Working note on non-biological use cases in the U.S. Department of Energy (DOE) Advanced Scientific Computing Research (ASCR) space. The emphasis here is on problems where the software already exposes logic that can be extracted, constrained, or verified. For the official ASCR mission and program scope, see the [DOE ASCR program page](https://science.osti.gov/ascr/).

## Thesis

The best non-bio ASCR targets are not generic "AI for HPC" tasks. They are cases where:

- the decision logic is already partly explicit
- correctness conditions are well defined
- public codes or datasets are available
- a neuro-symbolic or formal layer adds something beyond black-box prediction

## Glossary

- **DOE**: U.S. Department of Energy.
- **ASCR**: Advanced Scientific Computing Research, a DOE Office of Science program focused on advanced computing, software, and networking for science. Official page: <https://science.osti.gov/ascr/>.
- **HPC**: high-performance computing.
- **LLNL**: Lawrence Livermore National Laboratory.
- **I/O**: input/output.
- **DAG**: directed acyclic graph.
- **IR**: intermediate representation.
- **PETSc**: Portable, Extensible Toolkit for Scientific Computation. Official docs: <https://petsc.org/>.
- **KSP**: PETSc's linear solver interface for Krylov Subspace Methods. Official docs: <https://petsc.org/main/manualpages/KSP/KSP/>.
- **hypre**: scalable linear solvers and multigrid methods library from LLNL. Official pages: <https://computing.llnl.gov/projects/hypre-scalable-linear-solvers-multigrid-methods>, <https://hypre.readthedocs.io/en/stable/>.
- **MFEM**: Modular Finite Element Methods library. Official site: <https://mfem.org/>.
- **ECP**: Exascale Computing Project. Proxy-app suite: <https://proxyapps.exascaleproject.org/>.
- **ADIOS2**: Adaptable Input/Output System 2. Official docs: <https://adios2.readthedocs.io/en/latest/>.
- **AMR**: adaptive mesh refinement.
- **NPB**: NAS Parallel Benchmarks. Official page: <https://www.nas.nasa.gov/software/npb.html>.
- **Spack**: package manager for HPC software stacks. Official docs: <https://spack.readthedocs.io/en/latest/>.

## 1. Solver and Preconditioner Selection

Learn a compact policy that maps matrix, mesh, or problem features to valid solver and preconditioner choices. The key artifact is an interpretable decision rule, not a learned numerical solution operator.

Why it fits:

- solver families are explicit
- convergence and residual checks already exist
- legality constraints can be made structural

Good starting points:

- [PETSc KSP documentation](https://petsc.org/main/manualpages/KSP/KSP/) and the [PETSc users manual](https://petsc.org/release/manual/manual.pdf)
- [hypre documentation](https://hypre.readthedocs.io/en/stable/) and the [LLNL hypre overview page](https://computing.llnl.gov/projects/hypre-scalable-linear-solvers-multigrid-methods)
- [MFEM examples and miniapps](https://mfem.org/examples/)

## 2. Verified Autotuning for ECP Proxy Apps

Use public Exascale Computing Project (ECP) proxy applications to learn algorithm or parameter selection policies while preserving correctness against built-in checks or reference outputs.

Why it fits:

- kernels are small and benchmark-oriented
- optimization spaces are explicit
- correctness is easier to define than in full production codes

Good starting points:

- [ECP Proxy Applications suite](https://proxyapps.exascaleproject.org/)
- [XSBench](https://proxyapps.exascaleproject.org/app/xsbench/)
- [miniQMC](https://proxyapps.exascaleproject.org/miniqmc/)
- [CloverLeaf](https://proxyapps.exascaleproject.org/app/cloverleaf/)
- [hypre-mini-app](https://proxyapps.exascaleproject.org/app/hypre-mini-app/)

## 3. Workflow Scheduling and Orchestration

Model workflow systems as symbolic decision processes over DAGs, resources, staging rules, and retries. Learn scheduling or retry heuristics without discarding hard workflow constraints.

Why it fits:

- workflow logic is already formal-ish
- outputs can be explicit policies
- constraints are clearer than in many simulation surrogates

Good starting points:

- [Parsl](https://parsl-project.org/)
- [Balsam site and workflow docs](https://balsam.readthedocs.io/en/latest/user-guide/site-config/) and [job execution docs](https://balsam.readthedocs.io/en/latest/user-guide/batchjob/)
- [Flux quick start](https://flux-framework.readthedocs.io/en/latest/quickstart.html) and the [Flux project site](https://flux-framework.org/)

## 4. I/O, Checkpointing, and Data-Movement Policies

Learn policies for when to checkpoint, compress, stage, or run reduced diagnostics, while preserving hard constraints on consistency and recoverability.

Why it fits:

- existing I/O frameworks already expose explicit objects and rules
- the output policy is naturally interpretable
- there is a direct performance and usability story for ASCR

Good starting points:

- [ADIOS2 interface/components docs](https://adios2.readthedocs.io/en/latest/components/components.html)
- [Balsam data-transfer docs](https://balsam.readthedocs.io/en/latest/user-guide/transfer/) and [auto-scaling docs](https://balsam.readthedocs.io/en/latest/user-guide/elastic/)

## 5. AMR and Mesh-Control Policies

Treat adaptive mesh refinement (AMR), coarsening, and mesh-control logic as a constrained symbolic decision problem with learned scoring or prioritization inside valid mesh-update scaffolding.

Why it fits:

- refine/coarsen logic is structured
- constraints on admissible mesh states are explicit
- the learned component can stay small

Good starting points:

- [AMReX guided tutorials and example codes](https://amrex-codes.github.io/amrex/tutorials_html/)
- [AMReX AMR tutorial](https://amrex-codes.github.io/amrex/tutorials_html/AMR_Tutorial.html)
- [MFEM examples and miniapps](https://mfem.org/examples/)

## 6. Specification-Driven Synthesis and Verification

Use benchmark kernels where the specification and expected outputs are stable enough to support extraction, synthesis, and verification.

Why it fits:

- benchmarks are small
- reference behavior is known
- the logic is easier to isolate than in production applications

Good starting points:

- [NAS Parallel Benchmarks (NPB)](https://www.nas.nasa.gov/software/npb.html)

## 7. Package and Environment Logic

Treat package concretization, compatibility resolution, or environment repair as a symbolic reasoning problem with learned ranking or conflict triage.

Why it fits:

- the specification language already exists
- constraints are discrete and explicit
- this is highly relevant to scientific software operations

Good starting points:

- [Spack spec syntax](https://spack.readthedocs.io/en/latest/spec_syntax.html)
- [Spack environments](https://spack.readthedocs.io/en/latest/environments.html)
- [Spack `concretize` command reference](https://spack.readthedocs.io/en/latest/command_index.html)

## Best Near-Term Bets

If the goal is to demonstrate value quickly, prioritize:

1. workflow scheduling and orchestration
2. solver and preconditioner selection
3. verified autotuning on ECP proxy apps

These have the cleanest combination of public software, explicit logic, and believable verification stories.

## Relation to Lean or Formal Methods

These are also the best cases for a Lean-backed workflow because the semantic core is small enough to extract:

- solver applicability rules
- legal scheduling or resource-allocation constraints
- optimization-preserving transformations
- checkpoint or restart invariants

That makes them promising targets for a restricted IR that could feed both an executable system and a proof backend.

## Selected Official References

- DOE ASCR: <https://science.osti.gov/ascr/>
- PETSc KSP: <https://petsc.org/main/manualpages/KSP/KSP/>
- hypre: <https://hypre.readthedocs.io/en/stable/>
- MFEM examples: <https://mfem.org/examples/>
- ECP Proxy Apps: <https://proxyapps.exascaleproject.org/>
- Parsl: <https://parsl-project.org/>
- Balsam: <https://balsam.readthedocs.io/en/latest/user-guide/site-config/>
- Flux: <https://flux-framework.readthedocs.io/en/latest/quickstart.html>
- ADIOS2: <https://adios2.readthedocs.io/en/latest/components/components.html>
- AMReX tutorials: <https://amrex-codes.github.io/amrex/tutorials_html/>
- NAS Parallel Benchmarks: <https://www.nas.nasa.gov/software/npb.html>
- Spack: <https://spack.readthedocs.io/en/latest/>
