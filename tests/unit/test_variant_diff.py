from __future__ import annotations

import json

import pytest

from kicad_mcp.server import create_server
from kicad_mcp.tools.schematic import place_symbol_block
from tests.conftest import call_tool_text


def _write_variant_schematic(sample_project) -> None:
    schematic = sample_project / "demo.kicad_sch"
    schematic.write_text(
        (
            "(kicad_sch\n"
            "\t(version 20250316)\n"
            '\t(generator "pytest")\n'
            '\t(uuid "00000000-0000-0000-0000-000000000000")\n'
            '\t(paper "A4")\n'
            "\t(lib_symbols)\n"
            f"{place_symbol_block('Device:R', 20.0, 20.0, 'R1', '10k', 'Resistor_SMD:R_0805')}\n"
            f"{place_symbol_block('Device:R', 35.0, 20.0, 'R2', '1k', 'Resistor_SMD:R_1206')}\n"
            "\t(sheet_instances\n"
            '\t\t(path "/" (page "1"))\n'
            "\t)\n"
            "\t(embedded_fonts no)\n"
            ")\n"
        ),
        encoding="utf-8",
    )


@pytest.mark.anyio
async def test_variant_tools_create_diff_and_export(sample_project) -> None:
    _write_variant_schematic(sample_project)
    server = create_server()

    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    await call_tool_text(server, "variant_create", {"name": "lite"})
    await call_tool_text(
        server,
        "variant_set_component_override",
        {"variant": "lite", "reference": "R2", "enabled": False},
    )
    await call_tool_text(server, "variant_set_active", {"name": "lite"})

    listing = json.loads(await call_tool_text(server, "variant_list", {}))
    assert listing["active_variant"] == "lite"
    assert {item["name"] for item in listing["variants"]} == {"default", "lite"}

    diff = json.loads(
        await call_tool_text(
            server,
            "variant_diff_bom",
            {"variant_a": "default", "variant_b": "lite"},
        )
    )
    assert diff["removed"][0]["reference"] == "R2"

    exported = await call_tool_text(server, "variant_export_bom", {"variant": "lite"})
    assert "lite_bom.csv" in exported

