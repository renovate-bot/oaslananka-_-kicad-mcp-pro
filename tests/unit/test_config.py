from __future__ import annotations

from pathlib import Path

import pytest

from kicad_mcp.config import KiCadMCPConfig


def test_config_reads_env_vars(sample_project: Path, monkeypatch) -> None:
    monkeypatch.setenv("KICAD_MCP_LOG_LEVEL", "DEBUG")
    cfg = KiCadMCPConfig()
    assert cfg.project_dir == sample_project
    assert cfg.log_level == "DEBUG"


def test_config_auto_detects_files(sample_project: Path) -> None:
    cfg = KiCadMCPConfig()
    assert cfg.project_file == sample_project / "demo.kicad_pro"
    assert cfg.pcb_file == sample_project / "demo.kicad_pcb"
    assert cfg.sch_file == sample_project / "demo.kicad_sch"


def test_config_resolve_within_project(sample_project: Path) -> None:
    cfg = KiCadMCPConfig()
    resolved = cfg.resolve_within_project("exports/demo.txt")
    assert resolved == sample_project / "exports" / "demo.txt"


def test_mount_path_is_normalized_without_trailing_slash(sample_project: Path) -> None:
    _ = sample_project
    cfg = KiCadMCPConfig(mount_path="api/")
    assert cfg.mount_path == "/api"


def test_cors_origins_require_explicit_http_urls(sample_project: Path) -> None:
    _ = sample_project
    cfg = KiCadMCPConfig(cors_origins="https://example.com,http://localhost:3334")
    assert cfg.cors_origin_list == ["https://example.com", "http://localhost:3334"]

    with pytest.raises(ValueError, match="cannot contain '\\*'"):
        KiCadMCPConfig(cors_origins="*")

    with pytest.raises(ValueError, match="must be fully qualified"):
        KiCadMCPConfig(cors_origins="vscode-webview://panel")
