from __future__ import annotations

import json

import pytest

from kicad_mcp.tools.variants import (
    _load_project_payload,
    _load_state,
    _project_state_from_payload,
    _render_variant_components,
    _variants_path,
    variant_apply_to_kicad_cli_args,
)


def test_load_project_payload_rejects_invalid_json(sample_project) -> None:
    project_file = sample_project / "demo.kicad_pro"
    project_file.write_text("{broken", encoding="utf-8")

    with pytest.raises(ValueError, match="valid JSON"):
        _load_project_payload(project_file)


def test_load_project_payload_rejects_non_object_root(sample_project) -> None:
    project_file = sample_project / "demo.kicad_pro"
    project_file.write_text('["not-an-object"]', encoding="utf-8")

    with pytest.raises(ValueError, match="JSON object"):
        _load_project_payload(project_file)


def test_load_state_falls_back_to_sidecar_when_no_project_file(
    sample_project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_file = sample_project / "demo.kicad_pro"
    project_file.unlink()
    monkeypatch.setenv("KICAD_MCP_PROJECT_DIR", str(sample_project))
    monkeypatch.setenv("KICAD_MCP_SCH_FILE", str(sample_project / "demo.kicad_sch"))

    state = _load_state()

    assert state["active_variant"] == "default"
    assert _variants_path().exists()


def test_project_state_from_payload_returns_none_for_incomplete_section() -> None:
    assert _project_state_from_payload({}) is None
    assert _project_state_from_payload({"variants": {}}) is None


def test_variant_apply_to_kicad_cli_args_reads_active_variant_from_project(
    sample_project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_file = sample_project / "demo.kicad_pro"
    monkeypatch.setenv("KICAD_MCP_PROJECT_DIR", str(sample_project))
    monkeypatch.setenv("KICAD_MCP_PROJECT_FILE", str(project_file))
    monkeypatch.setenv("KICAD_MCP_SCH_FILE", str(sample_project / "demo.kicad_sch"))
    project_file.write_text(
        json.dumps(
            {
                "meta": {"version": 1},
                "variants": {
                    "default_variant": "default",
                    "active_variant": "lite",
                    "variants": {"default": {"overrides": {}}, "lite": {"overrides": {}}},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert variant_apply_to_kicad_cli_args() == ["--variant", "lite"]
    with pytest.raises(ValueError, match="was not found"):
        variant_apply_to_kicad_cli_args("missing")


def test_variant_apply_to_kicad_cli_args_returns_empty_when_project_has_no_active_variant(
    sample_project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_file = sample_project / "demo.kicad_pro"
    monkeypatch.setenv("KICAD_MCP_PROJECT_DIR", str(sample_project))
    monkeypatch.setenv("KICAD_MCP_PROJECT_FILE", str(project_file))
    monkeypatch.setenv("KICAD_MCP_SCH_FILE", str(sample_project / "demo.kicad_sch"))
    project_file.write_text(
        json.dumps(
            {
                "meta": {"version": 1},
                "variants": {
                    "default_variant": "",
                    "active_variant": " ",
                    "variants": {"default": {"overrides": {}}},
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    assert variant_apply_to_kicad_cli_args() == []


def test_render_variant_components_merges_unknown_override_reference(
    sample_project,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KICAD_MCP_PROJECT_DIR", str(sample_project))
    monkeypatch.setenv("KICAD_MCP_SCH_FILE", str(sample_project / "demo.kicad_sch"))
    state = {
        "default_variant": "default",
        "active_variant": "default",
        "variants": {
            "default": {
                "overrides": {
                    "U99": {"enabled": False, "value": "ALT", "footprint": "Package:Test"}
                }
            }
        },
    }

    rendered = _render_variant_components(state, "default")

    assert "U99" in rendered
    assert rendered["U99"]["enabled"] is False
