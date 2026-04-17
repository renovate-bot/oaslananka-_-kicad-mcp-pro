# Phase 5 Summary

## Changed

- Added pin-aware bounding boxes in `src/kicad_mcp/tools/schematic.py` so `sch_get_bounding_boxes()` now includes symbol pin extents instead of center-only heuristics.
- Extended `sch_find_free_placement()` with rectangular `keepout_regions` support.
- Extended `sch_auto_place_functional()` with `anchor_ref` support and project-spec-driven `functional_spacing_mm`.
- Expanded `sch_get_template_info()` so each bundled YAML template now shows declared left/right pin lists.
- Updated `docs/workflows/schematic-to-pcb.md` and `CHANGELOG.md` to describe the new schematic placement behavior.

## Tests Added

- Added schematic integration coverage for:
  - pin-aware bounding boxes,
  - keepout-aware free placement,
  - anchored functional auto-placement,
  - design-intent spacing in functional auto-placement,
  - template pin-list reporting.

## Validation

- `uv run python -m ruff check src/ tests/`
- `uv run python -m mypy src/kicad_mcp/`
- `uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing`
- Baseline stayed green and total coverage rose to `81.28%`.

## Risks / Follow-ups

- Byte-exact KiCad 10 schematic round-trip remains unresolved and is tracked in `reports/plan_drift.md`.
