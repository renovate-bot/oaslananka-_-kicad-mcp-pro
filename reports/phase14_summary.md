# Phase 14 Summary

## Changed

- Added a Windows validation job to the root Azure pipeline for ruff, mypy, and
  unit tests.
- Added `pip-audit` to the Ubuntu validation gate and an optional Safety scan
  when `SAFETY_API_KEY` is configured.
- Added `Dockerfile.kicad10` for CI images that extract `kicad-cli` from an
  official KiCad 10 AppImage URL supplied at build time.

## Tests

- YAML syntax was updated in `azure-pipelines.yml`; no Azure hosted run was
  queued from this local workspace.
- `uv run python -m pip_audit --skip-editable --progress-spinner off`
- `"n" | uv run python -m safety scan --target . --output screen`

## Risks

- Azure publish, registry verification, Docker image build/push, and final PyPI
  release remain manual release steps. The repository is not tagged or
  published by this local change.
