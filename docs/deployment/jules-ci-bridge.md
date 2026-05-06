# Jules CI Bridge

This repository can run Jules against the canonical source repository while the
organization mirror remains the CI execution surface. The pattern is designed to
avoid the common loop where Jules opens a PR in a personal repository but cannot
see the failing organization CI checks.

## Topology

```text
Jules task
  -> opens or updates PR on oaslananka/kicad-mcp-pro
  -> org mirror syncs to oaslananka-lab/kicad-mcp-pro
  -> org CI runs
  -> publish-ci-status-to-personal.yml writes org CI status back to the personal commit
  -> Jules CI Fixer can see the failed status and push a fix commit
```

The canonical development repository remains `oaslananka/kicad-mcp-pro`. The lab
repository is the protected CI/release runner and mirror. Do not hand-edit the
lab mirror unless you are repairing the mirror machinery itself.

## Required configuration

Set these secrets/variables in `oaslananka-lab/kicad-mcp-pro`:

```text
PERSONAL_REPO_STATUS_TOKEN     fine-grained PAT for oaslananka/kicad-mcp-pro commit statuses
DOPPLER_GITHUB_SERVICE_TOKEN   existing mirror/sync token when mirror workflows need it
JULES_API_KEY                  only required for Jules API workflows
JULES_API_ENDPOINT             repository variable with the Jules session endpoint
```

Minimum permission for `PERSONAL_REPO_STATUS_TOKEN`:

```text
Repository: oaslananka/kicad-mcp-pro
Permissions:
- Metadata: read
- Commit statuses: read and write
```

## Workflows

### `publish-ci-status-to-personal.yml`

Runs on the lab mirror after the `CI` workflow completes. It writes a commit
status to the matching SHA in the personal repository with context
`org-mirror/ci`.

Manual recovery:

```bash
# Linux/macOS
gh workflow run publish-ci-status-to-personal.yml   --repo oaslananka-lab/kicad-mcp-pro   -f sha=<commit-sha>   -f state=failure   -f target_url=<actions-run-url>
```

```powershell
# Windows 11 PowerShell
gh workflow run publish-ci-status-to-personal.yml `
  --repo oaslananka-lab/kicad-mcp-pro `
  -f sha=<commit-sha> `
  -f state=failure `
  -f target_url=<actions-run-url>
```

### `jules-task.yml`

Manual workflow that starts a Jules task when the Jules API key and endpoint are
configured. Keep this workflow manual. It should not replace human review or the
protected CI gates.

### `jules-dependency-upgrade.yml`

Scheduled/manual dependency upgrade loop. It is intentionally skipped on the
schedule when the Jules API is not configured. Manual runs fail fast when the
secret or endpoint is missing.

## Test sequence

1. Create a small docs-only PR through Jules.
2. Confirm the PR appears in `oaslananka/kicad-mcp-pro`.
3. Confirm the lab mirror syncs the branch and runs CI.
4. Confirm the personal PR receives `org-mirror/ci` commit status.
5. Force a harmless CI failure in a temporary branch and verify Jules CI Fixer
   can see the failed status before attempting a fix.

## Security constraints

- Use fine-grained tokens with only the stated permissions.
- Never give Jules a broad account token.
- Keep release publishing credentials outside Jules workflows.
- CI Fixer may push fix commits, but merge remains branch-protected and human
  reviewed.
