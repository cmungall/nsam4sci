# Workflow Systems as a Neurosymbolic Target

Working note on workflow systems as an application area beyond simulation codes. The key idea is not to replace existing workflow theory or standards such as Petri nets, Common Workflow Language, or Workflow Description Language. The opportunity is to use workflow systems as already-structured symbolic objects, then add learning, extraction, repair, verification, or optimization around that fixed semantics.

## Thesis

Workflows are a strong target because they already expose:

- explicit tasks and dependencies
- typed inputs and outputs
- resource requests and execution constraints
- retries, caching, staging, and provenance hooks
- failure states and resumption logic

This makes them a better fit for a neuro-symbolic or formal layer than many arbitrary codebases.

## Why This Is Not "Just Petri Nets Again"

There is a long history of formal workflow models, including Petri nets and other process calculi. The goal here is not to redo that theory. The practical opportunity is one layer up:

- extract a common intermediate representation (IR) from real workflow systems
- preserve the hard workflow semantics those systems already define
- learn only the fuzzy or empirical parts
- optionally verify useful properties over the extracted IR

The novelty would be in the bridge between modern workflow software, agentic extraction, and constrained learning.

## Candidate Workflow Targets

### Scientific and HPC workflow engines

- [Parsl](https://parsl-project.org/): Python parallel scripting with dynamic task graphs
- [Balsam](https://balsam.readthedocs.io/en/latest/user-guide/site-config/): workflow and data management for large-scale computing campaigns
- [Flux](https://flux-framework.readthedocs.io/en/latest/quickstart.html): composable job scheduling and resource management
- [Pegasus](https://pegasus.isi.edu/): automated workflow execution, recovery, and provenance capture

### Workflow languages and standards

- [Common Workflow Language (CWL)](https://www.commonwl.org/)
- [OpenWDL / Workflow Description Language (WDL)](https://openwdl.org/)
- [Nextflow workflows](https://www.nextflow.io/docs/stable/workflow.html)
- [Snakemake](https://snakemake.readthedocs.io/en/stable/)

Genomics pipelines are the obvious first example, but the same abstraction applies well beyond bioinformatics.

## Workflow IR

A useful restricted IR would likely include:

- task nodes
- typed ports and files
- dependency edges
- resource requests
- scatter / map / conditional execution
- retries and failure handlers
- caching and provenance annotations
- checkpoint or resume semantics

This IR could serve three purposes:

1. common representation across workflow systems
2. target for learned policies
3. target for verification or static analysis

## Where Learning Helps

The hard semantics of the workflow should stay fixed. Learning should focus on the parts that are empirical or noisy:

- resource prediction
- walltime estimation
- retry policy
- failure diagnosis
- data staging and placement decisions
- subworkflow or backend selection
- cache reuse heuristics
- schedule ranking under constraints

This keeps the problem well scoped: learn policies over workflows, not the workflow semantics themselves.

## Where Verification Helps

The extracted IR could support checks such as:

- no task runs before required inputs exist
- resource requests satisfy backend constraints
- all outputs are produced along every valid path
- retry or restart rules preserve resumability
- provenance declarations remain intact under optimization
- workflow rewrites preserve observable behavior

This fits naturally with the Lean-oriented ideas elsewhere in this directory.

## Possible Project Shapes

### 1. Workflow linting and repair

Use an agent to read a workflow, extract the IR, detect bad dependencies or invalid resource declarations, and synthesize repairs with validation.

### 2. Workflow transpilation

Translate one workflow language to another through a common IR, with equivalence checks on the extracted structure.

### 3. Learned orchestration policies

Keep the workflow fixed, but learn resource sizing, placement, retry, or staging policies from execution traces.

### 4. Protocol-to-workflow synthesis

Extract a workflow from natural language methods sections, README files, notebooks, or shell scripts, then compile to CWL, WDL, or Nextflow.

## DOE / ASCR Relevance

This matters in ASCR because large-scale scientific campaigns are increasingly workflow-driven. The execution logic is already partly formal, the software stacks are public, and the payoff is not limited to one scientific domain. A workflow-focused project also avoids some of the representational friction of trying to formalize full simulation codes.

## Recommended Phase I Path

1. Choose one workflow front-end, preferably WDL or CWL because they are already standards.
2. Define a small workflow IR.
3. Build an extractor and a linter or verifier over that IR.
4. Add one learned component, such as resource or retry prediction.
5. Evaluate on public workflows and execution traces where available.

## Recommendation

Workflow systems are a promising application area precisely because they already have explicit symbolic structure. The right project is not to replace that structure, but to make it portable, checkable, and learnable in the places where current workflow software is still heuristic.
