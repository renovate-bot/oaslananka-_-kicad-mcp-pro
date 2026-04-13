from __future__ import annotations

import re

import pytest
from kipy.proto.common import types as common_types

from kicad_mcp.server import build_server
from tests.conftest import call_tool_text


@pytest.mark.anyio
async def test_pcb_summary_tool(mock_board) -> None:
    server = build_server("pcb")
    text = await call_tool_text(server, "pcb_get_board_summary", {})
    assert "Board summary" in text


@pytest.mark.anyio
async def test_pcb_add_track_creates_item(mock_board) -> None:
    server = build_server("pcb")
    await server.call_tool(
        "pcb_add_track",
        {
            "x1_mm": 0.0,
            "y1_mm": 0.0,
            "x2_mm": 10.0,
            "y2_mm": 0.0,
            "layer": "F_Cu",
            "width_mm": 0.25,
            "net_name": "NET1",
        },
    )
    assert mock_board.create_items.called


@pytest.mark.anyio
async def test_pcb_add_text_uses_kicad_compatible_alignment(mock_board) -> None:
    server = build_server("pcb")

    await server.call_tool(
        "pcb_add_text",
        {
            "text": "HELLO",
            "x_mm": 1.0,
            "y_mm": 1.0,
            "layer": "F_SilkS",
            "size_mm": 1.0,
        },
    )

    [[text_item]] = mock_board.create_items.call_args.args
    assert text_item.attributes.horizontal_alignment == common_types.HA_LEFT
    assert text_item.attributes.vertical_alignment == common_types.VA_BOTTOM


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_adds_missing_footprints(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: False)
    monkeypatch.setattr(
        "kicad_mcp.tools.pcb._export_schematic_net_map",
        lambda: (
            {
                ("R1", "1"): "VIN",
                ("R1", "2"): "MID",
                ("R2", "1"): "MID",
                ("R2", "2"): "GND",
            },
            "",
        ),
    )
    server = build_server("full")

    await call_tool_text(
        server,
        "sch_build_circuit",
        {
            "symbols": [
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R1",
                    "value": "10k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                },
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R2",
                    "value": "22k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 76.2,
                    "y_mm": 50.8,
                },
            ]
        },
    )

    result = await call_tool_text(server, "pcb_sync_from_schematic", {})
    pcb_text = (sample_project / "demo.kicad_pcb").read_text(encoding="utf-8")

    assert "New footprints added: 2" in result
    assert "(version 20250216)" in pcb_text
    assert pcb_text.count('(footprint "R_0805"') == 2
    assert '(property "Reference" "R1"' in pcb_text
    assert '(property "Reference" "R2"' in pcb_text
    assert '(net "VIN")' in pcb_text
    assert '(net "MID")' in pcb_text
    assert '(net "GND")' in pcb_text


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_refuses_when_board_is_open(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: True)
    server = build_server("pcb")

    result = await call_tool_text(server, "pcb_sync_from_schematic", {})

    assert "Refusing file-based PCB sync while a board is open" in result


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_deduplicates_multi_unit_references(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: False)
    monkeypatch.setattr("kicad_mcp.tools.pcb._export_schematic_net_map", lambda: ({}, ""))
    server = build_server("full")

    await call_tool_text(
        server,
        "sch_build_circuit",
        {
            "symbols": [
                {
                    "library": "MultiUnit",
                    "symbol_name": "DualChild",
                    "reference": "U1",
                    "value": "DualOpamp",
                    "footprint": "Resistor_SMD:R_1206",
                    "unit": 1,
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                },
                {
                    "library": "MultiUnit",
                    "symbol_name": "DualChild",
                    "reference": "U1",
                    "value": "DualOpamp",
                    "footprint": "Resistor_SMD:R_1206",
                    "unit": 2,
                    "x_mm": 76.2,
                    "y_mm": 50.8,
                },
            ]
        },
    )

    result = await call_tool_text(server, "pcb_sync_from_schematic", {})
    pcb_text = (sample_project / "demo.kicad_pcb").read_text(encoding="utf-8")

    assert "New footprints added: 1" in result
    assert pcb_text.count('(footprint "R_1206"') == 1
    assert pcb_text.count('(property "Reference" "U1"') == 1


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_reports_mismatches_without_replacing(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: False)
    monkeypatch.setattr("kicad_mcp.tools.pcb._export_schematic_net_map", lambda: ({}, ""))
    (sample_project / "demo.kicad_pcb").write_text(
        (
            "(kicad_pcb\n"
            '\t(version 20250216)\n'
            '\t(generator "pytest")\n'
            '\t(footprint "R_1206"\n'
            '\t\t(layer "F.Cu")\n'
            '\t\t(uuid "00000000-0000-0000-0000-000000000001")\n'
            "\t\t(at 40 50 90)\n"
            '\t\t(property "Reference" "R1"\n'
            '\t\t\t(at 0 -1.8 0)\n'
            '\t\t\t(layer "F.SilkS")\n'
            "\t\t)\n"
            '\t\t(property "Value" "10k"\n'
            '\t\t\t(at 0 1.8 0)\n'
            '\t\t\t(layer "F.Fab")\n'
            "\t\t)\n"
            '\t\t(pad "1" smd rect (at -1.4 0) (size 1.2 1.6) (layers "F.Cu"))\n'
            '\t\t(pad "2" smd rect (at 1.4 0) (size 1.2 1.6) (layers "F.Cu"))\n'
            "\t)\n"
            ")\n"
        ),
        encoding="utf-8",
    )
    server = build_server("full")

    await call_tool_text(
        server,
        "sch_build_circuit",
        {
            "symbols": [
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R1",
                    "value": "10k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                }
            ]
        },
    )

    result = await call_tool_text(server, "pcb_sync_from_schematic", {})
    pcb_text = (sample_project / "demo.kicad_pcb").read_text(encoding="utf-8")

    assert "Existing footprint mismatches:" in result
    assert "Rerun with replace_mismatched=True" in result
    assert "Mismatched footprints replaced: 0" in result
    assert '(footprint "R_1206"' in pcb_text
    assert '(footprint "R_0805"' not in pcb_text


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_replaces_mismatched_footprints_in_place(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: False)
    monkeypatch.setattr("kicad_mcp.tools.pcb._export_schematic_net_map", lambda: ({}, ""))
    (sample_project / "demo.kicad_pcb").write_text(
        (
            "(kicad_pcb\n"
            '\t(version 20250216)\n'
            '\t(generator "pytest")\n'
            '\t(footprint "R_1206"\n'
            '\t\t(layer "F.Cu")\n'
            '\t\t(uuid "00000000-0000-0000-0000-000000000001")\n'
            "\t\t(at 40 50 90)\n"
            '\t\t(property "Reference" "R1"\n'
            '\t\t\t(at 0 -1.8 0)\n'
            '\t\t\t(layer "F.SilkS")\n'
            "\t\t)\n"
            '\t\t(property "Value" "10k"\n'
            '\t\t\t(at 0 1.8 0)\n'
            '\t\t\t(layer "F.Fab")\n'
            "\t\t)\n"
            '\t\t(pad "1" smd rect (at -1.4 0) (size 1.2 1.6) (layers "F.Cu"))\n'
            '\t\t(pad "2" smd rect (at 1.4 0) (size 1.2 1.6) (layers "F.Cu"))\n'
            "\t)\n"
            ")\n"
        ),
        encoding="utf-8",
    )
    server = build_server("full")

    await call_tool_text(
        server,
        "sch_build_circuit",
        {
            "symbols": [
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R1",
                    "value": "10k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                }
            ]
        },
    )

    result = await call_tool_text(
        server,
        "pcb_sync_from_schematic",
        {"replace_mismatched": True},
    )
    pcb_text = (sample_project / "demo.kicad_pcb").read_text(encoding="utf-8")

    assert "Mismatched footprints replaced: 1" in result
    assert '(footprint "R_0805"' in pcb_text
    assert '(footprint "R_1206"' not in pcb_text
    assert re.search(r"\s+\(at 40\.0000 50\.0000 90\)", pcb_text) is not None


@pytest.mark.anyio
async def test_pcb_sync_from_schematic_avoids_simple_footprint_overlap(
    sample_project,
    mock_kicad,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("kicad_mcp.tools.pcb._board_is_open", lambda: False)
    monkeypatch.setattr("kicad_mcp.tools.pcb._export_schematic_net_map", lambda: ({}, ""))
    server = build_server("full")

    await call_tool_text(
        server,
        "sch_build_circuit",
        {
            "symbols": [
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R1",
                    "value": "10k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                },
                {
                    "library": "Device",
                    "symbol_name": "R",
                    "reference": "R2",
                    "value": "22k",
                    "footprint": "Resistor_SMD:R_0805",
                    "x_mm": 50.8,
                    "y_mm": 50.8,
                },
            ]
        },
    )

    await call_tool_text(server, "pcb_sync_from_schematic", {})
    pcb_text = (sample_project / "demo.kicad_pcb").read_text(encoding="utf-8")

    positions = {
        match.group(1)
        for match in re.finditer(r"\n\t\t\(at\s+([0-9.\-]+\s+[0-9.\-]+\s+\d+)\)", pcb_text)
    }

    assert pcb_text.count('(footprint "R_0805"') == 2
    assert len(positions) >= 2
