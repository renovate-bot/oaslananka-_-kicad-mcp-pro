# Docker Deployment

Docker can be used to run the HTTP transport for remote access or an internal team bridge.

## Basic Flow

```bash
docker build -t kicad-mcp-pro .
docker run --rm -p 27185:27185 \
  -e KICAD_MCP_TRANSPORT=http \
  -e KICAD_MCP_PORT=27185 \
  -e KICAD_MCP_HOST=0.0.0.0 \
  kicad-mcp-pro
```

For production-style deployments, set `KICAD_MCP_AUTH_TOKEN` and keep `KICAD_MCP_CORS_ORIGINS` narrowly scoped.
