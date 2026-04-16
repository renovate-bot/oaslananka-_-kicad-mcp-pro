"""Static discovery metadata for HTTP clients."""

from __future__ import annotations

from . import __version__
from .tools.router import available_profiles


def get_wellknown_metadata() -> dict[str, object]:
    """Return server discovery metadata for ``/.well-known/mcp-server``."""
    return {
        "name": "kicad-mcp-pro",
        "version": __version__,
        "description": "AI-powered PCB and schematic design with KiCad",
        "capabilities": ["tools", "resources", "prompts"],
        "profiles": available_profiles(),
        "kicad_version_required": "9.0",
        "transport": ["stdio", "streamable-http"],
        "docs": "https://oaslananka.github.io/kicad-mcp-pro",
        "registry": "io.github.oaslananka/kicad-mcp-pro",
    }
