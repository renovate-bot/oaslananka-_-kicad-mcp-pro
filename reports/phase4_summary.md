# Phase 4 Summary

## What changed

- Moved KiCad 10 variant persistence to the active `.kicad_pro` `variants` section when a project file is available, while keeping `.kicad-mcp/variants.json` as a fallback path.
- Forwarded the active design variant into compatible `kicad-cli` export commands through `--variant`.
- Replaced fragile string-based `.kicad_dru` editing with an S-expression-aware parser in `src/kicad_mcp/utils/dru.py`.
- Upgraded `route_tune_time_domain()` to derive delay-to-length targets from stackup context when a layer is supplied.
- Added `sch_set_hop_over()` to toggle KiCad 10 hop-over display in the active project settings.
- Tightened PCB KiCad 10 helpers:
  - `pcb_add_barcode()` now accepts `code128` in addition to `qr` and `datamatrix`.
  - `add_footprint_inner_layer_graphic()` now requires a stackup with at least four copper layers before writing inner-layer graphics.

## Files touched

- `src/kicad_mcp/tools/export.py`
- `src/kicad_mcp/tools/pcb.py`
- `src/kicad_mcp/tools/routing.py`
- `src/kicad_mcp/tools/schematic.py`
- `src/kicad_mcp/tools/validation.py`
- `src/kicad_mcp/tools/variants.py`
- `src/kicad_mcp/tools/router.py`
- `src/kicad_mcp/utils/dru.py`
- `README.md`
- `docs/kicad10/variants.md`
- `docs/kicad10/time-domain.md`
- `docs/kicad10/graphical-drc.md`
- `tests/unit/test_variant_diff.py`
- `tests/unit/test_variant_helpers.py`
- `tests/unit/test_kicad10_parity_tools.py`
- `tests/unit/test_dru_utils.py`
- `tests/unit/test_impedance.py`
- `tests/integration/test_export_tools.py`

## Tests added or extended

- `tests/unit/test_variant_helpers.py`
- `tests/unit/test_kicad10_parity_tools.py`
- `tests/unit/test_dru_utils.py`
- Extended `tests/unit/test_variant_diff.py`
- Extended `tests/unit/test_impedance.py`
- Extended `tests/integration/test_export_tools.py`

## Validation

- `uv run python -m ruff check src/ tests/`
- `uv run python -m mypy src/kicad_mcp/`
- `uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing`

## Coverage delta

- Before this phase tranche: `77.92%`
- After this phase tranche: `80.04%`

## Risks / follow-up

- This tranche closes the KiCad 10 parity surface that already existed in the repo skeleton. Later plan phases around SI/PI/EMC, DFM, simulation robustness, observability, and packaging are still separate work.
