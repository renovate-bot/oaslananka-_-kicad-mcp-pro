FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS builder
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src/ src/
RUN uv sync --frozen --extra http

FROM base AS runtime
RUN groupadd --system kicadmcp \
    && useradd --system --gid kicadmcp --home-dir /app --shell /usr/sbin/nologin kicadmcp
COPY --from=builder --chown=kicadmcp:kicadmcp /app/.venv .venv
COPY --chown=kicadmcp:kicadmcp src/ src/
COPY --chown=kicadmcp:kicadmcp README.md LICENSE ./
LABEL org.opencontainers.image.description="KiCad MCP Pro - kicad-cli export and validation tools require a KiCad installation mounted at /usr/bin/kicad-cli"
ENV PATH="/app/.venv/bin:$PATH"
ENV KICAD_MCP_TRANSPORT=streamable-http
ENV KICAD_MCP_HOST=0.0.0.0
ENV KICAD_MCP_KICAD_CLI=/usr/bin/kicad-cli
EXPOSE 3334
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import http.client, sys; c = http.client.HTTPConnection('localhost', 3334, timeout=4); c.request('GET', '/health'); r = c.getresponse(); sys.exit(0 if r.status < 500 else 1)"
USER kicadmcp
CMD ["kicad-mcp-pro", "--transport", "http"]
