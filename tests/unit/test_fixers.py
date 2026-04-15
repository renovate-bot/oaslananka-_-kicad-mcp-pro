from __future__ import annotations

from kicad_mcp.tools.fixers import (
    BLOCKING_GATES,
    auto_fix_description,
    first_agent_action,
    fixers_for_gate,
)


def test_fixers_registry_helpers() -> None:
    schematic_fixers = fixers_for_gate("Schematic")
    assert len(schematic_fixers) == 3
    assert auto_fix_description("Schematic") == "Annotate un-annotated schematic symbols."
    assert first_agent_action("Schematic").tool == "sch_get_bounding_boxes"

    assert fixers_for_gate("Unknown") == []
    assert auto_fix_description("Unknown") is None
    assert first_agent_action("Unknown") is None

    assert "Schematic" in BLOCKING_GATES
    assert "Schematic connectivity" in BLOCKING_GATES
