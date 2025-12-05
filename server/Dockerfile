FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Copy project files
COPY . ./

# Install dependencies
RUN uv sync 

# Run the application
CMD ["uv", "run", "python", "main.py"]

