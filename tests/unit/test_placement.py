from __future__ import annotations

from kicad_mcp.utils.placement import (
    ForceDirectedConfig,
    PlacementComponent,
    PlacementNet,
    force_directed_placement,
)


def test_force_directed_placement_is_deterministic_and_snaps_to_grid() -> None:
    components = [
        PlacementComponent(ref="J1", x=2.0, y=2.0, w=3.0, h=3.0),
        PlacementComponent(ref="U1", x=18.0, y=8.0, w=4.0, h=4.0),
        PlacementComponent(ref="U2", x=32.0, y=18.0, w=4.0, h=4.0),
    ]
    nets = [PlacementNet(name="USB_DP", refs=["J1", "U1", "U2"], weight=1.0)]
    cfg = ForceDirectedConfig(
        iterations=80,
        board_w=40.0,
        board_h=25.0,
        grid_mm=1.0,
        seed=7,
    )

    first = force_directed_placement(components, nets, cfg)
    second = force_directed_placement(components, nets, cfg)

    assert [(item.ref, item.x, item.y) for item in first] == [
        (item.ref, item.x, item.y) for item in second
    ]
    assert all(item.x == round(item.x) for item in first)
    assert all(item.y == round(item.y) for item in first)


def test_force_directed_placement_respects_keepout_regions() -> None:
    components = [PlacementComponent(ref="U1", x=15.0, y=10.0, w=4.0, h=4.0)]
    cfg = ForceDirectedConfig(
        iterations=20,
        board_w=30.0,
        board_h=20.0,
        grid_mm=0.5,
        keepout_regions=[(12.0, 8.0, 18.0, 12.0)],
    )

    placed = force_directed_placement(components, [], cfg)[0]

    assert 0.0 <= placed.x - 2.0
    assert placed.x + 2.0 <= 30.0
    assert 0.0 <= placed.y - 2.0
    assert placed.y + 2.0 <= 20.0
    assert (
        placed.x + 2.0 <= 12.0
        or placed.x - 2.0 >= 18.0
        or placed.y + 2.0 <= 8.0
        or placed.y - 2.0 >= 12.0
    )
