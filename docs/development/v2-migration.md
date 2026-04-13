# v2 Migration Notes

## Component Search Surface

The v2 library surface removes the legacy browser-URL helpers:

- `lib_get_lcsc_search_url`
- `lib_search_lcsc`

Use the live component tools instead:

- `lib_search_components`
- `lib_get_component_details`
- `lib_assign_lcsc_to_symbol`
- `lib_get_bom_with_pricing`
- `lib_check_stock_availability`
- `lib_find_alternative_parts`

### Default Source

`jlcsearch` is the default live source because it is zero-auth and works in the
standard local profile.

### Optional Sources

`nexar` and `digikey` require external credentials and are intended for
authenticated deployments.

## Simulation Surface

v2 also adds a dedicated SPICE simulation category:

- `sim_run_operating_point`
- `sim_run_ac_analysis`
- `sim_run_transient`
- `sim_run_dc_sweep`
- `sim_check_stability`
- `sim_add_spice_directive`

The preferred backend is `InSpice` when the `simulation` extra is installed.
When that path is unavailable, the server falls back to direct `ngspice` CLI
execution.

## Signal Integrity Surface

v2 adds a signal-integrity category focused on quick transmission-line and
placement checks:

- `si_calculate_trace_impedance`
- `si_calculate_trace_width_for_impedance`
- `si_check_differential_pair_skew`
- `si_validate_length_matching`
- `si_generate_stackup`
- `si_check_via_stub`
- `si_calculate_decoupling_placement`

These tools use quasi-static formulas and board heuristics so agents can make
better placement and routing decisions before a full SI review.
