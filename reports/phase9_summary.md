# Phase 9 Summary

## Changed

- Added ngspice directive prefix validation to `sim_add_spice_directive`.
- Kept existing `.ac`, `.tran`, and `.dc` directive workflows accepted for
  backward compatibility with current tests and user projects.

## Tests

- `uv run python -m ruff check src/kicad_mcp/tools/simulation.py tests/integration/test_simulation_tools.py tests/e2e/test_professional_workflows.py`
- `uv run python -m mypy src/kicad_mcp/tools/simulation.py`
- `uv run python -m pytest tests/integration/test_simulation_tools.py tests/e2e/test_professional_workflows.py -q`

## Risks

- Full transient non-convergence retry fixtures and ngspice golden-value circuit
  coverage remain follow-up work; this phase closes the sidecar validation item
  without changing the default ngspice CLI backend.
