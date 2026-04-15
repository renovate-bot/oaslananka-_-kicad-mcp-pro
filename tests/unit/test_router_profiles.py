from __future__ import annotations

import pytest

from kicad_mcp.server import build_server, create_server
from kicad_mcp.tools.router import (
    PROFILE_CATEGORIES,
    TOOL_CATEGORIES,
    available_profiles,
    categories_for_profile,
)
from tests.conftest import call_tool_text


def test_available_profiles_include_v2_surface() -> None:
    expected = {
        "full",
        "minimal",
        "schematic_only",
        "pcb_only",
        "manufacturing",
        "high_speed",
        "power",
        "simulation",
        "analysis",
        "pcb",
        "schematic",
    }

    assert expected.issubset(set(available_profiles()))
    assert categories_for_profile("analysis") == PROFILE_CATEGORIES["analysis"]
    assert categories_for_profile("unknown-profile") == PROFILE_CATEGORIES["full"]


def test_create_server_sync_wrapper_materializes_tool_list() -> None:
    server = create_server("full")
    tools = server.list_tools()

    assert isinstance(tools, list)
    assert any(tool.name == "kicad_get_version" for tool in tools)


@pytest.mark.anyio
async def test_tool_category_output_shows_runtime_metadata() -> None:
    server = build_server("full")

    routing = await call_tool_text(server, "kicad_get_tools_in_category", {"category": "routing"})
    pcb_read = await call_tool_text(server, "kicad_get_tools_in_category", {"category": "pcb_read"})
    release_export = await call_tool_text(
        server,
        "kicad_get_tools_in_category",
        {"category": "release_export"},
    )

    assert "route_autoroute_freerouting [HEADLESS / REQUIRES:freerouting]" in routing
    assert "pcb_get_tracks [REQUIRES_KICAD]" in pcb_read
    assert "export_manufacturing_package [HEADLESS]" in release_export
    assert "get_board_stats [HEADLESS]" in release_export


@pytest.mark.anyio
async def test_manufacturing_profile_exposes_release_exports_only() -> None:
    server = build_server("manufacturing")
    tool_names = {tool.name for tool in await server.list_tools()}

    assert "export_manufacturing_package" in tool_names
    assert "get_board_stats" in tool_names
    assert "export_gerber" not in tool_names
    assert "export_drill" not in tool_names
    assert "export_bom" not in tool_names


@pytest.mark.anyio
async def test_full_profile_keeps_low_level_exports_available() -> None:
    server = build_server("full")
    tool_names = {tool.name for tool in await server.list_tools()}

    assert "export_gerber" in tool_names
    assert "export_drill" in tool_names
    assert "export_bom" in tool_names


@pytest.mark.anyio
async def test_tool_categories_have_no_phantom_or_undeclared_tools() -> None:
    server = build_server("full")
    registered = {tool.name for tool in await server.list_tools()}
    declared: set[str] = set()
    for category in TOOL_CATEGORIES.values():
        declared.update(category["tools"])

    assert declared == registered
