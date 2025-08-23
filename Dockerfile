# FastAPI NocoDB MCP Server Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mcp-server-fastapi.py .
COPY nocodb-mcp-tools.json .

# Create non-root user
RUN addgroup --gid 1001 nodejs && \
    adduser --uid 1001 --gid 1001 --shell /bin/bash --disabled-password --no-create-home nocodb

# Change ownership
RUN chown -R nocodb:nodejs /app
USER nocodb

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import aiohttp, asyncio; asyncio.run(aiohttp.ClientSession().get('http://localhost:3001/health'))" || exit 1

# Start the server
CMD ["uvicorn", "mcp-server-fastapi:app", "--host", "0.0.0.0", "--port", "3001", "--workers", "1"]
