# Standard FastMCP Server Template

This document defines the standard pattern for creating MCP servers using FastMCP with streamable-http transport.

## 🏗️ Architecture Pattern

Use this consistent architecture across all MCP servers:

```
Claude Code → Hosted FastMCP Server (SSE) → External API/Service
```

## 📁 File Structure

```
mcp-server-{service}/
├── {service}-mcp-server.py     # Main FastMCP server (required)
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container config
├── docker-compose.yaml         # Docker Compose config
├── CLAUDE.md                   # Claude Code guidance
├── README.md                   # User documentation
└── .env.example               # Environment variables template
```

## 🔧 Core Implementation Pattern

### 1. Server Initialization

```python
"""
{Service} MCP Server - Standard FastMCP Implementation
"""

import json
import logging
import os
import sys
import time
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"/tmp/{service}_mcp_server.log", mode="a")
        if os.path.exists("/tmp")
        else logging.NullHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Server configuration
server_host = "0.0.0.0"
server_port = int(os.getenv("PORT", 3001))  # Use consistent port pattern
```

### 2. Context Management

```python
@dataclass
class {Service}Context:
    """Context for {Service} MCP server."""
    # Service-specific configuration
    api_url: str
    api_token: str
    session: Optional[Any] = None  # HTTP client session
    startup_time: float = None

    def __post_init__(self):
        if self.startup_time is None:
            self.startup_time = time.time()

    async def get_session(self):
        """Get or create HTTP session"""
        # Implement service-specific session logic
        pass

    async def close_session(self):
        """Clean up HTTP session"""
        # Implement cleanup logic
        pass

@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[{Service}Context]:
    """Lifecycle manager for {Service} MCP server"""
    logger.info("🚀 Starting {Service} MCP Server...")

    try:
        # Get configuration from environment
        api_url = os.getenv("{SERVICE}_URL", "https://default.url")
        api_token = os.getenv("{SERVICE}_API_TOKEN")

        if not api_token:
            raise ValueError("{SERVICE}_API_TOKEN environment variable is required")

        # Create context
        context = {Service}Context(
            api_url=api_url.rstrip("/"),
            api_token=api_token
        )

        logger.info(f"✓ {Service} URL: {context.api_url}")
        logger.info("✓ {Service} MCP server ready")

        yield context

    except Exception as e:
        logger.error(f"💥 Critical error in lifespan setup: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        logger.info("🧹 Cleaning up {Service} MCP server...")
        if hasattr(context, 'session'):
            await context.close_session()
        logger.info("✅ {Service} MCP server shutdown complete")
```

### 3. FastMCP Server Setup

```python
# Define MCP instructions
MCP_INSTRUCTIONS = """
# {Service} MCP Server Instructions

## 🚨 CRITICAL RULES
1. **Authentication Required** - All operations require valid API token
2. **Error Handling** - Always provide clear error messages
3. **Resource Management** - Use proper pagination for large datasets

## 📋 Available Tools

### Core Operations
- `{service}_test_connection()` - Test service connection
- `{service}_list_resources()` - List available resources
- `{service}_get_item(id)` - Get specific item
- `{service}_create_item(data)` - Create new item
- `{service}_update_item(id, data)` - Update existing item
- `{service}_delete_item(id)` - Delete item

## 🔍 Common Workflows
(Service-specific workflows)

## 🎯 Best Practices
- Always test connection before starting work
- Use meaningful data with proper validation
- Handle errors gracefully and provide user feedback
- Use pagination for large result sets
"""

# Initialize FastMCP server
try:
    logger.info("🏗️ {SERVICE} MCP SERVER INITIALIZATION")
    logger.info("   Server Name: {service}-mcp-server")
    logger.info("   Description: Standard MCP server for {Service} integration")

    mcp = FastMCP(
        "{service}-mcp-server",
        instructions=MCP_INSTRUCTIONS,
        lifespan=lifespan,
        host=server_host,
        port=server_port,
        streamable_http_path="/"
    )
    logger.info("✓ FastMCP server instance created successfully")

except Exception as e:
    logger.error(f"✗ Failed to create FastMCP server: {e}")
    logger.error(traceback.format_exc())
    raise
```

### 4. Standard Tools

```python
# Health check tool (required for all servers)
@mcp.tool()
async def health_check(ctx: Context) -> str:
    """
    Check health status of {Service} MCP server.
    
    Returns:
        JSON with health status, uptime, and service connection info
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context", None)
        
        if context is None:
            return json.dumps({
                "success": True,
                "status": "starting",
                "message": "{Service} MCP server is initializing...",
                "timestamp": datetime.now().isoformat(),
            })

        # Test service connection
        service_status = "unknown"
        try:
            # Implement service-specific health check
            service_status = "healthy"  # or "unhealthy"
        except Exception as e:
            service_status = f"error: {str(e)}"

        return json.dumps({
            "success": True,
            "status": "healthy",
            "service_status": service_status,
            "uptime_seconds": time.time() - context.startup_time,
            "service_url": context.api_url,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        })

# Service-specific tools
@mcp.tool()
async def {service}_test_connection(ctx: Context) -> str:
    """
    Test connection to {Service} and return basic info.
    
    Returns:
        JSON with connection status and service info
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        
        # Implement connection test logic
        # Return standardized response format
        
        return json.dumps({
            "success": True,
            "message": "✅ Connection successful",
            "service_info": {},  # Service-specific info
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"{Service} connection test failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Connection test failed: {str(e)}",
        })

# Add more service-specific tools following this pattern
```

### 5. Main Entry Point

```python
def main():
    """Main entry point for the {Service} MCP server."""
    try:
        logger.info("🚀 Starting {Service} MCP Server")
        logger.info("   Mode: Streamable HTTP")
        logger.info(f"   URL: http://{server_host}:{server_port}/")
        
        # Run with streamable-http transport
        mcp.run(transport="streamable-http")

    except Exception as e:
        logger.error(f"💥 Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 {Service} MCP server stopped by user")
    except Exception as e:
        logger.error(f"💥 Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
```

## 📦 Requirements Template

```txt
# Standard FastMCP dependencies
mcp
aiohttp
python-dotenv
pydantic

# Service-specific dependencies
# Add as needed for your service integration
```

## 🐳 Docker Template

```dockerfile
# Standard FastMCP Server Dockerfile
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
COPY {service}-mcp-server.py .

# Create non-root user
RUN addgroup --gid 1001 mcpuser && \
    adduser --uid 1001 --gid 1001 --shell /bin/bash --disabled-password --no-create-home mcpuser

# Change ownership and switch user
RUN chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/ || exit 1

# Start the server
CMD ["python", "{service}-mcp-server.py"]
```

## 🔧 Environment Variables

Standard environment variables across all MCP servers:

```bash
# Required
{SERVICE}_API_TOKEN=your-api-token-here

# Optional with defaults
{SERVICE}_URL=https://service.example.com
PORT=3001
LOG_LEVEL=INFO
```

## 📋 Naming Conventions

- **Repository**: `mcp-server-{service}`
- **Main File**: `{service}-mcp-server.py`
- **Docker Image**: `your-username/{service}-mcp-server`
- **Tool Prefix**: `{service}_`
- **Environment Variables**: `{SERVICE}_`

## 🎯 Quality Standards

1. **Error Handling**: All tools return JSON with `success` boolean
2. **Logging**: Use structured logging with timestamps
3. **Documentation**: Include comprehensive MCP_INSTRUCTIONS
4. **Health Checks**: Always implement health_check tool
5. **Resource Cleanup**: Proper async context management
6. **Type Safety**: Use dataclasses and type hints
7. **Environment Config**: Follow 12-factor app principles

## 🚀 Deployment Pattern

1. **Local Development**: Direct Python execution
2. **Docker**: Containerized deployment
3. **Coolify/Production**: Docker Compose with health checks
4. **Claude Integration**: SSE connection to hosted server

## 📝 Documentation Template

Every MCP server should include:

- **CLAUDE.md**: Development guidance for Claude Code
- **README.md**: User setup and usage instructions
- **API documentation**: Tool descriptions and examples
- **Deployment guide**: Docker and production setup

This standard ensures consistency, maintainability, and ease of development across all MCP servers.