# Doppler Setup

This repository expects Doppler project `all`, config `main`.

## Manually Required GitHub Secret

Set exactly one GitHub secret manually in both repositories:

- `DOPPLER_TOKEN`

The token must be a read-only Doppler service token scoped to project `all`, config `main`.

Set it in:

- `oaslananka/kicad-mcp-pro`
- `oaslananka-lab/kicad-mcp-pro`

The organization repository may inherit the secret from the organization if that is easier to maintain.

Other secret names, including `DOPPLER_GITHUB_SERVICE_TOKEN`, `CODECOV_TOKEN`,
and `SAFETY_API_KEY`, may be present as GitHub Actions secrets at runtime.
Prefer projecting them into GitHub by Doppler GitHub Sync. Release publishing
uses PyPI Trusted Publishing and does not require long-lived PyPI tokens in
GitHub Actions.

## Doppler GitHub Sync

In the Doppler dashboard:

1. Open project `all`, config `main`.
2. Install the GitHub integration for both `oaslananka` and `oaslananka-lab`.
3. Create a sync to `oaslananka/kicad-mcp-pro` repository secrets.
4. Create a sync to `oaslananka-lab/kicad-mcp-pro` repository secrets.
5. Use replace mode so GitHub remains a projection of Doppler, not a second source of truth.

## Required Secrets

The authoritative secret-name list lives in this document rather than a dotfile
so scanner exclusions do not need to hide a `.doppler/` directory.

Current expected Doppler-backed names:

- `CODECOV_TOKEN`
- `DOPPLER_GITHUB_SERVICE_TOKEN`
- `SAFETY_API_KEY`

Usage:

- `CODECOV_TOKEN`: optional coverage upload token.
- `DOPPLER_GITHUB_SERVICE_TOKEN`: least-privilege GitHub service token for mirror synchronization and release-please PR creation when organization policy blocks `GITHUB_TOKEN` from opening pull requests.
- `SAFETY_API_KEY`: optional authenticated Safety scan. It is not required for local default gates.

Legacy local-only fallback names, not required by GitHub Actions after Trusted
Publishing migration:

- `PYPI_TOKEN`
- `TEST_PYPI_TOKEN`

The personal repository dispatcher also requires `ORG_SYNC_TOKEN` if immediate
`repository_dispatch` wakeups are enabled. That token only needs permission to
create `repository_dispatch` events on `oaslananka-lab/kicad-mcp-pro`; the org
repository's `DOPPLER_GITHUB_SERVICE_TOKEN` performs the actual mirror push.

No workflow or diagnostic output should print secret values.

## Verification

```bash
bash scripts/verify_doppler_secrets.sh
```

This command requires the Doppler CLI and a local login or `DOPPLER_TOKEN`.
