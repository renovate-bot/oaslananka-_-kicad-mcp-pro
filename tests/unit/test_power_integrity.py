from __future__ import annotations

from kicad_mcp.tools.power_integrity import (
    _ipc_current_capacity_a,
    _required_width_mm,
    _track_resistance_ohm,
)


def test_track_resistance_and_drop_are_reasonable() -> None:
    resistance_ohm = _track_resistance_ohm(0.5, 100.0, 1.0)

    assert 0.09 <= resistance_ohm <= 0.11


def test_ipc_current_capacity_helper_and_required_width_are_consistent() -> None:
    capacity_a = _ipc_current_capacity_a(
        0.5,
        0.035,
        external=True,
        max_temp_rise_c=10.0,
    )
    required_width_mm = _required_width_mm(
        1.0,
        0.035,
        external=True,
        max_temp_rise_c=10.0,
    )

    assert 0.8 <= capacity_a <= 1.6
    assert 0.2 <= required_width_mm <= 0.7
