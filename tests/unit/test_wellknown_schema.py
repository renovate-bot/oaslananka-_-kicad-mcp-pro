from __future__ import annotations

from kicad_mcp.wellknown import get_wellknown_metadata


def test_wellknown_payload_contains_required_server_card_fields() -> None:
    payload = get_wellknown_metadata()

    assert (
        payload["$schema"]
        == "https://static.modelcontextprotocol.io/schemas/mcp-server-card/v1.json"
    )
    assert payload["version"]
    assert payload["protocolVersion"]
    assert payload["serverInfo"]["title"] == "KiCad MCP Pro"
    assert payload["transport"]["type"] in {"stdio", "streamable-http"}
    assert payload["capabilities"] == {
        "tools": True,
        "resources": True,
        "prompts": True,
        "sampling": True,
    }
    assert payload["categories"] == ["eda", "pcb", "kicad"]
