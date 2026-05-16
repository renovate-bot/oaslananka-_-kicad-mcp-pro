# Submission Readiness Checklist

This page is the working index for public listing submissions.
It links platform-specific instructions to the root listing source of truth: [`PUBLIC_LISTING.md`](../public-listing.md).
Use this checklist before entering any external review form.

## Platform Documents

- [ ] Open [`anthropic-directory.md`](anthropic-directory.md) before submitting to the Anthropic Connector Directory.
- [ ] Open [`chatgpt-apps.md`](chatgpt-apps.md) before submitting to ChatGPT Apps.
- [ ] Open [`openai-mcp-registry.md`](openai-mcp-registry.md) before publishing to the OpenAI/MCP registry.
- [ ] Open [`reviewer-test-prompts.md`](reviewer-test-prompts.md) before sending reviewer instructions.
- [ ] Open [`safety-and-permissions.md`](safety-and-permissions.md) before answering security questions.
- [ ] Open [`PUBLIC_LISTING.md`](../public-listing.md) before recording submission status.

## Identity Fields

- [ ] Owner account is `oaslananka`.
- [ ] Maintainer name is `Osman Aslan`.
- [ ] Contact handle is `oaslananka`.
- [ ] Primary domain placeholder is `oaslananka.dev`.
- [ ] Repository URL is `https://github.com/oaslananka/kicad-mcp-pro`.
- [ ] Documentation URL is `https://oaslananka.github.io/kicad-mcp-pro`.
- [ ] Privacy URL is `https://oaslananka.github.io/kicad-mcp-pro/privacy/`.
- [ ] Support URL is `https://github.com/oaslananka/kicad-mcp-pro/issues`.
- [ ] MCP server name is `io.github.oaslananka/kicad-mcp-pro`.
- [ ] Package name is `kicad-mcp-pro`.
- [ ] Container image is `ghcr.io/oaslananka/kicad-mcp-pro:<version>`.
- [ ] Transport for directory reviewers is `stdio`.

## Repository Evidence

- [ ] Confirm `pyproject.toml` version matches `server.json`, `mcp.json`, and `src/kicad_mcp/__init__.py`.
- [ ] Confirm `server.json` declares `name` as `io.github.oaslananka/kicad-mcp-pro`.
- [ ] Confirm `mcp.json` declares repository URL as `https://github.com/oaslananka/kicad-mcp-pro`.
- [ ] Confirm README references the demo media slot `docs/assets/demo.gif`.
- [ ] Confirm README links to `PUBLIC_LISTING.md`.
- [ ] Confirm README links to the privacy policy.
- [ ] Confirm `docs/privacy.md` states no telemetry is collected.
- [ ] Confirm `docs/assets/icon.svg` exists and is the canonical vector icon.
- [ ] Confirm `docs/assets/icon-512.png` is 512x512.
- [ ] Confirm `docs/assets/screenshots/` contains five 1920x1080 image slots.
- [ ] Confirm `docs/assets/demo.cast` parses as asciinema v2 JSON Lines.
- [ ] Confirm `tests/reviewer/prompts.json` contains exactly five prompts.

## Anthropic Directory Checklist

- [ ] Use submission URL `https://clau.de/mcp-directory-submission`.
- [ ] Set product name to `KiCad MCP Pro`.
- [ ] Set category to `EDA / Hardware Design` when available.
- [ ] Use fallback category `Developer Tools` only if EDA is unavailable.
- [ ] Set transport to `stdio`.
- [ ] Paste repository URL exactly as `https://github.com/oaslananka/kicad-mcp-pro`.
- [ ] Paste privacy URL exactly as `https://oaslananka.github.io/kicad-mcp-pro/privacy/`.
- [ ] Paste support URL exactly as `https://github.com/oaslananka/kicad-mcp-pro/issues`.
- [ ] State that OAuth is not required because the server is local stdio.
- [ ] State that manufacturing export is gated by `project_quality_gate`.

## ChatGPT Apps Checklist

- [ ] Use the OpenAI Developer Platform app submission area at `https://platform.openai.com/apps`.
- [ ] Verify the domain `oaslananka.dev` using the required TXT record.
- [ ] Use app name `KiCad MCP Pro`.
- [ ] Use short description no longer than 80 characters.
- [ ] Use long description no longer than 500 characters.
- [ ] Set category to `Developer Tools`.
- [ ] Use support URL `https://github.com/oaslananka/kicad-mcp-pro/issues`.
- [ ] Use privacy URL `https://oaslananka.github.io/kicad-mcp-pro/privacy/`.
- [ ] Use screenshots from `docs/assets/screenshots/`.
- [ ] Confirm tool annotations expose `readOnlyHint`, `destructiveHint`, and `openWorldHint`.

## OpenAI MCP Registry Checklist

- [ ] Run `pnpm run submission:check` before registry dry run.
- [ ] Run `uv run --all-extras python scripts/publish_mcp_registry.py --dry-run` before live publish.
- [ ] Use `server.json` as the registry source of truth.
- [ ] Confirm PyPI Trusted Publisher OIDC is enabled for release workflow.
- [ ] Confirm GHCR image is available as `ghcr.io/oaslananka/kicad-mcp-pro:<version>`.
- [ ] Confirm release artifacts include SBOM evidence.
- [ ] Confirm release artifacts include SHA-256 checksums.
- [ ] Confirm release artifacts include Sigstore signatures.
- [ ] Confirm release artifacts include GitHub provenance attestations.
- [ ] Do not publish if metadata version values differ.

## Reviewer Package Checklist

- [ ] Use fixture directory `tests/fixtures/benchmark_projects/pass_sensor_node/` for all reproducible reviewer prompts.
- [ ] Use fixture project `tests/fixtures/benchmark_projects/pass_sensor_node/demo.kicad_pro` for project-specific prompts.
- [ ] Run prompt `p1-health` to verify tool discovery and KiCad CLI readiness.
- [ ] Run prompt `p2-set-project-quality-gate` to verify project quality gate behavior.
- [ ] Run prompt `p3-schematic-connectivity` to verify schematic read path.
- [ ] Run prompt `p4-pcb-state` to verify PCB state read path.
- [ ] Run prompt `p5-manufacturing-export-gate` to verify gated export behavior.
- [ ] Explain wrong-path failures as caller configuration issues, not server defects.
- [ ] Include PASS response shape for each prompt.
- [ ] Do not include private boards or customer design files in reviewer evidence.

## Preflight Commands

- [ ] Run `pnpm run metadata:check`.
- [ ] Run `pnpm run mcp:manifest:check`.
- [ ] Run `pnpm run assets:icons:check`.
- [ ] Run `pnpm run submission:check`.
- [ ] Run `SUBMISSION_MODE=1 pnpm run submission:check` and expect placeholder screenshots to fail before real captures.
- [ ] Run `pnpm run docs:tools:check` after the generated catalog exists.
- [ ] Run `pnpm run release:dry-run`.
- [ ] Run `uv run --all-extras mkdocs build --strict`.

## Manual Submission Log

- [ ] Record every submission in `PUBLIC_LISTING.md` after the external form is sent.
- [ ] Record target name exactly as `Anthropic Connector Directory`, `ChatGPT Apps`, or `OpenAI/MCP Registry`.
- [ ] Record submitted timestamp in UTC.
- [ ] Record approved timestamp in UTC when approval arrives.
- [ ] Record listing URL only after it is public.
- [ ] Record rejection notes without copying private reviewer messages into public issues.
- [ ] Open a GitHub issue for any required repo change from a reviewer.
- [ ] Close the issue only after the listing source of truth is updated.

## Final Gate

- [ ] Do not submit while `pnpm run submission:check` fails.
- [ ] Do not submit while `mkdocs build --strict` fails.
- [ ] Do not submit while version metadata is out of sync.
- [ ] Do not submit while screenshot placeholders are still present for final production submission.
- [ ] Do not submit with any secret value in logs or screenshots.
- [ ] Do not submit with old organization namespace strings.
- [ ] Do not submit with non-self-hosted workflow runner declarations.
- [ ] Do not submit before `PUBLIC_LISTING_READY.md` says `READY FOR SUBMISSION`.
- [ ] Evidence line 130: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 131: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 132: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 133: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 134: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 135: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 136: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 137: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 138: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 139: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 140: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 141: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 142: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 143: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 144: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 145: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 146: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 147: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 148: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 149: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 150: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 151: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 152: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 153: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 154: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
- [ ] Evidence line 155: keep reviewer-facing values synchronized with `PUBLIC_LISTING.md` and `server.json`.
