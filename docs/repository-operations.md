# Repository Operations

## Repositories

- Canonical: `oaslananka/kicad-mcp-pro`
- CI/CD mirror: `oaslananka-lab/kicad-mcp-pro`

The canonical repository is the public source of truth. The lab repository can
still run protected release and mirror automation, but normal CI and security
checks are expected to run on pull requests, pushes, and merge queue events.

## Synchronization

The lab repository pulls from canonical every 15 minutes with `.github/workflows/sync-from-canonical.yml`.

Direction:

- Branches and tags: canonical to lab
- GitHub Releases and release assets: lab to canonical

Normal CI, lint, test, docs, CodeQL, Gitleaks, Trivy, and workflow-security jobs
must not be skipped by stale repository guards. Release, publish, mirroring,
deployment, and issue/label mutation jobs remain explicitly guarded.

## Actions Policy

Keep Actions enabled anywhere branch protection depends on them. Use least
privilege workflow permissions and protected environments rather than disabling
normal validation.

## Manual Sync

Use this only if the scheduled lab pull is unavailable:

```bash
bash scripts/sync-remotes.sh main
```

```powershell
.\scripts\sync-remotes.ps1 -Branch main
```

Both scripts require a clean working tree.

## Mirror Recovery

1. Confirm `DOPPLER_GITHUB_SERVICE_TOKEN` exists in Doppler and is synced to the lab repository.
2. Run `.github/workflows/sync-from-canonical.yml` manually in `oaslananka-lab/kicad-mcp-pro`.
3. If the workflow is unavailable, run the manual sync helper from a clean local clone.
4. Re-run lab CI on the mirrored branch.

## Release Artifact Back-Mirror

The `Mirror releases back to canonical` workflow republishes lab GitHub Releases to canonical. It uses `DOPPLER_GITHUB_SERVICE_TOKEN`.

## Pending: OIDC Trusted Publishing

The current release pipeline publishes with `pypa/gh-action-pypi-publish` and
GitHub Actions OIDC. Long-lived PyPI tokens (`PYPI_TOKEN`, `TEST_PYPI_TOKEN`)
are not required by `.github/workflows/release.yml`.

Migration path:
1. Configure a trusted publisher in the PyPI project settings pointing to
   `oaslananka-lab/kicad-mcp-pro`, workflow `release.yml`, environment `release`.
2. Configure the matching trusted publisher in TestPyPI with the same owner,
   repository, workflow, and environment.
3. Keep `id-token: write` on the release workflow so PyPI can mint short-lived
   publish credentials during the protected `release` environment run.
4. Remove any remaining `PYPI_TOKEN` and `TEST_PYPI_TOKEN` secrets from the org
   repo after TestPyPI and PyPI trusted publishers are confirmed.

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

The monthly `Branch hygiene report` workflow is report-only. It opens or updates an issue and does not delete branches.

## Auto-Delete Merged PR Branches

Recommended one-time setting on canonical:

```bash
gh api -X PATCH /repos/oaslananka/kicad-mcp-pro -f delete_branch_on_merge=true
```
