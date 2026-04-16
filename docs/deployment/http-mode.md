# HTTP Mode

The server can run in `streamable-http` mode in addition to `stdio`.

## Behavior

- MCP endpoint: `/mcp`
- Discovery endpoint: `/.well-known/mcp-server`
- Optional bearer-token auth
- Optional CORS allowlist
- Stateless HTTP by default

The default HTTP port is `3334`. For KiCad Studio local bridge setups, `27185` is a good convention if you want a dedicated port.

## Environment Variables

- `KICAD_MCP_TRANSPORT=http`
- `KICAD_MCP_HOST=127.0.0.1`
- `KICAD_MCP_PORT=3334`
- `KICAD_MCP_CORS_ORIGINS=vscode-webview://`
- `KICAD_MCP_AUTH_TOKEN=...`
