from __future__ import annotations

import asyncio
import json
import re
import subprocess
import tomllib
from pathlib import Path
from typing import Any

import anyio
import pytest
from mcp.types import CallToolResult
from starlette.testclient import TestClient

from kicad_mcp.config import get_config, reset_config
from kicad_mcp.discovery import CliCapabilities
from kicad_mcp.server import CLI_FAILURE_TOOL_NAMES, HEAVY_TOOL_NAMES, build_server
from tests.conftest import call_tool_text

EXPOSED_HOST = "0." + "0.0.0"
STRONG_TOKEN = "".join(("0123456789abcdef", "0123456789ABCDEF"))
ROTATED_STRONG_TOKEN = "".join(("fedcba9876543210", "FEDCBA9876543210"))


def test_stateful_http_config_controls_fastmcp_setting(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.stateful_http = True
    assert build_server("minimal").settings.stateless_http is False

    reset_config()
    cfg = get_config()
    cfg.stateful_http = False
    assert build_server("minimal").settings.stateless_http is True


@pytest.mark.anyio
async def test_metrics_increment_after_tool_call(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    cfg.enable_metrics = True
    server = build_server("minimal")

    await call_tool_text(server, "kicad_get_version", {})

    response = TestClient(server.streamable_http_app()).get("/metrics")

    assert response.status_code == 200
    assert 'kicad_mcp_tool_calls_total{tool="kicad_get_version",status="ok"}' in response.text
    assert "kicad_mcp_tool_latency_p95_ms" in response.text


@pytest.mark.anyio
async def test_heavy_tool_calls_are_rate_limited(sample_project: Path, monkeypatch) -> None:
    _ = sample_project
    server = build_server("full")
    active = 0
    max_active = 0

    async def fake_call_tool(
        name: str,
        arguments: dict[str, Any],
        context: object | None = None,
        convert_result: bool = False,
    ) -> list[object]:
        nonlocal active, max_active
        _ = name, arguments, context, convert_result
        active += 1
        max_active = max(max_active, active)
        await anyio.sleep(0.05)
        active -= 1
        return []

    monkeypatch.setattr(server._tool_manager, "call_tool", fake_call_tool)

    await asyncio.gather(
        server.call_tool("export_gerber", {}),
        server.call_tool("export_gerber", {}),
        server.call_tool("export_gerber", {}),
    )

    assert max_active == 2


def test_release_heavy_tools_are_rate_limited() -> None:
    expected = {
        "run_drc",
        "run_erc",
        "project_quality_gate",
        "check_design_for_manufacture",
        "export_gerber",
        "pcb_export_3d_pdf",
        "export_manufacturing_package",
        "route_export_dsn",
        "route_autoroute_freerouting",
        "route_import_ses",
    }

    assert expected.issubset(HEAVY_TOOL_NAMES)


def test_cli_failure_tools_are_structured_error_candidates() -> None:
    expected = {
        "run_drc",
        "run_erc",
        "export_gerber",
        "get_board_stats",
        "pcb_export_3d_pdf",
    }

    assert expected.issubset(CLI_FAILURE_TOOL_NAMES)
    # route_* tools return ToolResult directly; failures are encoded in ok=False,
    # not intercepted by the string-match layer.
    assert "route_export_dsn" not in CLI_FAILURE_TOOL_NAMES
    assert "route_autoroute_freerouting" not in CLI_FAILURE_TOOL_NAMES
    assert "route_import_ses" not in CLI_FAILURE_TOOL_NAMES


def test_audit_log_records_keys_without_sensitive_values(monkeypatch) -> None:
    from kicad_mcp import server as server_module

    cfg = get_config()
    cfg.transport = "streamable-http"
    events: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        server_module.logger,
        "info",
        lambda event, **kwargs: events.append((event, kwargs)),
    )

    server_module._audit_tool_call(
        tool_name="example_tool",
        arguments={"auth_token": "super-secret", "normal": "value"},
        status="ok",
        elapsed_ms=1.0,
        error_code=None,
    )

    assert events[0][1]["argument_keys"] == ["auth_token", "normal"]
    assert "super-secret" not in str(events[0])


@pytest.mark.anyio
async def test_http_tool_call_audit_log_is_emitted(sample_project: Path, monkeypatch) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    server = build_server("minimal")
    events: list[tuple[str, dict[str, object]]] = []
    monkeypatch.setattr(
        "kicad_mcp.server.logger.info",
        lambda event, **kwargs: events.append((event, kwargs)),
    )

    await call_tool_text(server, "kicad_get_version", {})

    audit = [item for item in events if item[0] == "tool_call_audit"]
    assert audit
    assert audit[0][1]["tool"] == "kicad_get_version"
    assert audit[0][1]["status"] == "ok"


def test_token_rotation_requires_current_bearer_and_updates_verifier(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    cfg.auth_token = STRONG_TOKEN
    server = build_server("minimal")
    client = TestClient(server.streamable_http_app())

    unauthorized = client.post(
        "/.well-known/mcp-server/token-rotate",
        json={"new_token": "new-token"},
    )
    assert unauthorized.status_code == 401

    rotated = client.post(
        "/.well-known/mcp-server/token-rotate",
        headers={"Authorization": f"Bearer {STRONG_TOKEN}"},
        json={"new_token": ROTATED_STRONG_TOKEN},
    )

    assert rotated.status_code == 200
    assert cfg.auth_token == ROTATED_STRONG_TOKEN
    assert asyncio.run(server._token_verifier.verify_token(STRONG_TOKEN)) is None
    assert asyncio.run(server._token_verifier.verify_token(cfg.auth_token)) is not None


def test_token_rotation_rejects_weak_token(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    cfg.auth_token = STRONG_TOKEN
    server = build_server("minimal")
    client = TestClient(server.streamable_http_app())

    response = client.post(
        "/.well-known/mcp-server/token-rotate",
        headers={"Authorization": f"Bearer {STRONG_TOKEN}"},
        json={"new_token": "short-token"},
    )

    assert response.status_code == 400
    assert cfg.auth_token == STRONG_TOKEN


def test_non_loopback_http_requires_auth_token(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    try:
        cfg.transport = "streamable-http"
        cfg.host = EXPOSED_HOST
        cfg.auth_token = None

        with pytest.raises(ValueError, match="requires auth_token"):
            build_server("minimal")
    finally:
        reset_config()


def test_non_loopback_http_accepts_strong_token(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    try:
        cfg.transport = "streamable-http"
        cfg.host = EXPOSED_HOST
        cfg.auth_token = STRONG_TOKEN

        assert build_server("minimal").settings.host == EXPOSED_HOST
    finally:
        reset_config()


def test_exposed_metrics_require_authentication(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    try:
        cfg.transport = "streamable-http"
        cfg.host = EXPOSED_HOST
        cfg.auth_token = STRONG_TOKEN
        cfg.enable_metrics = True
        server = build_server("minimal")
        client = TestClient(server.streamable_http_app())

        unauthorized = client.get("/metrics")
        authorized = client.get("/metrics", headers={"Authorization": f"Bearer {STRONG_TOKEN}"})

        assert unauthorized.status_code == 401
        assert authorized.status_code == 200
    finally:
        reset_config()


def test_http_mcp_endpoint_requires_bearer_token(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    cfg.auth_token = "required-token"  # noqa: S105 - test fixture
    server = build_server("minimal")
    client = TestClient(server.streamable_http_app())

    response = client.post(
        "/mcp",
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
    )

    assert response.status_code == 401
    assert response.json()["error"] == "invalid_token"


def test_token_rotation_rejects_non_string_token(sample_project: Path) -> None:
    _ = sample_project
    cfg = get_config()
    cfg.transport = "streamable-http"
    cfg.auth_token = STRONG_TOKEN
    server = build_server("minimal")
    client = TestClient(server.streamable_http_app())

    response = client.post(
        "/.well-known/mcp-server/token-rotate",
        headers={"Authorization": f"Bearer {STRONG_TOKEN}"},
        json={"new_token": 123},
    )

    assert response.status_code == 400
    assert cfg.auth_token == STRONG_TOKEN


@pytest.mark.anyio
async def test_tool_exception_returns_structured_error() -> None:
    server = build_server("full")

    result = await server.call_tool("export_gerber", {})

    assert isinstance(result, CallToolResult)
    assert result.isError is True
    assert result.structuredContent is not None
    assert result.structuredContent["error_code"] == "CONFIGURATION_ERROR"
    assert "message" in result.structuredContent
    assert "hint" in result.structuredContent


@pytest.mark.anyio
async def test_cli_nonzero_result_returns_structured_error(
    sample_project: Path,
    monkeypatch,
) -> None:
    class Result:
        returncode = 2
        stdout = ""
        stderr = "fatal export failed"

    monkeypatch.setattr(
        "kicad_mcp.tools.export.get_cli_capabilities",
        lambda _cli: CliCapabilities(
            version="KiCad 10.0.1",
            gerber_command="gerber",
            drill_command="drill",
            position_command="pos",
            supports_ipc2581=True,
        ),
    )
    monkeypatch.setattr("kicad_mcp.tools.export.subprocess.run", lambda *_args, **_kwargs: Result())

    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    result = await server.call_tool("export_gerber", {})

    assert isinstance(result, CallToolResult)
    assert result.isError is True
    assert result.structuredContent is not None
    assert result.structuredContent["error_code"] == "CLI_COMMAND_FAILED"
    assert "Gerber export failed" in result.structuredContent["message"]


@pytest.mark.anyio
async def test_export_gerber_sends_progress_notifications(
    sample_project: Path,
    monkeypatch,
) -> None:
    progress_events: list[tuple[float, float, str]] = []

    async def fake_report_progress(
        _ctx: object,
        progress: float,
        total: float,
        message: str,
    ) -> None:
        progress_events.append((progress, total, message))

    def fake_run_cli_variants(variants: list[list[str]]) -> tuple[int, str, str]:
        command = variants[0]
        output_index = command.index("--output") + 1
        output_path = Path(command[output_index])
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "board-F_Cu.gbr").write_text("gerber\n", encoding="utf-8")
        return 0, "", ""

    monkeypatch.setattr("kicad_mcp.tools.export._report_progress", fake_report_progress)
    monkeypatch.setattr("kicad_mcp.tools.export._run_cli_variants", fake_run_cli_variants)
    monkeypatch.setattr(
        "kicad_mcp.tools.export.get_cli_capabilities",
        lambda _cli: CliCapabilities(
            version="KiCad 10.0.1",
            gerber_command="gerber",
            drill_command="drill",
            position_command="pos",
            supports_ipc2581=True,
        ),
    )

    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    result = await call_tool_text(server, "export_gerber", {})

    assert "Gerber export completed" in result
    assert progress_events[0][0:2] == (5, 100)
    assert progress_events[-1][0:2] == (100, 100)


@pytest.mark.anyio
async def test_manufacturing_gate_block_returns_structured_validation_error(
    sample_project: Path,
    monkeypatch,
) -> None:
    from kicad_mcp.tools.validation import GateOutcome

    monkeypatch.setattr(
        "kicad_mcp.tools.validation._evaluate_project_gate",
        lambda **_kwargs: [
            GateOutcome(name="DRC", status="FAIL", summary="DRC failed", details=["clearance"])
        ],
    )

    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    result = await server.call_tool("export_manufacturing_package", {})

    assert isinstance(result, CallToolResult)
    assert result.isError is True
    assert result.structuredContent is not None
    assert result.structuredContent["error_code"] == "VALIDATION_FAILED"


def test_run_cli_retries_transient_timeout(fake_cli: Path, monkeypatch) -> None:
    from kicad_mcp.tools import export

    attempts = 0

    def fake_run(*_args: object, **_kwargs: object):
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise subprocess.TimeoutExpired(cmd="kicad-cli", timeout=0.1)

        class Result:
            returncode = 0
            stdout = "ok"
            stderr = ""

        return Result()

    monkeypatch.setattr(export.subprocess, "run", fake_run)
    monkeypatch.setattr(export.time, "sleep", lambda _seconds: None)

    code, stdout, stderr = export._run_cli("pcb", "export", "gerber")

    assert (code, stdout, stderr) == (0, "ok", "")
    assert attempts == 3


def test_run_cli_does_not_retry_non_transient_exit(fake_cli: Path, monkeypatch) -> None:
    from kicad_mcp.tools import export

    attempts = 0

    def fake_run(*_args: object, **_kwargs: object):
        nonlocal attempts
        attempts += 1

        class Result:
            returncode = 2
            stdout = ""
            stderr = "syntax error"

        return Result()

    monkeypatch.setattr(export.subprocess, "run", fake_run)
    monkeypatch.setattr(export.time, "sleep", lambda _seconds: None)

    code, stdout, stderr = export._run_cli("pcb", "export", "gerber")

    assert (code, stdout, stderr) == (2, "", "syntax error")
    assert attempts == 1


def test_pdn_mesh_reports_ac_impedance_violations() -> None:
    from kicad_mcp.utils.pdn_mesh import PdnDecouplingCap, PdnLoad, PdnMesh

    result = PdnMesh().solve(
        net_name="+3V3",
        source_ref="U_REG",
        loads=[PdnLoad(ref="U1", current_a=0.2, distance_mm=50.0)],
        trace_width_mm=0.25,
        copper_weight_oz=1.0,
        nominal_voltage_v=3.3,
        frequency_points_hz=[1_000_000.0, 100_000_000.0],
        decoupling_caps=[
            PdnDecouplingCap(ref="C1", capacitance_f=100e-9, esr_ohm=0.02, esl_h=1e-9)
        ],
        target_impedance_ohm=0.05,
    )

    assert result.impedance_ohm
    assert result.max_impedance_ohm > 0.0
    assert result.impedance_violations


def test_release_workflow_uses_trusted_publishing() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")
    shell_suppression = "||" + " true"
    legacy_publish_script = "bash scripts/" + "publish.sh"

    assert "id-token: write" in workflow
    assert "pypa/gh-action-pypi-publish@" in workflow
    assert "needs.release-please.outputs.release_created == 'true'" in workflow
    assert "Verify required release secrets" not in workflow
    assert "secrets.PYPI" not in workflow
    assert "secrets.TEST_PYPI" not in workflow
    assert legacy_publish_script not in workflow
    assert shell_suppression not in workflow


def test_release_workflow_stages_only_python_distributions_for_publish() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")

    staging_start = workflow.index("Stage Python distributions for package index")
    staging_end = workflow.index("Generate CycloneDX SBOM")
    staging_block = workflow[staging_start:staging_end]

    assert 'source.glob("*.whl")' in staging_block
    assert 'source.glob("*.tar.gz")' in staging_block
    assert "dist-pypi" in staging_block
    assert "packages-dir: dist-pypi/" in workflow
    assert "bom.json" not in staging_block
    assert "SHA256SUMS.txt" not in staging_block


def test_review_thread_gate_paginates_graphql_threads() -> None:
    root = Path(__file__).resolve().parents[2]
    workflow = (root / ".github" / "workflows" / "review-thread-gate.yml").read_text(
        encoding="utf-8"
    )
    script = (root / "scripts" / "check-review-threads.mjs").read_text(encoding="utf-8")

    assert "actions/checkout@de0fac2e4500dabe0009e67214ff5f5447ce83dd" in workflow
    assert "actions/setup-node@48b55a011bda9f5d6aeb4c2d9c7362e8dae4041e" in workflow
    assert "node-version-file: .node-version" in workflow
    assert "node scripts/check-review-threads.mjs" in workflow
    assert "actions/checkout@v4" not in workflow

    assert "pageInfo" in script
    assert "hasNextPage" in script
    assert "endCursor" in script
    assert "do {" in script
    assert "} while (cursor);" in script
    assert "GitHub GraphQL request failed" in script


def test_docker_metadata_contains_mcp_oci_label_and_no_mutable_image_tags() -> None:
    root = Path(__file__).resolve().parents[2]
    dockerfile = (root / "Dockerfile").read_text(encoding="utf-8")
    kicad_dockerfile = (root / "Dockerfile.kicad10").read_text(encoding="utf-8")
    compose = (root / "docker-compose.yml").read_text(encoding="utf-8")
    docker_workflow = (root / ".github" / "workflows" / "docker-publish.yml").read_text(
        encoding="utf-8"
    )
    uv_toml = (root / "uv.toml").read_text(encoding="utf-8")
    docker_install = (root / "docs" / "install" / "docker.md").read_text(encoding="utf-8")
    publishing = (root / "docs" / "publishing.md").read_text(encoding="utf-8")
    uv_version = tomllib.loads(uv_toml).get("required-version")
    assert uv_version

    for content in (dockerfile, kicad_dockerfile):
        assert 'io.modelcontextprotocol.server.name="io.github.oaslananka/kicad-mcp-pro"' in content
        assert (
            'org.opencontainers.image.source="https://github.com/oaslananka/kicad-mcp-pro"'
            in content
        )
        assert "ARG KICAD_MCP_VERSION" in content
        assert "ARG VCS_REF" in content
        assert "@sha256:" in content

    assert "pip install --no-cache-dir uv" not in dockerfile
    assert "pip install --no-cache-dir uv" not in kicad_dockerfile
    assert "apt-get upgrade -y --no-install-recommends" in dockerfile
    assert "apt-get upgrade -y --no-install-recommends" in kicad_dockerfile
    assert f"UV_VERSION={uv_version}" in dockerfile
    assert f"UV_VERSION={uv_version}" in kicad_dockerfile
    assert "ENV KICAD_MCP_HOST=127.0.0.1" in kicad_dockerfile
    assert "debian:bookworm-slim@sha256:" in kicad_dockerfile
    assert "ghcr.io/freerouting/freerouting:2.1.0@sha256:" in compose
    assert ":latest" not in compose
    assert "type=raw,value=latest" not in docker_workflow
    assert "ghcr.io/oaslananka/kicad-mcp-pro:latest" not in docker_install
    assert "ghcr.io/oaslananka/kicad-mcp-pro:latest" not in publishing


def test_scorecard_workflow_avoids_artifact_storage_for_sarif() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "scorecard.yml"
    ).read_text(encoding="utf-8")

    assert "security-events: write" in workflow
    assert "results_file: scorecard.sarif" in workflow
    assert "github/codeql-action/upload-sarif@68bde559dea0fdcac2102bfdf6230c5f70eb485e" in workflow
    assert "sarif_file: scorecard.sarif" in workflow
    assert "Detect Scorecard SARIF" in workflow
    assert "steps.scorecard-sarif.outputs.present == 'true'" in workflow
    assert "Scorecard did not emit scorecard.sarif; skipping SARIF upload." in workflow
    assert "actions/upload-artifact@" not in workflow
    assert "scorecard-results" not in workflow


def test_version_synchronization_across_release_manifests() -> None:
    def is_oci_package(package: dict[str, object]) -> bool:
        return package.get("registryType") == "oci" or package.get("registry") in {
            "container",
            "oci",
        }

    root = Path(__file__).resolve().parents[2]
    config = (root / "release-please-config.json").read_text(encoding="utf-8")
    release_please = json.loads(config)
    manifest = json.loads((root / ".release-please-manifest.json").read_text(encoding="utf-8"))
    wrapper = json.loads((root / "npm-wrapper" / "package.json").read_text(encoding="utf-8"))
    pyproject = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))
    mcp = json.loads((root / "mcp.json").read_text(encoding="utf-8"))
    server = json.loads((root / "server.json").read_text(encoding="utf-8"))
    init_py = (root / "src" / "kicad_mcp" / "__init__.py").read_text(encoding="utf-8")

    version = manifest["."]
    assert "npm-wrapper/package.json" in config
    extra_files = release_please["packages"]["."]["extra-files"]
    assert {
        (entry["path"], entry.get("jsonpath"))
        for entry in extra_files
        if entry.get("type") == "json"
    } == {
        ("npm-wrapper/package.json", "$.version"),
        ("mcp.json", "$.version"),
        ("mcp.json", "$.packages[0].version"),
        ("server.json", "$.version"),
        ("server.json", "$.packages[0].version"),
    }
    assert wrapper["version"] == pyproject["project"]["version"] == version
    assert mcp["version"] == server["version"] == version
    assert all(
        package["version"] == version for package in mcp["packages"] if not is_oci_package(package)
    )
    assert all(
        package["version"] == version
        for package in server["packages"]
        if not is_oci_package(package)
    )
    assert all("version" not in package for package in mcp["packages"] if is_oci_package(package))
    assert all(
        "version" not in package for package in server["packages"] if is_oci_package(package)
    )
    assert f'__version__ = "{version}"' in init_py
    assert "https://oaslananka.github.io/kicad-mcp-pro" in wrapper["homepage"]


def test_release_workflow_retries_post_publish_smoke_check() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")
    shell_suppression = "||" + " true"

    smoke_start = workflow.index("Post-publish smoke check")
    smoke_end = workflow.index("actions/upload-artifact@", smoke_start)
    smoke_block = workflow[smoke_start:smoke_end]

    assert "for attempt in {1..10}; do" in smoke_block
    assert "retrying in 30 s" in smoke_block
    assert (
        'uv tool run --from "kicad-mcp-pro==${PACKAGE_VERSION}" kicad-mcp-pro --help' in smoke_block
    )
    assert (
        'uv tool run --from "kicad-mcp-pro==${PACKAGE_VERSION}" kicad-mcp-pro health --json'
        in smoke_block
    )
    assert 'uv run --no-project --with "kicad-mcp-pro==${PACKAGE_VERSION}"' in smoke_block
    assert "import kicad_mcp" in smoke_block
    assert "Smoke check failed:" in smoke_block
    assert "--dry-run" not in smoke_block
    assert shell_suppression not in smoke_block


def test_release_workflow_sets_up_python_before_sigstore_signing() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")
    setup_action = "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065"

    setup_steps = [
        match.start()
        for match in re.finditer(
            r"^[ \t]+- name: Set up Python for Sigstore$",
            workflow,
            flags=re.MULTILINE,
        )
    ]
    signing_steps = [
        match.start()
        for match in re.finditer(
            r"^[ \t]+- name: Sign release artifacts with Sigstore$",
            workflow,
            flags=re.MULTILINE,
        )
    ]

    assert len(setup_steps) == len(signing_steps) == 2

    for setup_step, signing_step in zip(setup_steps, signing_steps, strict=True):
        clear_step = workflow.rfind("Clear project virtualenv for signing action", 0, signing_step)
        next_boundary = re.search(
            r"(?m)^(?: {6}- |  [A-Za-z0-9_-]+:)",
            workflow[signing_step + 1 :],
        )
        next_step = (
            signing_step + 1 + next_boundary.start() if next_boundary is not None else len(workflow)
        )
        setup_block = workflow[setup_step:signing_step]
        signing_block = workflow[signing_step:next_step]

        assert clear_step != -1
        assert clear_step < setup_step < signing_step
        assert setup_action in setup_block
        assert 'python-version: "3.12"' in setup_block
        assert "UV_PYTHON:" not in signing_block
        assert 'UV_NO_CONFIG: "1"' in signing_block
        assert "UV_CACHE_DIR:" in signing_block
        assert "sigstore-uv-python-dir" in signing_block

    manual_start = workflow.index("  finish-existing-release:")
    manual_setup = workflow.index("Set up Python for Sigstore", manual_start)
    manual_signing = workflow.index("Sign release artifacts with Sigstore", manual_setup)
    manual_setup_block = workflow[manual_setup:manual_signing]

    assert "steps.recovery-target.outputs.finish_needed == 'true'" in manual_setup_block


def test_release_workflow_manual_dispatch_only_finishes_existing_release() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")
    legacy_input = "inputs." + "version"
    jobs_match = re.search(r"^jobs:\n", workflow, flags=re.MULTILINE)
    assert jobs_match is not None
    jobs_block = workflow[jobs_match.start() :]
    manual_match = re.search(r"^  finish-existing-release:\n", jobs_block, flags=re.MULTILINE)
    assert manual_match is not None
    manual_start = manual_match.start()
    automatic_jobs = jobs_block[:manual_start]
    manual_remainder = jobs_block[manual_start:]
    next_job_match = re.search(
        r"^  [a-zA-Z0-9_-]+:\n",
        manual_remainder[1:],
        flags=re.MULTILINE,
    )
    manual_job = (
        manual_remainder[: 1 + next_job_match.start()] if next_job_match else manual_remainder
    )
    release_tag = _workflow_input_default(workflow, "release_tag")
    release_sha = _workflow_input_default(workflow, "release_sha")

    assert "workflow_dispatch" in workflow
    assert "release_tag:" in workflow
    assert "release_sha:" in workflow
    assert "package_version:" not in workflow
    assert legacy_input not in workflow
    assert "inputs.release_tag" in workflow
    assert "inputs.release_sha" in workflow
    assert "outputs.version" in workflow
    assert "outputs.tag_name" in workflow
    assert "github.event_name == 'workflow_dispatch'" not in automatic_jobs
    assert "inputs.release_tag" not in automatic_jobs
    assert "inputs.release_sha" not in automatic_jobs
    assert "needs.release-please.outputs.release_created == 'true'" in automatic_jobs

    assert re.fullmatch(r"v\d+\.\d+\.\d+", release_tag)
    assert re.fullmatch(r"[0-9a-f]{40}", release_sha)
    assert f'allowed_tag="{release_tag}"' in manual_job
    assert f'allowed_sha="{release_sha}"' in manual_job
    assert "permissions:\n      contents: read" in manual_job
    assert "contents: write" not in manual_job
    assert "git ls-remote --tags" in manual_job
    assert "gh release view" in manual_job
    assert "GH_TOKEN: ${{ secrets.DOPPLER_GITHUB_SERVICE_TOKEN }}" in manual_job
    assert "finish_needed=true" in manual_job
    assert "steps.recovery-target.outputs.finish_needed == 'true'" in manual_job
    assert "Stage Python distributions for package index" in manual_job
    assert "packages-dir: dist-pypi/" in manual_job
    assert "actions/upload-artifact@" not in manual_job


def _workflow_input_default(workflow: str, name: str) -> str:
    input_match = re.search(
        rf"^      {re.escape(name)}:\n(?P<body>(?:        .+\n)+)",
        workflow,
        flags=re.MULTILINE,
    )
    assert input_match is not None
    default_match = re.search(
        r"^        default: (?P<value>\S+)$", input_match.group("body"), re.MULTILINE
    )
    assert default_match is not None
    return default_match.group("value")


def test_release_workflow_installs_actionlint_before_ci_check() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")

    setup_index = workflow.index("actions/setup-go@")
    install_index = workflow.index("Install workflow lint tools")
    check_index = workflow.index("corepack pnpm run check:ci")

    assert setup_index < install_index < check_index
    assert "go install github.com/rhysd/actionlint/cmd/actionlint@v1.7.7" in workflow
    assert 'echo "${HOME}/go/bin" >> "${GITHUB_PATH}"' in workflow


def test_release_please_uses_service_token_for_release_prs() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "release-please.yml"
    ).read_text(encoding="utf-8")

    assert "permissions:\n  contents: read" in workflow
    assert "contents: write" in workflow
    assert "pull-requests: write" in workflow
    assert "DOPPLER_GITHUB_SERVICE_TOKEN is required." in workflow
    assert "token: ${{ secrets.DOPPLER_GITHUB_SERVICE_TOKEN }}" in workflow
    assert "DOPPLER_GITHUB_SERVICE_TOKEN || github.token" not in workflow


def test_docs_workflow_deploys_only_from_org_repo() -> None:
    workflow = (
        Path(__file__).resolve().parents[2] / ".github" / "workflows" / "docs.yml"
    ).read_text(encoding="utf-8")
    shell_suppression = "||" + " true"

    assert "github.repository == 'oaslananka/kicad-mcp-pro'" in workflow
    assert "Mirror canonical GitHub Pages" not in workflow
    assert "CANONICAL_PAGES_TOKEN" not in workflow
    assert "github.com/oaslananka/kicad-mcp-pro.git" not in workflow
    assert "base64" not in workflow
    assert shell_suppression not in workflow


@pytest.mark.anyio
async def test_project_generate_design_prompt_uses_design_intent(sample_project: Path) -> None:
    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    await call_tool_text(
        server,
        "project_set_design_intent",
        {
            "critical_nets": ["USB_DP", "USB_DN"],
            "manufacturer": "JLCPCB",
            "manufacturer_tier": "standard",
            "power_rails": [
                {
                    "name": "+3V3",
                    "voltage_v": 3.3,
                    "current_max_a": 0.5,
                    "source_ref": "U_REG",
                }
            ],
        },
    )

    prompt = await call_tool_text(
        server,
        "project_generate_design_prompt",
        {"circuit_description": "USB sensor", "target_fab": ""},
    )

    assert "USB sensor" in prompt
    assert "USB_DP, USB_DN" in prompt
    assert "+3V3" in prompt
    assert "jlcpcb_standard" in prompt.lower()


@pytest.mark.anyio
async def test_export_manufacturing_package_accepts_explicit_variant(
    sample_project: Path,
    monkeypatch,
) -> None:
    commands: list[list[str]] = []

    def fake_run_cli_variants(variants: list[list[str]]) -> tuple[int, str, str]:
        command = variants[0]
        commands.append(command)
        output_index = command.index("--output") + 1
        output_path = Path(command[output_index])
        if output_path.suffix:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("generated\n", encoding="utf-8")
        else:
            output_path.mkdir(parents=True, exist_ok=True)
            (output_path / "board-F_Cu.gbr").write_text("gerber\n", encoding="utf-8")
        return 0, "", ""

    monkeypatch.setattr(
        "kicad_mcp.tools.validation._evaluate_project_gate",
        lambda **_kwargs: [],
    )
    monkeypatch.setattr("kicad_mcp.tools.export._run_cli_variants", fake_run_cli_variants)
    monkeypatch.setattr(
        "kicad_mcp.tools.export.get_cli_capabilities",
        lambda _cli: CliCapabilities(
            version="KiCad 10.0.1",
            gerber_command="gerber",
            drill_command="drill",
            position_command="pos",
            supports_ipc2581=True,
            supports_cli_variant=True,
        ),
    )

    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})
    await call_tool_text(server, "variant_create", {"name": "lite"})

    result = await call_tool_text(server, "export_manufacturing_package", {"variant": "lite"})

    assert "Gerber export completed" in result
    assert commands
    assert all("--variant" in command and "lite" in command for command in commands)
    active = await call_tool_text(server, "variant_list", {})
    assert '"active_variant": "default"' in active


def test_structured_error_code_unavailable() -> None:
    from kicad_mcp.server import _structured_tool_error_from_message

    result = _structured_tool_error_from_message("kicad-cli is missing")
    assert result.isError is True
    assert result.structuredContent["error_code"] == "CLI_UNAVAILABLE"


def test_health_doctor_schema_and_secret_masking(
    sample_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _ = sample_project
    reset_config()
    cfg = get_config()
    cfg.auth_token = "secret-token"  # noqa: S105
    cfg.kicad_token = "kicad-secret"  # noqa: S105

    from kicad_mcp.diagnostics import build_doctor_report, build_health_report

    health = build_health_report()
    assert health.ok is True
    config_diag = health.config
    assert config_diag.auth_token == {"configured": True}
    assert config_diag.kicad_token == {"configured": True}
    # Ensure secrets are NOT in the output
    health_json = health.model_dump_json()
    assert "secret-token" not in health_json
    assert "kicad-secret" not in health_json

    doctor = build_doctor_report()
    # doctor might not be 'ok' if KiCad is not running, but it should have stable keys
    assert hasattr(doctor, "status")
    assert hasattr(doctor, "checks")
    doctor_json = doctor.model_dump_json()
    assert "secret-token" not in doctor_json
    assert "kicad-secret" not in doctor_json


@pytest.mark.anyio
async def test_export_path_traversal_rejection_strengthened(
    sample_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "kicad_mcp.tools.export.get_cli_capabilities",
        lambda _cli: CliCapabilities(
            version="KiCad 10.0.1",
            supports_step=True,
        ),
    )
    server = build_server("full")
    await call_tool_text(server, "kicad_set_project", {"project_dir": str(sample_project)})

    # Test various traversal attempts
    traversals = [
        "../outside.step",
        "../../outside.step",
        "/absolute/path/board.step",
        "nested/../../outside.step",
        " ",
        ".",
        "..",
    ]

    for path in traversals:
        result = await call_tool_text(server, "export_step", {"output_path": path})
        assert "Invalid output path" in result or "traversal" in result.lower()


def test_tool_registry_invariants_and_profiles() -> None:
    from kicad_mcp.tools.router import (
        TOOL_CATEGORIES,
        available_profiles,
        categories_for_profile,
    )

    # All tools in categories must exist in some way or be registered
    for _category, info in TOOL_CATEGORIES.items():
        assert "tools" in info
        assert isinstance(info["tools"], list)

    # Critical profiles must be stable
    for profile in ["full", "minimal", "pcb", "schematic", "agent_full"]:
        assert profile in available_profiles()
        categories = categories_for_profile(profile)
        assert len(categories) > 0


@pytest.mark.anyio
async def test_lazy_startup_idempotency_and_deferral() -> None:
    from kicad_mcp.server import build_server

    server = build_server("minimal", defer_registration=True)
    assert server._lazy_registration_complete is False

    # First call should trigger registration
    tools = await server.list_tools()
    assert server._lazy_registration_complete is True
    count = len(tools)

    # Repeated calls should be idempotent and not duplicate tools
    tools_repeated = await server.list_tools()
    assert server._lazy_registration_complete is True
    assert len(tools_repeated) == count
