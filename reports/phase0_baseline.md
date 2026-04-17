# Phase 0 Baseline

Repository base for `release/v2.4.0` is current `main` commit `e3afd80`.

## Commands Run

```bash
uv sync --all-extras --python 3.12
uv run python -m ruff check src/ tests/
uv run python -m mypy src/kicad_mcp/
uv run python -m pytest tests/unit/ tests/integration/ tests/e2e/ -q --cov=kicad_mcp --cov-report=term-missing
uv run python -c "from kicad_mcp.server import build_server; s = build_server('full'); print('ok')"
uv run kicad-mcp-pro --help
```

## Result

- All baseline commands were green on the starting point.
- Coverage baseline on current `main`: `77.35%`.
- `build_server('full')` completed successfully.
- CLI help rendered successfully.

## Starting Surface

- Profiles: `14`
- Categories: `16`
- Unique tools: `241`
