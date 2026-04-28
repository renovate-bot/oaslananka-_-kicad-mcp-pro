from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from kicad_mcp.connection import KiCadConnectionError
from kicad_mcp.server import app


def test_cli_health_json_does_not_require_kicad(sample_project: Path) -> None:
    _ = sample_project
    result = CliRunner().invoke(app, ["health", "--json"])

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["ok"] is True
    assert payload["package"]["name"] == "kicad-mcp-pro"
    assert payload["kicad"]["ipc_reachable"] is False
    assert payload["checks"][-1]["name"] == "kicad_ipc"
    assert payload["checks"][-1]["status"] == "skipped"


def test_cli_doctor_json_reports_unavailable_kicad_without_stack_trace(
    sample_project: Path,
    monkeypatch,
) -> None:
    _ = sample_project
    monkeypatch.setattr("kicad_mcp.diagnostics.find_kicad_version", lambda _path: "KiCad 10.0.1")
    monkeypatch.setattr(
        "kicad_mcp.diagnostics.get_board",
        lambda: (_ for _ in ()).throw(KiCadConnectionError("IPC not reachable")),
    )

    result = CliRunner().invoke(app, ["doctor", "--json"])

    assert result.exit_code == 0, result.output
    assert "Traceback" not in result.output
    payload = json.loads(result.output)
    assert payload["status"] == "degraded"
    assert payload["kicad"]["version"] == "KiCad 10.0.1"
    assert any(check["name"] == "kicad_ipc" for check in payload["checks"])


def test_cli_version_and_serve_help(sample_project: Path) -> None:
    _ = sample_project
    runner = CliRunner()

    version = runner.invoke(app, ["version", "--json"])
    serve_help = runner.invoke(app, ["serve", "--help"])

    assert version.exit_code == 0, version.output
    assert json.loads(version.output)["package"]["version"]
    assert serve_help.exit_code == 0, serve_help.output
    assert "Start the MCP server explicitly" in serve_help.output
