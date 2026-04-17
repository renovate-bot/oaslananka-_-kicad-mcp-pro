# Phase 3 Summary

## What Changed

- Added the `agent_full` profile as a discovery-visible superset profile.
- Extended `high_speed` to include `simulation` and `version_control`.
- Populated `EXPERIMENTAL_TOOL_NAMES` for unstable schematic-facing helpers.
- Server-side `list_tools()` now filters by:
  - the active profile’s declared tool surface
  - experimental-tool visibility
- Removed stale export-category declarations for `run_drc`, `run_erc`, and `validate_design`, which already belong to validation.

## Tests Added

- `tests/unit/test_profile_matrix.py`
- `tests/unit/test_tool_metadata_lint.py`

## Validation

- `uv run python -m pytest tests/unit/test_router_profiles.py tests/unit/test_profile_matrix.py tests/unit/test_tool_metadata_lint.py -q`
- `uv run kicad-mcp-pro --help`

## Risks

- Tool metadata truthfulness is improved at the profile/discovery level, but richer per-tool runtime labels still need deeper tightening in later phases.
