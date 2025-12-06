FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy all files from server directory to /app/server/ to match import structure
COPY . ./server/

# Install dependencies (uv sync needs pyproject.toml)
WORKDIR /app/server
RUN uv sync

# Run the application (from /app so server package is importable)
WORKDIR /app
ENV PYTHONPATH=/app
CMD ["/app/server/.venv/bin/uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]

