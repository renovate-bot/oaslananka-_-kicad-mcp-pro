# Phase 6 Summary

## Changed

- Extended `pcb_score_placement()` / placement gate internals with:
  - critical-net Manhattan proxy length,
  - proxy density normalized by board area,
  - thermal-hotspot proximity scoring.
- Fixed `resolve_design_intent()` merging so newer spec fields such as
  `functional_spacing_mm`, `thermal_hotspots`, and `critical_frequencies_mhz`
  are preserved in the resolved view used by downstream gates.
- Hardened `utils/placement.py` and `pcb_auto_place_force_directed()` with:
  - `max_seconds` wall-clock budget,
  - final `grid_mm` snapping,
  - deterministic seed-aware fallback search,
  - rectangular keepout-region hard constraints inside the placement loop.
- Hardened `utils/freerouting.py` and `route_autoroute_freerouting()` with:
  - pinned Docker image default (`ghcr.io/freerouting/freerouting:2.1.0`),
  - Docker-to-JAR fallback when Docker is unavailable,
  - FreeRouting 2.x flags (`-mp`, `-mt`, `--router.max_passes`, `-inc`, `-drc`),
  - `KICAD_MCP_FREEROUTING_TIMEOUT_SEC`,
  - structured routing telemetry (`routed_pct`, `total_nets`, `unrouted_nets`,
    `pass_count`, `wall_seconds`, `stdout_tail`, `ses_path`).
- Updated `docs/workflows/schematic-to-pcb.md` and `CHANGELOG.md` to describe the new placement behavior.

## Tests Added

- Added `tests/unit/test_placement.py` for deterministic force-directed placement and keepout handling.
- Added integration coverage for:
  - force-directed MCP tool keepout behavior,
  - critical-net placement proxy reporting,
  - thermal-hotspot proximity warnings.
- Added FreeRouting coverage for Docker command construction, JAR fallback, route
  telemetry parsing, and MCP tool output.

## Validation

- `uv run python -m ruff check src/ tests/`
- `uv run python -m mypy src/kicad_mcp/`
- `uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing`
- Baseline stayed green and total coverage rose to `82.11%`.

## Risks / Follow-ups

- The live FreeRouting CI fixture target (`4-layer 10-net board routes to >=95% in <=2 minutes`) remains conditional because this local environment does not provide Docker/FreeRouting runtime validation.
