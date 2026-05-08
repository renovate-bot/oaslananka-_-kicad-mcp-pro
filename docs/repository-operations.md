# Repository Operations

## Repositories

- Canonical source-of-truth: `oaslananka-lab/kicad-mcp-pro`
- Personal showcase mirror: `oaslananka/kicad-mcp-pro`

The organization repository is the only source repository for CI/CD, release,
publishing, registry updates, package-manager updates, signing, SBOM generation,
and artifact attestations. The personal repository is a showcase mirror only.
If repository state differs, the organization repository wins.

## Showcase Mirror

The organization repository mirrors only `main` and version tags to the personal
showcase repository with `.github/workflows/mirror-personal.yml`.

Direction:

- `oaslananka-lab/kicad-mcp-pro` `main` branch to `oaslananka/kicad-mcp-pro` `main`
- `v*.*.*` tags from organization to personal showcase

The mirror does not sync pull request branches, release-please branches,
workflow run state, issues, or GitHub Releases. The mirror workflow uses
`PERSONAL_REPO_PUSH_TOKEN`, which must be scoped only to the personal showcase
repository. It does not use the default `GITHUB_TOKEN` for cross-repo writes.

## Actions Policy

Keep Actions enabled anywhere branch protection depends on them. Use least
privilege workflow permissions and protected environments rather than disabling
normal validation.

## Release Automation

Release automation is driven by `.github/workflows/release-please.yml` on
merges to `main`. Release-please opens the release pull request, derives the
SemVer version from Conventional Commits, creates the GitHub Release after the
release pull request is merged, and exposes the release version and tag to the
publish job.

Manual version inputs, manual tag creation, and hand-edited changelog entries
are not part of the release process.

## Maintenance Workflows

`.github/workflows/actions-maintenance.yml` can list and classify failed runs,
reports stale deployments/tags, and can rerun infra-only failures when
explicitly requested. It does not create releases, packages, tags, or mirror
force pushes.

References:

- [Failure classifier](automation/failure-classifier.md)
- [Review thread gate](automation/review-thread-gate.md)

## Mirror Recovery

1. Confirm `PERSONAL_REPO_PUSH_TOKEN` exists in the organization repository and
   has access only to `oaslananka/kicad-mcp-pro`.
2. Fix divergence through a reviewed repository maintenance change.
3. Let `.github/workflows/mirror-personal.yml` fast-forward `main` or add the
   missing release tag after CI is green.

## Pending: OIDC Trusted Publishing

The current release pipeline publishes with `pypa/gh-action-pypi-publish` and
GitHub Actions OIDC. Long-lived package-index tokens are not required by
`.github/workflows/release-please.yml`.

Migration path:
1. Configure a trusted publisher in the PyPI project settings pointing to
   `oaslananka-lab/kicad-mcp-pro`, workflow `release-please.yml`, environment `release`.
2. Configure the matching trusted publisher in TestPyPI with the same owner,
   repository, workflow, and environment.
3. Keep `id-token: write` on the release publish job so PyPI can mint short-lived
   publish credentials during the protected `release` environment run.
4. Remove any remaining package-index token secrets from the org repo after the
   PyPI trusted publisher is confirmed.

Blocked by: requires PyPI and TestPyPI account owner action to configure the
trusted publishers.

## Branch Cleanup

Review planned cleanup actions:

```bash
bash scripts/repo-cleanup.sh
```

Apply after reviewing the dry run:

```bash
bash scripts/repo-cleanup.sh --apply
```

The monthly `Branch hygiene report` workflow is report-only. It writes a job
summary and does not create issues or delete branches.

## Auto-Delete Merged PR Branches

Recommended one-time setting on the organization repository:

```bash
gh api -X PATCH /repos/oaslananka-lab/kicad-mcp-pro -f delete_branch_on_merge=true
```
