# Repository and CI/CD Topology

This project uses one canonical GitHub repository for source, CI/CD, and
publishing:

- Canonical source and release authority: `https://github.com/oaslananka/kicad-mcp-pro`

The canonical repository owns code review, issues, security reporting,
release automation, package publishing, registry metadata, signing, SBOM output,
and artifact attestations.

## Trigger Policy

| Surface | Role | Trigger policy |
|---|---|---|
| GitHub (`oaslananka/kicad-mcp-pro`) | Canonical source and CI/CD owner | CI and security run on `push`/`pull_request`; publish remains guarded |
| Azure DevOps | Manual fallback and release support | Manual only |
| GitLab | Manual fallback import | Manual only |

CI/CD, publishing, registry, signing, package-manager, and release jobs keep
`github.repository == 'oaslananka/kicad-mcp-pro'` guards so copied workflow files
cannot publish from another repository.

## Recommended Remotes

Use explicit remotes so source pushes go to the canonical repository.

```bash
git remote add origin git@github.com:oaslananka/kicad-mcp-pro.git
git remote add azure git@ssh.dev.azure.com:v3/oaslananka/open-source/kicad-mcp-pro
```

If a GitLab import is used, add it as a separate manual remote:

```bash
git remote add gitlab <gitlab-repository-url>
```

## Publishing

PyPI, TestPyPI, GHCR, MCP registry, Homebrew, Scoop, npm wrapper, GitHub
Releases, SBOM, provenance, signing, and attestations are emitted only from
`oaslananka/kicad-mcp-pro`.

## Doppler Secrets

The recommended secret model is to store only `DOPPLER_TOKEN` in CI/CD systems and keep the actual release secrets in Doppler:

- PyPI Trusted Publishing configuration for workflow `release-please.yml` and
  environment `release`
- `SAFETY_API_KEY`
- `NPM_TOKEN`
- `OVSX_PAT`
- `VSCE_PAT`

GitHub workflows, Azure DevOps, and GitLab all use the same pattern: install the Doppler CLI, then execute sensitive commands through `doppler run -- ...` so Doppler injects secrets as environment variables at runtime.

Minimum setup:

- GitHub repository secret: `DOPPLER_TOKEN`
- GitHub repository secrets: `DOPPLER_PROJECT=all`, `DOPPLER_CONFIG=main`
- Azure DevOps secret variable or variable group entry: `DOPPLER_TOKEN`
- Azure DevOps variables: `DOPPLER_PROJECT=all`, `DOPPLER_CONFIG=main`
- GitLab CI/CD variable: `DOPPLER_TOKEN`
- GitLab CI/CD variables: `DOPPLER_PROJECT=all`, `DOPPLER_CONFIG=main`

Do not keep native package-index tokens in CI once GitHub trusted publishing is
configured. The canonical release workflow uses OIDC Trusted Publishing.
