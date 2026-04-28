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
USER kicadmcp
CMD ["kicad-mcp-pro", "--transport", "http"]
