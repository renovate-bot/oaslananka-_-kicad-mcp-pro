# Claude Code

The simplest Claude Code setup uses `stdio`. For longer-lived multi-client setups, prefer streamable HTTP.

## Recommendation

- Local single-user session: `stdio`
- VS Code webview or KiCad Studio bridge: `http`
- If you need local auth, set `KICAD_MCP_AUTH_TOKEN`
