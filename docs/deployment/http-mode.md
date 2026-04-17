# HTTP Mode

The server can run in `streamable-http` mode in addition to `stdio`.

## Behavior

- MCP endpoint: `/mcp`
- Discovery endpoint: `/.well-known/mcp-server`
- Optional bearer-token auth
- Optional CORS allowlist using explicit `http://` or `https://` origins only
- Wildcard CORS (`*`) is rejected intentionally
- Stateless HTTP by default, with opt-in stateful HTTP for session-aware clients
- Legacy SSE stays disabled unless explicitly enabled

The default HTTP port is `3334`. For KiCad Studio local bridge setups, `27185` is a good convention if you want a dedicated port.

## Environment Variables

- `KICAD_MCP_TRANSPORT=http`
- `KICAD_MCP_HOST=127.0.0.1`
- `KICAD_MCP_PORT=3334`
- `KICAD_MCP_CORS_ORIGINS=https://app.example.com,http://127.0.0.1:3334`
- `KICAD_MCP_AUTH_TOKEN=...`
- `KICAD_MCP_STATEFUL_HTTP=true`
- `KICAD_MCP_LEGACY_SSE=true`

## Notes

- When bearer auth is enabled, cross-origin `POST /mcp` requests are checked against `KICAD_MCP_CORS_ORIGINS`.
- If you run over `stdio`, `KICAD_MCP_AUTH_TOKEN` is ignored and a startup warning is emitted.
- Use explicit origins instead of browser- or IDE-specific pseudo-schemes so the allowlist stays valid and auditable.
