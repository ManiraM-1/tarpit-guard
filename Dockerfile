# Runs the tarpit-guard MCP server over stdio.
#   docker build -t tarpit-guard .
#   docker run -i --rm -v "$PWD:/work:ro" tarpit-guard
# Mount the code you want checked (read-only) and pass paths under /work.
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY tarpit_guard ./tarpit_guard
RUN pip install --no-cache-dir ".[mcp]"

WORKDIR /work
CMD ["tarpit-guard-mcp"]
