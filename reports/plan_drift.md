# Plan Drift

## Phase 5

- The repository's bundled subcircuit templates live under `src/kicad_mcp/templates/subcircuits/` as YAML blueprints, not as standalone `.kicad_sch` files. The Phase 5 instruction to validate every template as a KiCad 10 schematic cannot be applied literally without first changing the template format.
- Byte-exact round-trip preservation for benchmark schematics is not currently satisfied by `kicad-sch-api` on the existing fixture corpus. A no-op load/save rewrites files into canonical expanded KiCad syntax, so full compliance will require either fixture canonicalization or a dedicated format-preservation layer beyond the current safe tranche.

## Release Gate

- The local validation baseline is green and the repository metadata has been
  bumped to `2.4.0`, but the branch has not been tagged, pushed, or published.
  Azure hosted validation and the manual PyPI publish stage must run outside
  this local workspace before a real `v2.4.0` release is cut.
- The full v2.4.0 master plan contains deeper fixture-backed engineering work
  that remains intentionally unsquashed into this tranche: PDN mesh solving,
  full SI/PI/EMC golden corpus, persisted gate history, per-tool metrics
  reservoirs, full sampling/elicitation roundtrips, DFM release-package signing,
  and live KiCad/FreeRouting/Docker validation.
