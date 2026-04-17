# Phase 2 Summary

## What Changed

- Canonical project-spec persistence now goes through a single helper.
- Legacy `output/design_intent.json` reads now emit a one-time migration log.
- `kicad_set_project()` now fails closed when a directory contains only `.kicad_pro` without a board or schematic file.
- Design-intent schema gained:
  - `ComplianceTarget.extra_standards`
  - `ThermalEnvelope.ambient_airflow_m_s`
  - `RFKeepoutIntent.frequency_mhz`
  - `ProjectDesignIntent.functional_spacing_mm`
  - `ProjectDesignIntent.thermal_hotspots`
  - `ProjectDesignIntent.critical_frequencies_mhz`
- Well-known discovery now uses a server-card style payload on both routes.

## Validation

- `uv run python -m pytest tests/unit/test_wellknown_and_studio.py tests/unit/test_wellknown_schema.py -q`
- `uv run python -m pytest tests/unit/test_config.py tests/unit/test_runtime_helpers.py tests/unit/test_server_startup.py -q`

## Risks

- The full SEP-1649 schema is not vendored locally yet; current validation is structural and route-based.
- Deeper project-spec v1/v2/v3 round-trip coverage beyond the current regression surface remains a later-phase item.
