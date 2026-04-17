# Phase 7 Summary

## Changed

- Extended `si_check_via_stub` so via-stub output includes critical-frequency
  resonance warnings when a stub resonance falls within 10 percent of a
  `ProjectDesignIntent.critical_frequencies_mhz` entry.
- Extended `thermal_calculate_via_count` with a backward-compatible
  package-envelope mode using `package_power_w`, `ambient_c`,
  `max_junction_c`, and `theta_ja_deg_c_w` while keeping the legacy `power_w`
  workflow.
- Extended `emc_check_return_path_continuity` so it can sweep design-intent
  critical nets automatically and return simple violation geometry hints.
- Added `docs/workflows/high-speed-review.md` and linked it from `mkdocs.yml`.

## Tests

- `uv run python -m ruff check src/kicad_mcp/tools/signal_integrity.py tests/integration/test_signal_integrity_tools.py`
- `uv run python -m mypy src/kicad_mcp/tools/signal_integrity.py`
- `uv run python -m pytest tests/integration/test_signal_integrity_tools.py -q`
- `uv run python -m ruff check src/kicad_mcp/models/power_integrity.py src/kicad_mcp/tools/power_integrity.py tests/integration/test_power_integrity_tools.py`
- `uv run python -m mypy src/kicad_mcp/models/power_integrity.py src/kicad_mcp/tools/power_integrity.py`
- `uv run python -m pytest tests/integration/test_power_integrity_tools.py -q`
- `uv run python -m ruff check src/kicad_mcp/tools/emc_compliance.py tests/integration/test_emc_tools.py`
- `uv run python -m mypy src/kicad_mcp/tools/emc_compliance.py`
- `uv run python -m pytest tests/integration/test_emc_tools.py -q`

## Risks

- The PDN mesh-solver and full fixture-backed SI/PI/EMC golden corpus from the
  larger v2.4.0 plan remain follow-up work; this phase closes the safest
  locally verifiable preflight upgrades without introducing new heavy
  dependencies.
