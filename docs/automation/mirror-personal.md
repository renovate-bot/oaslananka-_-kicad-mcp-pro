# Personal And Organization Mirror

The personal repository is:

```text
https://github.com/oaslananka/kicad-mcp-pro
```

The organization repository is the CI/CD execution repository:

```text
https://github.com/oaslananka-lab/kicad-mcp-pro
```

GitHub Actions are disabled on the personal repository and enabled on the
organization repository. Release, publish, signing, registry, SBOM, and
artifact attestation jobs run only from the organization repository.

## What Mirrors

`mirror-personal.yml` mirrors organization-maintained refs back to the personal
repository after CI/CD has produced them:

- `main`;
- `gh-pages`;
- `v*.*.*` tags.

`release-please.yml` mirrors a created GitHub Release and its attached assets to
the personal repository after organization release verification and publishing
finish.

Pull requests and issues are kept clean at the active-work level: no open pull
requests or issues should remain in either repository after maintenance work is
complete.

## Safe Default Behavior

Default automatic mode:

- fast-forwards personal `main` and `gh-pages` when safe;
- pushes missing version tags;
- refuses to clobber divergent tags;
- refuses non-fast-forward branch recovery.

Mirror failure must not invalidate a package release after package publication.
A stale personal tag or release is a repository mirror divergence that must be
repaired with an audited maintenance change.

## Stale Tag Recovery

When the workflow reports:

```text
Personal showcase tag divergence detected.
```

review the organization and personal refs first. If the organization repository
is confirmed to contain the CI-verified content, repair the stale personal ref
through a reviewed maintenance change. The mirror workflow does not perform
force updates.
