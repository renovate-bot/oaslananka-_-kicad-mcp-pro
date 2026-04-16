from __future__ import annotations

import json

import pytest

from kicad_mcp.config import get_config
from kicad_mcp.server import create_server
from kicad_mcp.wellknown import get_wellknown_metadata
from tests.conftest import call_tool_text


def test_wellknown_metadata_contains_http_and_profiles() -> None:
    metadata = get_wellknown_metadata()
    assert metadata["name"] == "kicad-mcp-pro"
    assert "streamable-http" in metadata["transport"]
    assert "full" in metadata["profiles"]


@pytest.mark.anyio
async def test_studio_push_context_updates_resource_and_auto_sets_project(sample_project) -> None:
    server = create_server()
    active_file = sample_project / "demo.kicad_pro"

    result = await call_tool_text(
        server,
        "studio_push_context",
        {
            "active_file": str(active_file),
            "file_type": "other",
            "drc_errors": ["clearance"],
            "selected_reference": "U1",
        },
    )

    resource_items = list(await server.read_resource("kicad://studio/context"))
    payload = json.loads(resource_items[0].content)
    assert payload["active_file"] == str(active_file)
    assert payload["selected_reference"] == "U1"
    assert get_config().project_dir == sample_project.resolve()
    assert "Studio context updated" in result
