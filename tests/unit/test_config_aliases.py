from __future__ import annotations

from pathlib import Path

import pytest

from kicad_mcp.config import KiCadMCPConfig


def test_config_aliases_and_secret_masking(fake_cli: Path, monkeypatch) -> None:
    workspace = fake_cli.parent
    monkeypatch.setenv("KICAD_API_TOKEN", "secret-token")
    monkeypatch.setenv("KICAD_CLI_PATH", str(fake_cli))
    monkeypatch.setenv("KICAD_MCP_TIMEOUT_MS", "15000")
    monkeypatch.setenv("KICAD_MCP_RETRIES", "4")
    monkeypatch.setenv("KICAD_MCP_HEADLESS", "true")
    monkeypatch.setenv("KICAD_MCP_WORKSPACE_ROOT", str(workspace))
    monkeypatch.setenv("KICAD_MCP_LOG_LEVEL", "debug")

    cfg = KiCadMCPConfig()
    safe = cfg.safe_diagnostics()

    assert cfg.kicad_cli == fake_cli
    assert cfg.kicad_token == "secret-token"  # noqa: S105 - test fixture
    assert cfg.timeout_ms == 15000
    assert cfg.ipc_retries == 4
    assert cfg.headless is True
    assert cfg.log_level == "DEBUG"
    assert safe["kicad_token"] == {"configured": True}
    assert "secret-token" not in str(safe)


def test_invalid_timeout_alias_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("KICAD_MCP_TIMEOUT_MS", "not-a-number")

    with pytest.raises(ValueError):
        KiCadMCPConfig()


def test_vscode_webview_origin_is_allowed(sample_project: Path) -> None:
    _ = sample_project
    cfg = KiCadMCPConfig(cors_origins="vscode-webview://kicad-studio")

    assert cfg.cors_origin_list == ["vscode-webview://kicad-studio"]
