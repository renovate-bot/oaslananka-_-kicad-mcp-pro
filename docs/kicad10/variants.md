# KiCad 10 Variants

The `variant_*` tools build effective BOM variants from the active schematic and store their state in `.kicad-mcp/variants.json` inside the project.

## Tools

- `variant_list()` lists the known variants plus the default and active selections.
- `variant_create(name, base_variant=None)` creates a new variant or clones an existing one.
- `variant_set_active(name)` switches the active variant.
- `variant_set_component_override(...)` writes per-component enabled/value/footprint overrides.
- `variant_diff_bom(a, b)` returns a JSON BOM diff between two variants.
- `variant_export_bom(variant, format="csv")` writes a variant-specific BOM under `output/variants/`.

## Notes

This implementation keeps a sidecar representation aligned with KiCad 10 variant workflows. That approach remains safe in headless tests and on current CLI-only environments.
