# NSAM4Sci Proposal Abstract

Scientific AI systems increasingly interact with software through retrieval,
tool use, and agentic search, but they still treat most scientific code as
unstructured text or opaque executables. This creates a major gap for DOE
scientific software: agents may be able to read code or generate code, but they
do not reliably preserve the semantic structure, invariants, and domain
constraints that make scientific codes trustworthy. NSAM4Sci addresses this
problem by treating scientific code, workflows, and formal specifications as
first-class semantic data objects that can be extracted, indexed, reasoned
over, and selectively compiled into learnable models.

The central idea is an IR-first neuro-symbolic pipeline. In Phase I, LLM agents
will read public DOE-relevant artifacts such as Fortran or C kernels, workflow
descriptions, and benchmark codes, and translate them into a restricted
intermediate representation (IR). This IR will capture typed interfaces,
dependencies, guarded control flow, selected invariants, and semantic
annotations that can support both learning and verification. Extracted IR
fragments will then be routed to the backend most appropriate for their
structure. Some fragments will map naturally to neuro-symbolic backends,
including NSAM-style models that preserve explicit symbolic scaffolding while
learning only uncertain components. Other fragments will map more naturally to
formal or proof-oriented backends such as Lean, where contracts, equivalence
conditions, and transformations can be checked. The project therefore does not
assume one universal model for all scientific artifacts; instead, it uses a
shared semantic representation to support multiple forms of trustworthy
reasoning.

Phase I will demonstrate this framework on three complementary artifact
classes. First, in a scientific-kernel case, the project will extract a public
DOE-relevant kernel and preserve its known update structure while learning only
selected uncertain sub-expressions. This will demonstrate constrained surrogate
learning that remains interpretable and checkable, rather than replacing the
entire model with a black-box emulator. Second, in a workflow case, the project
will extract a scientific workflow into the IR and use that representation for
analysis, repair, or learned policy support such as retry, scheduling, or
resource prediction. Third, in a program-logic case, the project will apply the
same IR-first approach to a task such as verified optimization, translation, or
synthesis, showing that extracted symbolic structure can support interpretable
and checkable code transformations.

The proposed work is directly aligned with Topic 18C: Neuro-Symbolic Agents for
Code Development. Its AI advantage comes from combining three capabilities that
are usually isolated from one another: agentic code understanding, symbolic
structure preservation, and verification-aware learning. Rather than asking an
agent to generate or optimize code in an unconstrained way, NSAM4Sci uses
agents to identify the parts of a scientific artifact that should remain fixed,
the parts that can be learned, and the parts that should be formally checked.
This makes the resulting systems more interpretable, more portable across
artifact types, and more appropriate for scientific settings where correctness,
traceability, and domain semantics matter.

The expected Phase I outcome is a reusable prototype that shows how code and
workflows can be treated as structured scientific data rather than only as
source text. The project will deliver a restricted IR, at least two extraction
front ends, multiple backend mappings, and three proof-of-concept
demonstrations built on public artifacts with reproducible evaluation paths.
More broadly, NSAM4Sci will establish a credible path toward future scientific
AI systems that can learn from, reason over, and transform software artifacts
without discarding the semantic and formal structure on which scientific
trustworthiness depends.
