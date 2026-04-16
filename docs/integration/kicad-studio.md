# KiCad Studio

The `kicad-studio` extension connects through a local HTTP bridge rather than stdio.

## Recommended Environment

```bash
KICAD_MCP_TRANSPORT=http
KICAD_MCP_HOST=127.0.0.1
KICAD_MCP_PORT=27185
KICAD_MCP_CORS_ORIGINS=vscode-webview://
KICAD_MCP_AUTH_TOKEN=replace-with-local-token
KICAD_MCP_STUDIO_WATCH_DIR=/absolute/path/to/projects
```

`27185` is the recommended Studio bridge port for local setups. The server still defaults to `3334`, so set the port explicitly if you want this convention.

## Integration Points

- `studio_push_context()` pushes active file, DRC errors, selected net/reference, and cursor state into the server.
- `kicad://studio/context` is the resource that agents can read directly.
- `KICAD_MCP_STUDIO_WATCH_DIR` watches for `.kicad_pro` updates and auto-selects the active project.
