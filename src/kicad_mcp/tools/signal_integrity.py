"""Signal-integrity helpers for trace impedance, skew, and placement heuristics."""

from __future__ import annotations

import math
from typing import Protocol, cast

from kipy.proto.board.board_types_pb2 import ViaType
from mcp.server.fastmcp import FastMCP

from ..config import get_config
from ..connection import get_board
from ..models.common import _FootprintLike, _PadLike
from ..models.signal_integrity import (
    DecouplingPlacementInput,
    DifferentialPairSkewInput,
    LengthMatchingInput,
    StackupInput,
    TraceImpedanceInput,
    TraceWidthForImpedanceInput,
    ViaStubInput,
)
from ..utils.impedance import (
    copper_thickness_mm,
    differential_impedance,
    propagation_delay_ps_per_mm,
    recommended_decoupling_distance_mm,
    solve_spacing_for_differential_impedance,
    solve_width_for_impedance,
    trace_impedance,
    via_stub_resonance_ghz,
    via_stub_risk_level,
)
from ..utils.units import _coord_nm, nm_to_mm

_DEFAULT_OUTER_DIELECTRIC_MM = 0.18
_DEFAULT_BOARD_THICKNESS_MM = 1.6


class _TrackLike(Protocol):
    start: object
    end: object
    width: int
    net: object


class _ViaLike(Protocol):
    position: object
    drill_diameter: int
    net: object
    type: int


def _track_length_mm(track: _TrackLike) -> float:
    dx = _coord_nm(track.end, "x") - _coord_nm(track.start, "x")
    dy = _coord_nm(track.end, "y") - _coord_nm(track.start, "y")
    return math.hypot(dx, dy) / 1_000_000.0


def _track_lengths_by_net() -> dict[str, float]:
    lengths: dict[str, float] = {}
    for track in cast(list[_TrackLike], list(get_board().get_tracks())):
        net_name = str(getattr(getattr(track, "net", None), "name", "") or "")
        if not net_name:
            continue
        lengths[net_name] = lengths.get(net_name, 0.0) + _track_length_mm(track)
    return lengths


def _track_width_mm(net_name: str) -> float | None:
    widths: list[float] = []
    for track in cast(list[_TrackLike], list(get_board().get_tracks())):
        track_net = str(getattr(getattr(track, "net", None), "name", "") or "")
        if track_net == net_name:
            widths.append(nm_to_mm(int(getattr(track, "width", 0))))
    if not widths:
        return None
    return sum(widths) / len(widths)


def _stackup_layers() -> list[object]:
    stackup = get_board().get_stackup()
    return list(getattr(stackup, "layers", []))


def _is_copper_layer(layer: object) -> bool:
    material = str(getattr(layer, "material_name", "") or "").casefold()
    if material == "copper":
        return True
    layer_name = str(getattr(layer, "layer", ""))
    return "Cu" in layer_name


def _outer_dielectric_height_mm() -> float:
    layers = _stackup_layers()
    seen_outer_copper = False
    for layer in layers:
        if _is_copper_layer(layer) and not seen_outer_copper:
            seen_outer_copper = True
            continue
        if seen_outer_copper and not _is_copper_layer(layer):
            thickness_nm = int(getattr(layer, "thickness", 0))
            if thickness_nm > 0:
                return nm_to_mm(thickness_nm)
    return _DEFAULT_OUTER_DIELECTRIC_MM


def _board_thickness_mm() -> float:
    thickness_nm = 0
    for layer in _stackup_layers():
        thickness_nm += int(getattr(layer, "thickness", 0))
    if thickness_nm <= 0:
        return _DEFAULT_BOARD_THICKNESS_MM
    return nm_to_mm(thickness_nm)


def _board_footprints() -> list[_FootprintLike]:
    return cast(list[_FootprintLike], list(get_board().get_footprints()))


def _board_pads() -> list[_PadLike]:
    return cast(list[_PadLike], list(get_board().get_pads()))


def _footprint_reference(footprint: _FootprintLike) -> str:
    return str(footprint.reference_field.text.value)


def _footprint_value(footprint: _FootprintLike) -> str:
    return str(footprint.value_field.text.value)


def _footprint_position_mm(footprint: _FootprintLike) -> tuple[float, float]:
    return (
        nm_to_mm(_coord_nm(footprint.position, "x")),
        nm_to_mm(_coord_nm(footprint.position, "y")),
    )


def _find_footprint(reference: str) -> _FootprintLike | None:
    for footprint in _board_footprints():
        if _footprint_reference(footprint) == reference:
            return footprint
    return None


def _find_power_anchor(ic_ref: str, power_pin: str) -> tuple[float, float]:
    for pad in _board_pads():
        if _footprint_reference(pad.parent) == ic_ref and str(pad.number) == power_pin:
            return (
                nm_to_mm(_coord_nm(pad.position, "x")),
                nm_to_mm(_coord_nm(pad.position, "y")),
            )

    footprint = _find_footprint(ic_ref)
    if footprint is None:
        raise ValueError(f"Footprint '{ic_ref}' was not found on the active board.")
    return _footprint_position_mm(footprint)


def _nearest_capacitors(
    source_ref: str,
    source_x_mm: float,
    source_y_mm: float,
) -> list[tuple[str, float, str]]:
    matches: list[tuple[str, float, str]] = []
    for footprint in _board_footprints():
        reference = _footprint_reference(footprint)
        if reference == source_ref or not reference.upper().startswith("C"):
            continue
        x_mm, y_mm = _footprint_position_mm(footprint)
        distance_mm = math.hypot(source_x_mm - x_mm, source_y_mm - y_mm)
        matches.append((reference, distance_mm, _footprint_value(footprint)))
    return sorted(matches, key=lambda item: item[1])


def _via_position_mm(via: _ViaLike) -> tuple[float, float]:
    position = via.position
    return (
        nm_to_mm(_coord_nm(position, "x")),
        nm_to_mm(_coord_nm(position, "y")),
    )


def _selected_vias(via_positions: list[tuple[float, float]]) -> list[_ViaLike]:
    vias: list[_ViaLike] = cast(list[_ViaLike], list(get_board().get_vias()))
    if not via_positions:
        return list(vias)

    selected: list[_ViaLike] = []
    for via in vias:
        x_mm, y_mm = _via_position_mm(via)
        for target_x_mm, target_y_mm in via_positions:
            if math.hypot(x_mm - target_x_mm, y_mm - target_y_mm) <= 0.5:
                selected.append(via)
                break
    return selected


def _via_stub_length_mm(via: _ViaLike) -> float:
    via_type = int(getattr(via, "type", ViaType.VT_THROUGH))
    board_thickness_mm = _board_thickness_mm()
    if via_type == ViaType.VT_MICRO:
        return board_thickness_mm * 0.2
    if via_type == ViaType.VT_BLIND_BURIED:
        return board_thickness_mm * 0.5
    return board_thickness_mm


def _format_impedance_result(
    *,
    title: str,
    trace_type: str,
    width_mm: float,
    height_mm: float,
    er: float,
    copper_oz: float,
    impedance_ohm: float,
    effective_er: float,
    spacing_mm: float | None = None,
    differential_ohm: float | None = None,
) -> str:
    lines = [
        title,
        f"- Trace type: {trace_type}",
        f"- Width: {width_mm:.4f} mm",
        f"- Dielectric height: {height_mm:.4f} mm",
        f"- Copper: {copper_oz:.2f} oz ({copper_thickness_mm(copper_oz):.4f} mm)",
        f"- Relative permittivity (Er): {er:.3f}",
        f"- Effective permittivity: {effective_er:.3f}",
        f"- Estimated single-ended impedance: {impedance_ohm:.2f} ohm",
    ]
    if spacing_mm is not None:
        lines.append(f"- Gap / spacing: {spacing_mm:.4f} mm")
    if differential_ohm is not None:
        lines.append(f"- Estimated differential impedance: {differential_ohm:.2f} ohm")
    return "\n".join(lines)


def _stackup_templates(manufacturer: str, layer_count: int) -> list[dict[str, str | float]]:
    normalized = manufacturer.casefold()
    if normalized == "pcbway":
        templates: dict[int, list[dict[str, str | float]]] = {
            2: [
                {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
                {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 1.53},
                {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            ],
            4: [
                {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
                {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.17},
                {
                    "name": "In1.Cu",
                    "role": "ground plane",
                    "material": "Copper",
                    "thickness_mm": 0.018,
                },
                {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 1.124},
                {
                    "name": "In2.Cu",
                    "role": "power / signal",
                    "material": "Copper",
                    "thickness_mm": 0.018,
                },
                {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.17},
                {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            ],
            6: [
                {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
                {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.11},
                {
                    "name": "In1.Cu",
                    "role": "ground plane",
                    "material": "Copper",
                    "thickness_mm": 0.018,
                },
                {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.35},
                {"name": "In2.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.018},
                {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.65},
                {
                    "name": "In3.Cu",
                    "role": "power plane",
                    "material": "Copper",
                    "thickness_mm": 0.018,
                },
                {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.35},
                {
                    "name": "In4.Cu",
                    "role": "ground plane",
                    "material": "Copper",
                    "thickness_mm": 0.018,
                },
                {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.11},
                {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            ],
        }
        return templates[layer_count]

    templates = {
        2: [
            {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 1.53},
            {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
        ],
        4: [
            {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.18},
            {
                "name": "In1.Cu",
                "role": "solid GND plane",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 1.114},
            {
                "name": "In2.Cu",
                "role": "power / signal",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.18},
            {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
        ],
        6: [
            {"name": "F.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
            {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.11},
            {
                "name": "In1.Cu",
                "role": "solid GND plane",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.33},
            {
                "name": "In2.Cu",
                "role": "high-speed signal",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.62},
            {
                "name": "In3.Cu",
                "role": "power plane",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Core", "role": "dielectric", "material": "FR4", "thickness_mm": 0.33},
            {
                "name": "In4.Cu",
                "role": "solid GND plane",
                "material": "Copper",
                "thickness_mm": 0.018,
            },
            {"name": "Prepreg", "role": "dielectric", "material": "FR4", "thickness_mm": 0.11},
            {"name": "B.Cu", "role": "signal", "material": "Copper", "thickness_mm": 0.035},
        ],
    }
    return templates[layer_count]


def register(mcp: FastMCP) -> None:
    """Register signal-integrity tools."""

    @mcp.tool()
    def si_calculate_trace_impedance(
        width_mm: float,
        height_mm: float,
        er: float = 4.2,
        trace_type: str = "microstrip",
        copper_oz: float = 1.0,
        spacing_mm: float = 0.2,
    ) -> str:
        """Estimate PCB trace impedance using quasi-static interconnect formulas."""
        payload = TraceImpedanceInput(
            width_mm=width_mm,
            height_mm=height_mm,
            er=er,
            trace_type=trace_type,
            copper_oz=copper_oz,
            spacing_mm=spacing_mm,
        )
        impedance_ohm, effective_er = trace_impedance(
            payload.width_mm,
            payload.height_mm,
            payload.er,
            trace_type=payload.trace_type,
            copper_oz=payload.copper_oz,
            spacing_mm=payload.spacing_mm,
        )
        differential_ohm, _ = differential_impedance(
            payload.width_mm,
            payload.height_mm,
            payload.spacing_mm,
            payload.er,
            trace_type=payload.trace_type,
            copper_oz=payload.copper_oz,
        )
        return _format_impedance_result(
            title="Trace impedance estimate:",
            trace_type=payload.trace_type,
            width_mm=payload.width_mm,
            height_mm=payload.height_mm,
            er=payload.er,
            copper_oz=payload.copper_oz,
            impedance_ohm=impedance_ohm,
            effective_er=effective_er,
            spacing_mm=payload.spacing_mm,
            differential_ohm=differential_ohm,
        )

    @mcp.tool()
    def si_calculate_trace_width_for_impedance(
        target_ohm: float,
        height_mm: float,
        er: float = 4.2,
        trace_type: str = "microstrip",
        copper_oz: float = 1.0,
        spacing_mm: float = 0.2,
    ) -> str:
        """Solve for a trace width that meets the requested impedance target."""
        payload = TraceWidthForImpedanceInput(
            target_ohm=target_ohm,
            height_mm=height_mm,
            er=er,
            trace_type=trace_type,
            copper_oz=copper_oz,
            spacing_mm=spacing_mm,
        )
        solved_width_mm = solve_width_for_impedance(
            payload.target_ohm,
            payload.height_mm,
            payload.er,
            trace_type=payload.trace_type,
            copper_oz=payload.copper_oz,
            spacing_mm=payload.spacing_mm,
        )
        impedance_ohm, effective_er = trace_impedance(
            solved_width_mm,
            payload.height_mm,
            payload.er,
            trace_type=payload.trace_type,
            copper_oz=payload.copper_oz,
            spacing_mm=payload.spacing_mm,
        )
        return _format_impedance_result(
            title=f"Width synthesis for {payload.target_ohm:.2f} ohm:",
            trace_type=payload.trace_type,
            width_mm=solved_width_mm,
            height_mm=payload.height_mm,
            er=payload.er,
            copper_oz=payload.copper_oz,
            impedance_ohm=impedance_ohm,
            effective_er=effective_er,
            spacing_mm=payload.spacing_mm,
        )

    @mcp.tool()
    def si_check_differential_pair_skew(
        net_p: str,
        net_n: str,
        er: float = 4.2,
        trace_type: str = "microstrip",
    ) -> str:
        """Estimate differential-pair length skew and delay mismatch from board tracks."""
        payload = DifferentialPairSkewInput(net_p=net_p, net_n=net_n, er=er, trace_type=trace_type)
        lengths = _track_lengths_by_net()
        if payload.net_p not in lengths or payload.net_n not in lengths:
            return (
                "Could not compute differential-pair skew because one or both nets "
                "have no routed track segments on the active board."
            )

        height_mm = _outer_dielectric_height_mm()
        width_mm = _track_width_mm(payload.net_p) or _track_width_mm(payload.net_n) or 0.2
        _, effective_er = trace_impedance(
            width_mm,
            height_mm,
            payload.er,
            trace_type=payload.trace_type,
            spacing_mm=0.2,
        )
        delay_ps_per_mm = propagation_delay_ps_per_mm(effective_er)
        length_p = lengths[payload.net_p]
        length_n = lengths[payload.net_n]
        skew_mm = abs(length_p - length_n)
        skew_ps = skew_mm * delay_ps_per_mm
        verdict = "PASS" if skew_ps <= 10.0 else "WARN"

        return "\n".join(
            [
                f"Differential-pair skew analysis ({verdict}):",
                f"- Net P: {payload.net_p} length={length_p:.3f} mm",
                f"- Net N: {payload.net_n} length={length_n:.3f} mm",
                f"- Skew: {skew_mm:.3f} mm",
                f"- Estimated delay mismatch: {skew_ps:.3f} ps",
                f"- Effective permittivity used: {effective_er:.3f}",
                f"- Assumed outer dielectric height: {height_mm:.3f} mm",
                "- Heuristic target: keep skew under ~10 ps for fast serial links.",
            ]
        )

    @mcp.tool()
    def si_validate_length_matching(net_groups: list[list[str]], tolerance_mm: float = 2.0) -> str:
        """Validate that each net group is matched within the supplied tolerance."""
        payload = LengthMatchingInput(net_groups=net_groups, tolerance_mm=tolerance_mm)
        lengths = _track_lengths_by_net()

        lines = [f"Length-matching validation (tolerance {payload.tolerance_mm:.3f} mm):"]
        for index, group in enumerate(payload.net_groups, start=1):
            unique_group = [net for net in group if net]
            if not unique_group:
                lines.append(f"- Group {index}: skipped empty group")
                continue
            missing = [net for net in unique_group if net not in lengths]
            if missing:
                lines.append(f"- Group {index}: missing routed tracks for {', '.join(missing)}")
                continue

            samples = [(net, lengths[net]) for net in unique_group]
            shortest_net, shortest_mm = min(samples, key=lambda item: item[1])
            longest_net, longest_mm = max(samples, key=lambda item: item[1])
            spread_mm = longest_mm - shortest_mm
            verdict = "PASS" if spread_mm <= payload.tolerance_mm else "WARN"
            lines.append(
                f"- Group {index} ({verdict}): shortest {shortest_net}={shortest_mm:.3f} mm, "
                f"longest {longest_net}={longest_mm:.3f} mm, spread={spread_mm:.3f} mm"
            )
        return "\n".join(lines)

    @mcp.tool()
    def si_generate_stackup(
        layer_count: int = 4,
        target_impedance_ohm: float = 50.0,
        manufacturer: str = "JLCPCB",
        er: float = 4.2,
        copper_oz: float = 1.0,
    ) -> str:
        """Generate a practical board stackup recommendation and target trace geometry."""
        payload = StackupInput(
            layer_count=layer_count,
            target_impedance_ohm=target_impedance_ohm,
            manufacturer=manufacturer,
            er=er,
            copper_oz=copper_oz,
        )
        template = _stackup_templates(payload.manufacturer, payload.layer_count)
        outer_dielectric_mm = next(
            float(layer["thickness_mm"])
            for layer in template
            if str(layer["role"]).startswith("dielectric")
        )
        width_mm = solve_width_for_impedance(
            payload.target_impedance_ohm,
            outer_dielectric_mm,
            payload.er,
            trace_type="microstrip",
            copper_oz=payload.copper_oz,
        )
        impedance_ohm, effective_er = trace_impedance(
            width_mm,
            outer_dielectric_mm,
            payload.er,
            trace_type="microstrip",
            copper_oz=payload.copper_oz,
        )
        diff_gap_mm = solve_spacing_for_differential_impedance(
            100.0,
            width_mm * 0.55,
            outer_dielectric_mm,
            payload.er,
            trace_type="microstrip",
            copper_oz=payload.copper_oz,
        )
        diff_ohm, _ = differential_impedance(
            width_mm * 0.55,
            outer_dielectric_mm,
            diff_gap_mm,
            payload.er,
            trace_type="microstrip",
            copper_oz=payload.copper_oz,
        )

        lines = [
            f"Recommended {payload.layer_count}-layer {payload.manufacturer} stackup:",
            f"- Target outer-layer impedance: {payload.target_impedance_ohm:.2f} ohm",
            f"- Solved outer microstrip width: {width_mm:.3f} mm",
            f"- Rechecked impedance: {impedance_ohm:.2f} ohm",
            f"- Effective permittivity: {effective_er:.3f}",
            (
                f"- Approximate 100 ohm differential pair starting point: "
                f"width {width_mm * 0.55:.3f} mm / gap {diff_gap_mm:.3f} mm "
                f"(estimate {diff_ohm:.2f} ohm)"
            ),
            "Layers:",
        ]
        for index, layer in enumerate(template, start=1):
            lines.append(
                f"- {index}. {layer['name']} | {layer['role']} | "
                f"{layer['material']} | {float(layer['thickness_mm']):.3f} mm"
            )
        lines.append(
            "- Review with your fabricator's published stackup table "
            "before freezing impedance rules."
        )
        return "\n".join(lines)

    @mcp.tool()
    def si_check_via_stub(
        frequency_ghz: float,
        via_positions: list[tuple[float, float]] | None = None,
        er: float = 4.0,
    ) -> str:
        """Estimate via-stub resonance and risk for selected vias on the active board."""
        payload = ViaStubInput(
            via_positions=via_positions or [],
            frequency_ghz=frequency_ghz,
            er=er,
        )
        vias = _selected_vias(payload.via_positions)
        if not vias:
            return "No vias matched the supplied positions on the active board."

        board_thickness_mm = _board_thickness_mm()
        lines = [
            f"Via stub analysis at {payload.frequency_ghz:.3f} GHz:",
            f"- Assumed board thickness: {board_thickness_mm:.3f} mm",
            f"- Effective dielectric constant: {payload.er:.3f}",
        ]
        for via in vias[: get_config().max_items_per_response]:
            x_mm, y_mm = _via_position_mm(via)
            stub_mm = _via_stub_length_mm(via)
            resonance_ghz = via_stub_resonance_ghz(stub_mm, er=payload.er)
            risk = via_stub_risk_level(stub_mm, payload.frequency_ghz, er=payload.er)
            net_name = str(getattr(getattr(via, "net", None), "name", "") or "(no net)")
            drill_mm = nm_to_mm(int(getattr(via, "drill_diameter", 0)))
            via_type_name = ViaType.Name(int(getattr(via, "type", ViaType.VT_THROUGH)))
            lines.append(
                f"- {net_name} @ ({x_mm:.3f}, {y_mm:.3f}) mm | type={via_type_name} | "
                f"drill={drill_mm:.3f} mm | stub={stub_mm:.3f} mm | "
                f"quarter-wave resonance={resonance_ghz:.2f} GHz | risk={risk}"
            )
        return "\n".join(lines)

    @mcp.tool()
    def si_calculate_decoupling_placement(
        ic_ref: str,
        power_pin: str,
        target_freq_mhz: float,
    ) -> str:
        """Estimate decoupling placement quality around an IC power pin."""
        payload = DecouplingPlacementInput(
            ic_ref=ic_ref,
            power_pin=power_pin,
            target_freq_mhz=target_freq_mhz,
        )
        source_x_mm, source_y_mm = _find_power_anchor(payload.ic_ref, payload.power_pin)
        recommended_mm = recommended_decoupling_distance_mm(payload.target_freq_mhz)
        caps = _nearest_capacitors(payload.ic_ref, source_x_mm, source_y_mm)

        lines = [
            "Decoupling placement heuristic:",
            f"- IC reference: {payload.ic_ref}",
            f"- Power pin: {payload.power_pin}",
            f"- Anchor position: ({source_x_mm:.3f}, {source_y_mm:.3f}) mm",
            f"- Target frequency: {payload.target_freq_mhz:.3f} MHz",
            f"- Recommended maximum capacitor distance: {recommended_mm:.3f} mm",
        ]
        if not caps:
            lines.append("- No capacitor footprints were found on the active board.")
            lines.append("- Add a local decoupler as close as possible to the selected power pin.")
            return "\n".join(lines)

        best_ref, best_distance_mm, best_value = caps[0]
        verdict = "PASS" if best_distance_mm <= recommended_mm else "WARN"
        lines.append(
            f"- Nearest decoupler: {best_ref} ({best_value or 'value unknown'}) "
            f"at {best_distance_mm:.3f} mm ({verdict})"
        )
        lines.append("Nearest capacitors:")
        for reference, distance_mm, value in caps[: min(len(caps), 5)]:
            lines.append(f"- {reference}: {distance_mm:.3f} mm ({value or 'value unknown'})")
        lines.append(
            "- This is a placement heuristic; verify the actual current loop "
            "and return path in layout review."
        )
        return "\n".join(lines)
