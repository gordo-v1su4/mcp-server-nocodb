# Standard FastMCP NocoDB Server Dockerfile with uv
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy project files
COPY pyproject.toml .
COPY README.md .
COPY nocodb_mcp_server.py .

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with uv
RUN uv pip install -e .

# Create non-root user
RUN addgroup --gid 1001 mcpuser && \
    adduser --uid 1001 --gid 1001 --shell /bin/bash --disabled-password --no-create-home mcpuser

# Change ownership and switch user
RUN chown -R mcpuser:mcpuser /app /opt/venv
USER mcpuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/ || exit 1

# Start the server
CMD ["python", "nocodb_mcp_server.py"]