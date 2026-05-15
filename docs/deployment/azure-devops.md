# Azure DevOps Manual CI/CD

Azure DevOps is a manual compatibility fallback surface for
teams that import this repository into Azure DevOps. Automated GitHub CI/CD is
owned by `oaslananka/kicad-mcp-pro`.

## Pipeline Definition

The compatibility Azure pipeline definitions live under `.azure/pipelines/`.
The canonical CI pipeline remains `.github/workflows/ci.yml`; Azure files are
not the authoritative project CI.

It covers:

- `Validate`: `uv sync`, `ruff`, `mypy`, and `pytest` with a `--cov-fail-under=70` gate
- `Build`: `uv build` and artifact publication for the generated `dist/` output

## Recommended Azure Variables

Preferred setup: store a single Doppler service token in Azure DevOps and let
the pipeline fetch scan-only secrets at runtime:

- `DOPPLER_TOKEN`

Doppler may contain:

- `SAFETY_API_KEY`

The compatibility Azure security pipeline still supports native Azure variables
as a fallback:

- `SAFETY_API_KEY`

You can store these in a variable group if you want to share them across multiple pipelines.

## Release Model

- Automated GitHub CI/security jobs should run from `https://github.com/oaslananka/kicad-mcp-pro`.
- Azure DevOps should be queued manually when you need the Azure validation path.
- Package publication is handled only by the GitHub release-please workflow.

## GitHub Workflows

The repository includes GitHub workflows that are automatic only in
`oaslananka/kicad-mcp-pro` and manual elsewhere:

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `.github/workflows/release-please.yml`

Release publishing is handled by `.github/workflows/release-please.yml`
through PyPI Trusted Publishing.
