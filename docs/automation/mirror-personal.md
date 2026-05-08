# Personal Showcase Mirror

The canonical repository is:

```text
https://github.com/oaslananka-lab/kicad-mcp-pro
```

The personal showcase mirror is:

```text
https://github.com/oaslananka/kicad-mcp-pro
```

The personal repository is advisory and public-facing only. It is not a source
of truth for releases, package publishing, signing, registry updates, SBOMs, or
artifact attestations.

## What Mirrors

`mirror-personal.yml` mirrors only:

- `main`;
- `v*.*.*` tags.

It does not mirror pull request branches, release-please branches, issues,
workflow state, or GitHub Releases.

## Safe Default Behavior

Default automatic mode:

- fast-forwards personal `main` when safe;
- pushes missing version tags;
- refuses to clobber divergent tags;
- refuses non-fast-forward branch recovery.

Mirror failure must not invalidate a package release. A stale personal tag is a
showcase divergence, not a PyPI/TestPyPI build failure.

## Stale Tag Recovery

When the workflow reports:

```text
Personal showcase tag divergence detected.
```

review the canonical and personal refs first. If the organization repository is
confirmed canonical, repair the stale showcase ref through a reviewed
maintenance change. The mirror workflow does not perform force updates.
