# Azure DevOps CI/CD

Azure DevOps is the canonical CI/CD and release system for this repository. GitHub remains the source-hosting platform, but GitHub Actions in this repo are intentionally manual-only fallback workflows.

## Pipeline Definition

The primary pipeline definition lives in the repository root as `azure-pipelines.yml`.

It covers:

- `Validate`: `uv sync`, `ruff`, `mypy`, and `pytest` with a `--cov-fail-under=70` gate
- `Build`: `uv build` and artifact publication for the generated `dist/` output
- `Publish`: optional manual release to TestPyPI or PyPI using Azure-managed secrets

## Recommended Azure Variables

Create the following secret variables in Azure DevOps before enabling publish runs:

- `pypiToken`
- `testPyPIToken`

You can also store them in a variable group if you want to share them across multiple pipelines.

## Release Model

- Normal CI should run from Azure DevOps on pushes and pull requests.
- Package publication should be queued manually from Azure DevOps when you are ready to release.
- GitHub Actions should only be used as a manual fallback when Azure is temporarily unavailable.

## GitHub Fallback Workflows

The repository still includes manual-only GitHub workflows:

- `.github/workflows/ci.yml`
- `.github/workflows/security.yml`
- `.github/workflows/publish.yml`

These workflows are intentionally `workflow_dispatch` only and should not be treated as the primary delivery path.
