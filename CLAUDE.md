# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a standard FastMCP Model Context Protocol server that provides NocoDB integration for Claude Code. The server uses the official MCP streamable-http transport for remote hosting, following the same pattern as Archon MCP server.

## Key Components

- **FastMCP Server** (`nocodb-mcp-server.py`) - Standard MCP server with NocoDB API integration
- **Docker Configuration** - Production deployment with health checks and monitoring
- **Legacy Files** (`.old` extension) - Previous custom HTTP API implementation

## Development Commands

### Local Development
```bash
# Start FastMCP server in development mode
npm run dev
# Or: python nocodb-mcp-server.py

# Start production server
npm start
# Or: python nocodb-mcp-server.py

# Health check
npm test
# Or: curl http://localhost:3001/
```

### Docker Development
```bash
# Build and run with Docker Compose
npm run compose-up

# View logs
npm run compose-logs

# Stop services
npm run compose-down

# Build Docker image
npm run docker-build

# Run Docker container
npm run docker-run
```

### Testing Tools
```bash
# Test server directly
curl http://localhost:3001/

# Test via Claude Code MCP tools (once connected)
# Tools: nocodb_test_connection, nocodb_list_projects, etc.
```

## Architecture

### Server Architecture
- **FastMCP Application**: Standard MCP server with streamable-http transport
- **Tool Registration**: Standard `@mcp.tool()` decorators for each NocoDB operation
- **Context Management**: Async context with aiohttp session pooling
- **Error Handling**: Comprehensive error handling with JSON responses

### Deployment Architecture
```
Claude Code → Hosted FastMCP Server (SSE) → NocoDB API
```

### Environment Variables
- `NOCODB_API_TOKEN`: NocoDB API authentication token (required)
- `NOCODB_URL`: NocoDB instance URL (defaults to https://nocodb.v1su4.com)
- `PORT`: Server port (defaults to 3001)

### Tool Categories
1. **Connection & Management**: Test connections, list projects/tables
2. **Data Operations**: CRUD operations (get, create, update, delete, search records)
3. **Specialized Tools**: Discord-specific table creation and analytics

## Important Implementation Details

- Uses `xc-token` header for NocoDB authentication (not `xc-auth`)
- FastAPI server with async/await for better performance
- Client wrapper handles environment variable injection for Cursor IDE integration
- Docker configuration includes health checks and graceful shutdown
- All API responses follow standardized MCP format with `success` boolean and structured data

## Testing & Validation

The server includes comprehensive health checks:
- Basic health endpoint at `/health`
- Tool listing at `/tools` (requires authentication)
- Tool execution at `/call` (requires authentication)
- Docker health checks with proper timeout handling