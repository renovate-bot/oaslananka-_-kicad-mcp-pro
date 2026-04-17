# Phase 1 Summary

## What Changed

- Added `reports/` tracking artifacts required by the v2.4.0 execution plan.
- Hardened config parsing for `mount_path` and `cors_origins`.
- Added startup warning when bearer auth is configured for `stdio`.
- Replaced stale CLI capability caching with an mtime-aware cache.
- Fixed a studio watcher deadlock and added backoff/jitter behavior.
- Added sensitive-key log redaction.
- Upgraded well-known metadata to an SEP-1649-style server card payload.
- Added `agent_full` profile and experimental-tool discovery gating.
- Extended design-intent schema and canonical project-spec persistence.

## Files Touched

- `.gitignore`
- `.env.example`
- `README.md`
- `docs/deployment/http-mode.md`
- `src/kicad_mcp/config.py`
- `src/kicad_mcp/discovery.py`
- `src/kicad_mcp/models/intent.py`
- `src/kicad_mcp/server.py`
- `src/kicad_mcp/tools/project.py`
- `src/kicad_mcp/tools/router.py`
- `src/kicad_mcp/utils/logging.py`
- `src/kicad_mcp/wellknown.py`
- `tests/conftest.py`
- `tests/unit/test_config.py`
- `tests/unit/test_discovery_studio_watcher.py`
- `tests/unit/test_logging.py`
- `tests/unit/test_profile_matrix.py`
- `tests/unit/test_router_profiles.py`
- `tests/unit/test_runtime_helpers.py`
- `tests/unit/test_server_startup.py`
- `tests/unit/test_tool_metadata_lint.py`
- `tests/unit/test_wellknown_and_studio.py`
- `tests/unit/test_wellknown_schema.py`

## Tests Added

- `tests/unit/test_discovery_studio_watcher.py`
- `tests/unit/test_logging.py`
- `tests/unit/test_profile_matrix.py`
- `tests/unit/test_tool_metadata_lint.py`
- `tests/unit/test_wellknown_schema.py`

## Validation

- `uv run python -m ruff check src/ tests/`
- `uv run python -m mypy src/kicad_mcp/`
- `uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing`
- `uv run python -c "from kicad_mcp.server import build_server; s = build_server('full'); print('ok')"`
- `uv run kicad-mcp-pro --help`

## Coverage Delta

- Baseline: `77.35%`
- Current: `77.92%`

## Risks

- `KICAD_MCP_ENABLE_METRICS` is now a config knob, but the `/metrics` endpoint itself is still a later-phase task.
- Full per-tool metadata truthfulness still needs deeper tightening in later phases beyond the new profile/discovery coverage tests.
