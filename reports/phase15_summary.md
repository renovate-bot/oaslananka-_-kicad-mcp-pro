# Phase 15 Summary

## Changed

- Bumped repository/package/registry metadata from `2.3.2` to `2.4.0` across
  `pyproject.toml`, `src/kicad_mcp/__init__.py`, `mcp.json`, `server.json`,
  `smithery.yaml`, and `uv.lock`.
- Collapsed the top-level changelog into a concrete `## [2.4.0] - 2026-04-17`
  release section instead of leaving an `Unreleased` bucket.
- Refreshed README/docs to call out the `2.4` release highlights, the new
  high-speed workflow page, and the extended version-control surface.
- Extended the version-control tool surface with `vcs_tag_release()` and safer
  restore/commit behavior.

## Tests

- `uv lock`
- `uv run python -m ruff check src/ tests/`
- `uv run python -m mypy src/kicad_mcp/`
- `uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing`
- `uv run python -c "from kicad_mcp.server import build_server; s = build_server('full'); print('ok')"`
- `uv run kicad-mcp-pro --help`
- `uv run python -m pip_audit --skip-editable --progress-spinner off`
- `"n" | uv run python -m safety scan --target . --output screen`

## Coverage

- Total coverage after the final sweep: `82.27%`

## Risks

- Local code and metadata are ready for a `2.4.0` cut, but the real release
  still depends on an external Azure validation run, a git tag/push, and the
  manual publish pipeline.
