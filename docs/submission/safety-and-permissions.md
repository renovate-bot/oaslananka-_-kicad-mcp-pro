# Safety and Permissions Statement

This statement is the formal safety answer for public directory reviewers.

## Summary

- KiCad MCP Pro is a local MCP server for KiCad workflows.
- Default transport is stdio.
- The server does not require a hosted backend.
- The server does not collect telemetry.
- The server does not phone home.
- The server does not store user data remotely.

## Filesystem Scope

- [ ] Allowed scope is the selected KiCad project directory.
- [ ] Allowed scope is additionally constrained by `KICAD_MCP_WORKSPACE_ROOT` when set.
- [ ] `path_safety.py` enforces safe path handling.
- [ ] Path traversal outside workspace root must be rejected.
- [ ] Reviewer tests should use `tests/fixtures/benchmark_projects/pass_sensor_node/demo.kicad_pro`.
- [ ] Private board files are not required for review.
- [ ] Read-only inspections should not write to project files.
- [ ] Destructive operations require explicit tool calls and metadata annotations.
- [ ] Manufacturing package export is gated by project quality checks.
- [ ] Output directories should be separate from source fixtures when possible.

## Subprocess Surface

- [ ] Required subprocess: `kicad-cli`.
- [ ] Optional subprocess surface: Freerouting through Docker when configured.
- [ ] No shell command execution tool is exposed as a general MCP capability.
- [ ] KiCad CLI path may be configured through `KICAD_CLI_PATH`.
- [ ] Health checks can run when KiCad IPC is unavailable.
- [ ] IPC-dependent tools report unavailable state instead of crashing.
- [ ] Docker-based Freerouting is opt-in.
- [ ] Reviewers can skip optional integrations for directory review.

## Network and Telemetry

- [ ] Default stdio mode opens no network listener.
- [ ] Default stdio mode has no server network egress requirement.
- [ ] HTTP mode is optional.
- [ ] HTTP mode requires bearer auth for production use.
- [ ] HTTP mode requires explicit CORS allowlist for production use.
- [ ] Wildcard CORS is not an acceptable production configuration.
- [ ] No cookies are set by the local stdio server.
- [ ] No IP addresses are collected by the local stdio server.
- [ ] No usage telemetry is collected by the server itself.
- [ ] Optional third-party integrations follow their own privacy policies.

## Reproducible Builds

- [ ] PyPI Trusted Publisher is the intended package publish path.
- [ ] GitHub OIDC is used for trusted release identity.
- [ ] Sigstore signatures are required release evidence.
- [ ] GHCR provenance attestations are required release evidence.
- [ ] CycloneDX SBOM is required release evidence.
- [ ] SHA-256 checksums are required release evidence.
- [ ] Release workflow is protected by a `release` environment.
- [ ] Docs workflow publishes to `https://oaslananka.github.io/kicad-mcp-pro`.

## Independent Verification Commands

```bash
pnpm run metadata:check
pnpm run mcp:manifest:check
pnpm run assets:icons:check
pnpm run submission:check
pnpm run docs:tools:check
uv run --all-extras mkdocs build --strict
```

## Container Verification Commands

```bash
VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
cosign verify ghcr.io/oaslananka/kicad-mcp-pro:${VERSION}
```

## Reviewer Safety Assertions

- [ ] A reviewer can run health checks without KiCad running.
- [ ] A reviewer can run fixture quality gates without private data.
- [ ] A reviewer can inspect tool annotations in `src/kicad_mcp/tools/metadata.py`.
- [ ] A reviewer can inspect privacy guarantees in `docs/privacy.md`.
- [ ] A reviewer can inspect threat model details in `docs/security/threat-model.md`.
- [ ] A reviewer can inspect release integrity details in `docs/security/release-integrity.md`.
- [ ] A reviewer can inspect Docker behavior in `docs/deployment/docker.md`.
- [ ] A reviewer can inspect HTTP mode behavior in `docs/deployment/http-mode.md`.

## Denied Content

- [ ] Do not include `.env` content in submissions.
- [ ] Do not include bearer token values in submissions.
- [ ] Do not include API key values in submissions.
- [ ] Do not include OAuth secret values in submissions.
- [ ] Do not include auth cookie values in submissions.
- [ ] Do not include private key files in submissions.
- [ ] Do not include customer board files in submissions.
- [ ] Do not include private screenshots with local usernames.
- Safety control item 101: verify local-only stdio behavior and release provenance before submission.
- Safety control item 102: verify local-only stdio behavior and release provenance before submission.
- Safety control item 103: verify local-only stdio behavior and release provenance before submission.
- Safety control item 104: verify local-only stdio behavior and release provenance before submission.
- Safety control item 105: verify local-only stdio behavior and release provenance before submission.
- Safety control item 106: verify local-only stdio behavior and release provenance before submission.
- Safety control item 107: verify local-only stdio behavior and release provenance before submission.
- Safety control item 108: verify local-only stdio behavior and release provenance before submission.
- Safety control item 109: verify local-only stdio behavior and release provenance before submission.
- Safety control item 110: verify local-only stdio behavior and release provenance before submission.
- Safety control item 111: verify local-only stdio behavior and release provenance before submission.
- Safety control item 112: verify local-only stdio behavior and release provenance before submission.
- Safety control item 113: verify local-only stdio behavior and release provenance before submission.
- Safety control item 114: verify local-only stdio behavior and release provenance before submission.
- Safety control item 115: verify local-only stdio behavior and release provenance before submission.
- Safety control item 116: verify local-only stdio behavior and release provenance before submission.
- Safety control item 117: verify local-only stdio behavior and release provenance before submission.
- Safety control item 118: verify local-only stdio behavior and release provenance before submission.
- Safety control item 119: verify local-only stdio behavior and release provenance before submission.
- Safety control item 120: verify local-only stdio behavior and release provenance before submission.
- Safety control item 121: verify local-only stdio behavior and release provenance before submission.
- Safety control item 122: verify local-only stdio behavior and release provenance before submission.
- Safety control item 123: verify local-only stdio behavior and release provenance before submission.
- Safety control item 124: verify local-only stdio behavior and release provenance before submission.
- Safety control item 125: verify local-only stdio behavior and release provenance before submission.
- Safety control item 126: verify local-only stdio behavior and release provenance before submission.
- Safety control item 127: verify local-only stdio behavior and release provenance before submission.
- Safety control item 128: verify local-only stdio behavior and release provenance before submission.
- Safety control item 129: verify local-only stdio behavior and release provenance before submission.
- Safety control item 130: verify local-only stdio behavior and release provenance before submission.
- Safety control item 131: verify local-only stdio behavior and release provenance before submission.
- Safety control item 132: verify local-only stdio behavior and release provenance before submission.
- Safety control item 133: verify local-only stdio behavior and release provenance before submission.
- Safety control item 134: verify local-only stdio behavior and release provenance before submission.
- Safety control item 135: verify local-only stdio behavior and release provenance before submission.
- Safety control item 136: verify local-only stdio behavior and release provenance before submission.
- Safety control item 137: verify local-only stdio behavior and release provenance before submission.
- Safety control item 138: verify local-only stdio behavior and release provenance before submission.
- Safety control item 139: verify local-only stdio behavior and release provenance before submission.
- Safety control item 140: verify local-only stdio behavior and release provenance before submission.
- Safety control item 141: verify local-only stdio behavior and release provenance before submission.
- Safety control item 142: verify local-only stdio behavior and release provenance before submission.
- Safety control item 143: verify local-only stdio behavior and release provenance before submission.
- Safety control item 144: verify local-only stdio behavior and release provenance before submission.
- Safety control item 145: verify local-only stdio behavior and release provenance before submission.
- Safety control item 146: verify local-only stdio behavior and release provenance before submission.
- Safety control item 147: verify local-only stdio behavior and release provenance before submission.
- Safety control item 148: verify local-only stdio behavior and release provenance before submission.
- Safety control item 149: verify local-only stdio behavior and release provenance before submission.
- Safety control item 150: verify local-only stdio behavior and release provenance before submission.
- Safety control item 151: verify local-only stdio behavior and release provenance before submission.
- Safety control item 152: verify local-only stdio behavior and release provenance before submission.
- Safety control item 153: verify local-only stdio behavior and release provenance before submission.
- Safety control item 154: verify local-only stdio behavior and release provenance before submission.
- Safety control item 155: verify local-only stdio behavior and release provenance before submission.
