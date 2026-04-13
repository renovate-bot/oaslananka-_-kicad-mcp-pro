from __future__ import annotations

from kicad_mcp.utils.impedance import (
    differential_impedance,
    propagation_delay_ps_per_mm,
    recommended_decoupling_distance_mm,
    solve_spacing_for_differential_impedance,
    solve_width_for_impedance,
    trace_impedance,
    via_stub_resonance_ghz,
)


def test_microstrip_impedance_matches_expected_envelope() -> None:
    impedance_ohm, effective_er = trace_impedance(
        0.34,
        0.18,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
        spacing_mm=0.2,
    )

    assert 47.0 <= impedance_ohm <= 52.0
    assert 2.7 <= effective_er <= 3.6


def test_width_solver_rechecks_close_to_target() -> None:
    width_mm = solve_width_for_impedance(
        50.0,
        0.18,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
        spacing_mm=0.2,
    )
    impedance_ohm, _ = trace_impedance(
        width_mm,
        0.18,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
        spacing_mm=0.2,
    )

    assert 0.2 <= width_mm <= 0.5
    assert abs(impedance_ohm - 50.0) <= 0.25


def test_differential_spacing_solver_rechecks_close_to_target() -> None:
    width_mm = solve_width_for_impedance(
        50.0,
        0.18,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
        spacing_mm=0.2,
    )
    diff_width_mm = width_mm * 0.55
    spacing_mm = solve_spacing_for_differential_impedance(
        100.0,
        diff_width_mm,
        0.18,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
    )
    differential_ohm, _ = differential_impedance(
        diff_width_mm,
        0.18,
        spacing_mm,
        4.2,
        trace_type="microstrip",
        copper_oz=1.0,
    )

    assert 0.05 <= spacing_mm <= 0.5
    assert abs(differential_ohm - 100.0) <= 0.75


def test_via_stub_resonance_looks_reasonable() -> None:
    resonance_ghz = via_stub_resonance_ghz(1.6, er=4.0)

    assert 23.0 <= resonance_ghz <= 24.0


def test_propagation_delay_and_decoupling_heuristic_ranges() -> None:
    assert 5.7 <= propagation_delay_ps_per_mm(3.0) <= 5.9
    assert recommended_decoupling_distance_mm(50.0) == 10.0
    assert recommended_decoupling_distance_mm(250.0) == 2.0
    assert recommended_decoupling_distance_mm(2_000.0) == 0.5
