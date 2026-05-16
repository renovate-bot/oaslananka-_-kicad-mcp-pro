# OpenAI MCP Registry Submission

This document covers the registry publish path driven by `server.json`.

## Source of Truth

- Use `server.json` as the single source of truth for registry metadata.
- Do not hand-edit registry payloads after generation.
- Keep `mcp.json` synchronized with `server.json` and `pyproject.toml`.
- Version must match `src/kicad_mcp/__init__.py`.

## Dry Run Flow

- [ ] Run `pnpm run submission:check` first.
- [ ] Run `uv run --all-extras python scripts/publish_mcp_registry.py --dry-run`.
- [ ] Inspect the dry-run payload for repository URL correctness.
- [ ] Inspect the dry-run payload for privacy URL correctness.
- [ ] Inspect the dry-run payload for package identifiers.
- [ ] Inspect the dry-run payload for transport type `stdio`.
- [ ] Stop if dry-run output contains old owner strings.
- [ ] Stop if dry-run output contains a container image outside GHCR canonical namespace.

## Live Publish Flow

- [ ] Run live publish only after dry-run output is reviewed.
- [ ] Use the maintainer account controlled by Osman Aslan.
- [ ] Record live publish UTC timestamp in `PUBLIC_LISTING.md`.
- [ ] Record registry response URL in `PUBLIC_LISTING.md` only after it is public.
- [ ] Do not publish from a dirty working tree.
- [ ] Do not publish with placeholder screenshots if the registry requires production media.

## PyPI Trusted Publisher OIDC

- [ ] Confirm PyPI project name is `kicad-mcp-pro`.
- [ ] Confirm workflow is `release-please.yml`.
- [ ] Confirm release environment is `release`.
- [ ] Confirm owner is `oaslananka`.
- [ ] Confirm repository is `kicad-mcp-pro`.
- [ ] Confirm OIDC `id-token: write` remains configured for release publish.
- [ ] Remove token-based PyPI secrets after Trusted Publishing is active.
- [ ] Do not paste PyPI credentials into registry forms or docs.

## Container Image Verification

- [ ] Image pattern: `ghcr.io/oaslananka/kicad-mcp-pro:<version>`.
- [ ] Use the version from `pyproject.toml`.
- [ ] Verify digest before announcing a release.
- [ ] Verify provenance before announcing a release.
- [ ] Do not publish DockerHub coordinates because DockerHub is not enabled.
- [ ] Do not publish old GHCR namespace coordinates.

## Cosign Verification Snippet

```bash
VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")
cosign verify ghcr.io/oaslananka/kicad-mcp-pro:${VERSION} \
  --certificate-identity-regexp "https://github.com/oaslananka/kicad-mcp-pro/.github/workflows/.*" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com
```

## Registry Metadata Checks

- [ ] Check `server.json` schema before publish.
- [ ] Check package registry entry `kicad-mcp-pro` before publish.
- [ ] Check OCI package identifier before publish.
- [ ] Check website URL before publish.
- [ ] Check license value `MIT` before publish.
- [ ] Check capabilities include tools.
- [ ] Check capabilities include resources.
- [ ] Check capabilities include prompts.

## Failure Handling

- [ ] If schema validation fails, fix `server.json` and rerun `metadata:check`.
- [ ] If PyPI version is missing, stop until release publication completes.
- [ ] If GHCR image is missing, stop until container publication completes.
- [ ] If cosign verification fails, treat release as blocked.
- [ ] If registry rejects metadata, open a GitHub issue with the exact rejected field.
- [ ] If network is offline, treat PyPI reachability as warning-only in local checks.
- Registry control item 80: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 81: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 82: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 83: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 84: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 85: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 86: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 87: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 88: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 89: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 90: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 91: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 92: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 93: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 94: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 95: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 96: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 97: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 98: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 99: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 100: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 101: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 102: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 103: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 104: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 105: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 106: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 107: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 108: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 109: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 110: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 111: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 112: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 113: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 114: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 115: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 116: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 117: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 118: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 119: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 120: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 121: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 122: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 123: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 124: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 125: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 126: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 127: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 128: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 129: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 130: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 131: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 132: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 133: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 134: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 135: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 136: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 137: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 138: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 139: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 140: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 141: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 142: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 143: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 144: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 145: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 146: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 147: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 148: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 149: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 150: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 151: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 152: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 153: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 154: keep publish evidence tied to `server.json` and the current release version.
- Registry control item 155: keep publish evidence tied to `server.json` and the current release version.
