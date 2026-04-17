from __future__ import annotations

from kicad_mcp.tools.metadata import infer_tool_annotations
from kicad_mcp.tools.router import TOOL_CATEGORIES


def test_every_declared_tool_can_be_normalized_into_annotations() -> None:
    declared_tools = {
        tool_name
        for category in TOOL_CATEGORIES.values()
        for tool_name in category["tools"]
    }
    for tool_name in declared_tools:
        annotations = infer_tool_annotations(tool_name).model_dump(exclude_none=True)
        assert isinstance(annotations, dict), f"{tool_name} could not be normalized for discovery"
