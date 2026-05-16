# Public Listing Readiness Report

**Status:** READY FOR SUBMISSION
**Date (UTC):** 2026-05-16T00:47:33Z
**Commit SHA:** f7d1ff781edf8b8fd0888cbaf94fb408ca82f932
**Branch:** chore/public-listing-readiness
**Version:** 3.4.3

## Final Acceptance Gate Results

| # | Check | Result |
|---|-------|--------|
| 1 | Namespace regression | PASS |
| 2 | Runner regression | PASS |
| 3 | Legacy doc tokens | PASS |
| 4 | Version metadata sync | PASS |
| 5 | MCP manifest schema | PASS |
| 6 | Icon assets | PASS |
| 7 | Submission readiness | PASS |
| 8 | Submission mode (informational) | placeholder screenshots present; expected pre-submission state |
| 9 | Lint | PASS |
| 10 | Typecheck | PASS |
| 11 | Unit tests | PASS |
| 12 | Docs build | PASS |
| 13 | Tools reference drift | PASS |
| 14 | Release dry-run | PASS |

## submission:check Output

```
.../Programs/Antigravity/resources/app   | [WARN] Unsupported engine: wanted: {"node":"22.20.0"} (current: {"node":"v24.15.0","pnpm":"11.0.8"})
.../resources/app/extensions/antigravity | [WARN] The field "resolutions" was found in C:\Users\Admin\AppData\Local\Application Data\Programs\Antigravity\resources\app\extensions\antigravity/package.json. This will not take effect. You should configure "resolutions" at the root of the workspace instead.
.../node/corepack/v1/yarn/1.22.22        | [WARN] The field "resolutions" was found in C:\Users\Admin\AppData\Local\Application Data\node\corepack\v1\yarn\1.22.22/package.json. This will not take effect. You should configure "resolutions" at the root of the workspace instead.
Already up to date
Done in 333ms using pnpm v11.0.8
$ uv run --all-extras python scripts/check_submission_readiness.py
| Check | Result | Detail |
|---|---|---|
| namespace regression | PASS | no forbidden owner strings |
| runner regression | PASS | no GitHub-hosted runner tokens |
| version metadata sync | PASS | 3.4.3 |
| pypi current version | PASS | 3.4.3 is published |
| privacy policy | PASS | privacy.md covers data and telemetry |
| icon assets | PASS | all icon sizes present |
| screenshot assets | PASS | all screenshot slots valid |
| demo cast | PASS | 13 frames |
| submission docs | PASS | six files at >=150 lines |
| reviewer prompts | PASS | five prompts |
| README listing references | PASS | demo and privacy linked |
| server schema | PASS | server.json validates |
| public listing | PASS | root listing file referenced |
| namespace regression | PASS | no forbidden owner strings |
| runner regression | PASS | no GitHub-hosted runner tokens |
```

## Next Steps for Maintainer

See `TALIMAT.md` for manual submission steps.

READY FOR SUBMISSION
