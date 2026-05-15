# Operations: Required Human Actions

This file documents tasks that cannot be performed by an automated agent and require a
human operator with the appropriate permissions.

## PyPI Trusted Publishing Setup

Status: configure before the next protected release if it is not already active.

Required steps:

1. Go to https://pypi.org/manage/project/kicad-mcp-pro/settings/
2. Navigate to Publishing, then add a new publisher.
3. Select GitHub Actions.
4. Set owner to `oaslananka`, repository to `kicad-mcp-pro`, workflow name to
   `release-please.yml`, and environment to `release`.
5. Remove token-based PyPI secrets after Trusted Publishing is active.
6. Keep `.github/workflows/release-please.yml` on OIDC publishing with
   `id-token: write`.

## GitHub Protected Environment: release

Required steps:

1. Go to https://github.com/oaslananka/kicad-mcp-pro/settings/environments
2. Create an environment named `release`.
3. Add required reviewers, at minimum `@oaslananka`.
4. Enable the required reviewers gate.
5. Set deployment branch protection to `main` only.

## GitHub Protected Environment: docs

Create a `docs` protected environment with required reviewers for documentation deployment.

## Scorecard and Codecov Badges

Required steps:

1. Enable GitHub Actions on `oaslananka/kicad-mcp-pro`.
2. Verify README badges point at `oaslananka/kicad-mcp-pro`.

## Doppler Secret Rotation

When rotating secrets:

1. Update Doppler project `all`, config `main`.
2. Re-run the sync workflow in `oaslananka/kicad-mcp-pro`.
3. Verify no hardcoded secrets remain with `git log --all --full-history -- .env*`.

## KiCad 10 Smoke Test Runner Access

For the KiCad CLI smoke gate:

1. A self-hosted Linux X64 runner must be available with GitHub Actions labels
   `[self-hosted, Linux, X64]`.
2. The workflow downloads the KiCad 10.0.2 Linux AppImage and verifies its
   SHA-256 before invoking `kicad-cli`.
3. Set `KICAD_10_APPIMAGE_URL` only when overriding the default official
   AppImage URL.
4. Do not reintroduce PPA-based KiCad installation for this gate; the AppImage
   flow avoids stale apt source failures on the runner.
