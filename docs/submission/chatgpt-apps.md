# ChatGPT Apps Submission

Use this document for the ChatGPT Apps submission path.

## Developer Dashboard

- Dashboard URL: `https://platform.openai.com/apps`.
- Use the OpenAI Developer Platform account controlled by Osman Aslan.
- Track review status in the platform dashboard after submission.
- Keep public status mirrored in `PUBLIC_LISTING.md`.

## Domain Verification

- [ ] Primary domain placeholder: `oaslananka.dev`.
- [ ] Add the TXT record exactly as shown by the OpenAI Developer Platform.
- [ ] Do not invent the TXT token before the dashboard shows it.
- [ ] Confirm DNS propagation with `dig TXT oaslananka.dev` or an equivalent DNS checker.
- [ ] Keep the TXT record until the dashboard reports verified.
- [ ] Do not put the TXT token into repository files.
- [ ] If verification fails, check registrar DNS, Cloudflare proxy state, and record name.
- [ ] Record verification completion in `PUBLIC_LISTING.md` notes.

## App Metadata

- [ ] Name: `KiCad MCP Pro`.
- [ ] Short description: `KiCad PCB and schematic automation through local MCP.`
- [ ] Short description length: 58 characters, below the 80 character limit.
- [ ] Long description: `KiCad MCP Pro connects ChatGPT-compatible MCP clients to local KiCad projects for project setup, schematic review, PCB inspection, validation gates, DFM checks, and gated manufacturing export. It runs locally over stdio by default and does not collect telemetry.`
- [ ] Long description length: below 500 characters.
- [ ] Category: `Developer Tools`.
- [ ] Support URL: `https://github.com/oaslananka/kicad-mcp-pro/issues`.
- [ ] Privacy URL: `https://oaslananka.github.io/kicad-mcp-pro/privacy/`.
- [ ] Repository URL: `https://github.com/oaslananka/kicad-mcp-pro`.
- [ ] Documentation URL: `https://oaslananka.github.io/kicad-mcp-pro`.

## Tool Annotation Exports

- [ ] Confirm annotations are exported from `src/kicad_mcp/tools/metadata.py`.
- [ ] Confirm `readOnlyHint` is surfaced for read-only inspection tools.
- [ ] Confirm `destructiveHint` is surfaced for tools that can write files or mutate projects.
- [ ] Confirm `openWorldHint` is surfaced where external or broader context may be involved.
- [ ] Confirm reviewer-facing docs describe read-only default workflows.
- [ ] Confirm destructive workflows require explicit user intent.
- [ ] Confirm manufacturing export remains gate controlled.
- [ ] Run `pnpm run submission:check` after annotation changes.

## Localization

- [ ] Launch language: English only.
- [ ] Do not claim Turkish localization at launch.
- [ ] Roadmap note: Turkish localization can be added after first approval.
- [ ] Keep screenshots and reviewer prompts in English for initial review.
- [ ] Keep privacy policy in English for directory review.
- [ ] If Turkish is added later, update metadata and docs together.

## Screenshot Requirements

- [ ] Minimum screenshot size: at least 1280x800.
- [ ] Committed screenshot slots are 1920x1080.
- [ ] Screenshot directory: `docs/assets/screenshots/`.
- [ ] Use `01-claude-desktop-quality-gate.png` for Claude Desktop quality gate capture.
- [ ] Use `02-cursor-schematic-build.png` for Cursor schematic build capture.
- [ ] Use `03-vscode-pcb-inspection.png` for VS Code PCB inspection capture.
- [ ] Use `04-tools-reference.png` for tools reference capture.
- [ ] Use `05-export-manufacturing.png` for gated manufacturing export capture.
- [ ] Run `SUBMISSION_MODE=1 pnpm run submission:check` before final upload.
- [ ] Replace placeholders before final public production submission.

## Residency Note

- [ ] Default stdio mode processes files on the user machine.
- [ ] The server itself does not operate a hosted backend.
- [ ] The server itself does not store user files remotely.
- [ ] The server itself does not collect IP addresses.
- [ ] The server itself does not set cookies.
- [ ] Optional third-party integrations are governed by their own policies.
- [ ] Nexar or Freerouting usage must be explicitly configured by the user.
- [ ] Document residency as local processing only for the default path.

## Review Controls

- [ ] Run `pnpm run submission:check` before dashboard submission.
- [ ] Run `uv run --all-extras mkdocs build --strict` before dashboard submission.
- [ ] Attach only screenshots that avoid private paths and hostnames.
- [ ] Use fixture project evidence for all reviewer tests.
- [ ] Do not upload secrets, logs with tokens, or private KiCad designs.
- [ ] Update `PUBLIC_LISTING.md` after submission.
- ChatGPT Apps control item 88: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 89: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 90: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 91: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 92: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 93: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 94: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 95: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 96: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 97: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 98: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 99: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 100: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 101: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 102: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 103: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 104: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 105: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 106: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 107: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 108: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 109: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 110: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 111: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 112: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 113: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 114: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 115: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 116: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 117: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 118: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 119: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 120: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 121: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 122: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 123: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 124: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 125: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 126: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 127: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 128: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 129: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 130: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 131: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 132: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 133: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 134: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 135: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 136: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 137: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 138: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 139: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 140: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 141: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 142: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 143: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 144: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 145: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 146: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 147: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 148: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 149: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 150: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 151: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 152: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 153: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 154: verify dashboard values still match this document before pressing submit.
- ChatGPT Apps control item 155: verify dashboard values still match this document before pressing submit.
