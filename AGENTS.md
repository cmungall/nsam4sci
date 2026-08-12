# Repository Guidelines

## Project Structure & Module Organization
Core code lives under `src/`. `src/cajal/` contains the working language implementation: `syntax.py` for AST/types, `typing.py` for the linear type checker, `evaluating.py` for symbolic evaluation, and `compiling.py` for PyTorch-backed compilation. `src/trusty_neurocoder/` holds higher-level symbolic fitting code. Tests live in `tests/` and follow the package split. Use `examples/` for runnable demos, `notebooks/` for executed research notebooks, and `docs/` for MkDocs content and slides. Treat `site/` as generated output; only refresh it when publishing docs.

## Build, Test, and Development Commands
Use Python 3.12+ and `uv`.

- `uv pip install -e ".[dev,notebooks,docs]"` installs runtime, test, notebook, and docs dependencies.
- `just test` runs the full pytest suite with verbosity.
- `uv run pytest tests/test_cajal_soundness.py -v` runs a focused file during iteration.
- `just examples` executes the main scientific demos.
- `just notebooks` re-runs all notebooks in place; `just nb notebooks/01_cajal_intro.ipynb` runs one notebook.
- `just docs` serves the MkDocs site locally; `just docs-build` builds it.

## Coding Style & Naming Conventions
Follow existing Python style: 4-space indentation, `snake_case` for functions/modules, `CamelCase` for dataclasses and test classes. Preserve the established `Tm*`, `Ty*`, and `V*` naming in the Cajal AST. Prefer explicit types, dataclasses, and structural pattern matching over ad hoc dispatch. Keep comments sparse and technical. No formatter or linter is configured here, so match surrounding code closely and keep imports/readability tidy by hand.

## Testing Guidelines
Use `pytest`; numerical assertions should use tolerances such as `pytest.approx` when exact equality is unstable. Add regression tests for every semantic or compiler fix, especially around linear usage, type preservation, and tensor equality. Name files `tests/test_<area>.py`, test functions `test_<behavior>`, and keep example coverage in smoke-style tests when full training runs would be too slow.

## Commit & Pull Request Guidelines
Recent history uses short imperative subjects, sometimes with a scope prefix, for example `Add CI test workflow` or `docs: add internal review`. Keep commits focused on one concern. PRs should explain the problem, summarize the approach, list commands run (`just test`, targeted pytest, notebooks, docs build), and link any relevant issue or design note. Include plots or screenshots only when documentation, notebooks, or slides change.
