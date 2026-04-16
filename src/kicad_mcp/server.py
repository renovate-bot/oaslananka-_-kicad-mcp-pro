"""KiCad MCP Pro server entrypoint."""
# mypy: disable-error-code=untyped-decorator

from __future__ import annotations

import asyncio
import os
import secrets
from collections.abc import Callable

import structlog
import typer
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP
from mcp.types import Icon, ToolAnnotations
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from typer.models import OptionInfo

from . import __version__
from .config import KiCadMCPConfig, get_config, reset_config
from .connection import KiCadConnectionError, get_board
from .discovery import ensure_studio_project_watcher, find_kicad_version
from .prompts import workflows
from .resources import board_state, studio_context
from .tools import (
    dfm,
    emc_compliance,
    export,
    library,
    manufacturing,
    pcb,
    power_integrity,
    project,
    router,
    routing,
    schematic,
    signal_integrity,
    simulation,
    validation,
    variants,
    version_control,
)
from .tools.metadata import infer_tool_annotations
from .tools.router import available_profiles, categories_for_profile
from .utils.logging import setup_logging
from .wellknown import get_wellknown_metadata

logger = structlog.get_logger(__name__)
app = typer.Typer(help="KiCad MCP Pro server for PCB and schematic workflows.")
AnyFunction = Callable[..., object]


class _SyncServerHandle:
    """Compatibility wrapper that exposes sync-friendly discovery helpers."""

    def __init__(self, server: FastMCP) -> None:
        self._server = server

    def list_tools(self) -> object:
        """Return tool metadata synchronously when called outside an event loop."""
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self._server.list_tools())
        return self._server.list_tools()

    def __getattr__(self, name: str) -> object:
        return getattr(self._server, name)


class _StaticTokenVerifier:
    """Simple bearer-token verifier for local HTTP bridge deployments."""

    def __init__(self, expected_token: str) -> None:
        self._expected_token = expected_token

    async def verify_token(self, token: str) -> AccessToken | None:
        if secrets.compare_digest(token, self._expected_token):
            return AccessToken(token=token, client_id="kicad-studio", scopes=["mcp"])
        return None


class KiCadFastMCP(FastMCP):
    """FastMCP extension that auto-infers tool annotations and adds CORS support."""

    def tool(
        self,
        name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        annotations: ToolAnnotations | None = None,
        icons: list[Icon] | None = None,
        meta: dict[str, object] | None = None,
        structured_output: bool | None = None,
    ) -> Callable[[AnyFunction], AnyFunction]:
        def decorator(func: AnyFunction) -> AnyFunction:
            merged = infer_tool_annotations(name or func.__name__, explicit=annotations)
            return super(KiCadFastMCP, self).tool(
                name=name,
                title=title,
                description=description,
                annotations=merged or None,
                icons=icons,
                meta=meta,
                structured_output=structured_output,
            )(func)

        return decorator

    def streamable_http_app(self) -> Starlette:
        app = super().streamable_http_app()
        origins = get_config().cors_origin_list
        if origins:
            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=["Authorization", "Content-Type", "MCP-Protocol-Version"],
            )
        return app


def _server_base_url(cfg: KiCadMCPConfig) -> str:
    host = cfg.host if cfg.host not in {"0.0.0.0", "::"} else "127.0.0.1"  # noqa: S104
    return f"http://{host}:{cfg.port}"


def build_server(profile: str | None = None) -> FastMCP:
    """Build a FastMCP server instance for the active profile."""
    cfg = get_config()
    selected_profile = profile or cfg.profile
    token_verifier = _StaticTokenVerifier(cfg.auth_token) if cfg.auth_token else None
    auth = None
    if cfg.auth_token:
        base_url = _server_base_url(cfg)
        auth = AuthSettings(
            issuer_url=base_url,
            resource_server_url=base_url,
            required_scopes=["mcp"],
        )

    server = KiCadFastMCP(
        name="kicad-mcp-pro",
        instructions=(
            "KiCad MCP Pro Server for project setup, schematic capture, PCB editing, "
            "validation, and manufacturing export. Start with kicad_get_version(), "
            "kicad_set_project(), and project_get_design_spec()."
        ),
        website_url="https://oaslananka.github.io/kicad-mcp-pro",
        host=cfg.host,
        port=cfg.port,
        streamable_http_path=cfg.mount_path,
        mount_path=cfg.mount_path,
        log_level=cfg.log_level,
        json_response=True,
        stateless_http=True,
        auth=auth,
        token_verifier=token_verifier,
    )

    @server.custom_route("/.well-known/mcp-server", methods=["GET"], include_in_schema=False)
    async def _well_known_mcp(_request: Request) -> JSONResponse:
        return JSONResponse(get_wellknown_metadata())

    @server.custom_route("/well-known/mcp-server", methods=["GET"], include_in_schema=False)
    async def _well_known_mcp_compat(_request: Request) -> JSONResponse:
        return JSONResponse(get_wellknown_metadata())

    router.register(server)
    project.register(server)

    enabled = set(categories_for_profile(selected_profile))
    if "pcb_read" in enabled or "pcb_write" in enabled:
        pcb.register(server)
    if "schematic" in enabled:
        schematic.register(server)
        variants.register(server)
    if "library" in enabled:
        library.register(server)
    if "export" in enabled or "release_export" in enabled:
        export.register(server, include_low_level_exports="export" in enabled)
    if "validation" in enabled:
        validation.register(server)
    if "dfm" in enabled:
        dfm.register(server)
    if "routing" in enabled:
        routing.register(server)
    if "power_integrity" in enabled:
        power_integrity.register(server)
    if "emc" in enabled:
        emc_compliance.register(server)
    if "signal_integrity" in enabled:
        signal_integrity.register(server)
    if "simulation" in enabled:
        simulation.register(server)
    if "version_control" in enabled:
        version_control.register(server)
    if "manufacturing" in enabled:
        manufacturing.register(server)

    board_state.register(server)
    studio_context.register(server)
    workflows.register(server)

    if cfg.studio_watch_dir is not None:
        ensure_studio_project_watcher(cfg.studio_watch_dir)

    return server


def create_server(profile: str | None = None) -> _SyncServerHandle:
    """Backward-compatible helper used by benchmark and verification scripts."""
    return _SyncServerHandle(build_server(profile))


def _ipc_status_summary() -> str:
    try:
        get_board()
    except KiCadConnectionError as exc:
        return f"unavailable ({str(exc).splitlines()[0]})"
    return "connected (PCB editor available)"


def _print_startup_diagnostics(cfg: KiCadMCPConfig) -> None:
    """Emit a concise startup summary without writing directly to stdio transport."""
    logger.info(
        "startup_diagnostics",
        profile=cfg.profile,
        kicad_cli=str(cfg.kicad_cli),
        kicad_version=find_kicad_version(cfg.kicad_cli) or "unknown",
        project_dir=str(cfg.project_dir) if cfg.project_dir else None,
        gate_mode="release-export-only",
        ipc_status=_ipc_status_summary(),
    )


@app.callback(invoke_without_command=True)
def main_callback(
    transport: str | None = typer.Option(
        None, help="Transport: stdio, http, sse, streamable-http"
    ),
    host: str | None = typer.Option(None, help="HTTP bind host"),
    port: int | None = typer.Option(None, help="HTTP bind port"),
    project_dir: str | None = typer.Option(None, help="Active KiCad project directory"),
    log_level: str | None = typer.Option(None, help="Log level"),
    log_format: str | None = typer.Option(None, help="Log format: console or json"),
    profile: str | None = typer.Option(
        None, help=f"Server profile: {', '.join(available_profiles())}"
    ),
    experimental: bool | None = typer.Option(None, help="Enable experimental tools"),
) -> None:
    """Start the KiCad MCP Pro server."""
    cli_env = {
        "KICAD_MCP_TRANSPORT": transport,
        "KICAD_MCP_HOST": host,
        "KICAD_MCP_PORT": (
            str(port) if port is not None and not isinstance(port, OptionInfo) else None
        ),
        "KICAD_MCP_LOG_LEVEL": log_level,
        "KICAD_MCP_LOG_FORMAT": log_format,
        "KICAD_MCP_PROFILE": profile,
        "KICAD_MCP_PROJECT_DIR": project_dir,
    }
    for key, value in cli_env.items():
        if value is not None and not isinstance(value, OptionInfo):
            os.environ[key] = value
    if experimental is not None and not isinstance(experimental, OptionInfo):
        os.environ["KICAD_MCP_ENABLE_EXPERIMENTAL_TOOLS"] = "true" if experimental else "false"

    reset_config()
    cfg = get_config()
    setup_logging(cfg.log_level, cfg.log_format)

    selected_transport = "stdio" if cfg.transport == "stdio" else "streamable-http"
    server = build_server(cfg.profile)
    _print_startup_diagnostics(cfg)
    logger.info(
        "starting_kicad_mcp_pro",
        version=__version__,
        transport=selected_transport,
        profile=cfg.profile,
    )

    if selected_transport == "stdio":
        server.run(transport="stdio")
        return

    server.run(transport="streamable-http", mount_path=cfg.mount_path)


def main() -> None:
    """CLI entrypoint used by the package script."""
    app()


if __name__ == "__main__":
    main()
