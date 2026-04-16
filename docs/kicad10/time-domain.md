# KiCad 10 Time-Domain Tuning

The following helpers were added for KiCad 10 style time-domain routing workflows:

- `route_create_tuning_profile(...)`
- `route_list_tuning_profiles()`
- `route_apply_tuning_profile(net_pattern, profile_name)`
- `route_tune_time_domain(net_or_group, target_delay_ps, tolerance_ps=10)`

## How It Works

Profile definitions are stored in `.kicad-mcp/tuning_profiles.json`. Target delays are also written into `.kicad_dru` as a length-based fallback rule so mixed KiCad 9/10 environments still get a practical constraint path.
