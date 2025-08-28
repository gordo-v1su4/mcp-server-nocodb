# Docker Hub Deployment & Claude Code Connection

## Step 1: Build and Push to Docker Hub

```bash
# 1. Build the image with proper tagging
docker build -t gordov1su4/mcp-server-nocodb:1.1.0 .
docker build -t gordov1su4/mcp-server-nocodb:latest .

# 2. Login to Docker Hub
docker login

# 3. Push to Docker Hub
docker push gordov1su4/mcp-server-nocodb:1.1.0
docker push gordov1su4/mcp-server-nocodb:latest
```

## Step 2: Connect to Claude Code

### Method 1: Streamable HTTP (Recommended)

This is the easiest method since your server uses streamable HTTP transport:

**Claude MCP Config**: `%APPDATA%\Claude\mcp_servers.json` (Windows)

```json
{
  "mcpServers": {
    "nocodb": {
      "transport": {
        "type": "streamable-http",
        "url": "http://your-server-domain:3001/"
      }
    }
  }
}
```

### Method 2: Local Docker Launch

For running locally with Docker:

```json
{
  "mcpServers": {
    "nocodb": {
      "command": "docker",
      "args": [
        "run", "--rm", "-p", "3001:3001",
        "-e", "NOCODB_URL=https://your-nocodb.com",
        "-e", "NOCODB_API_TOKEN=your_token",
        "gordov1su4/mcp-server-nocodb:1.1.0"
      ],
      "env": {
        "NOCODB_URL": "https://your-nocodb.com",
        "NOCODB_API_TOKEN": "your_nocodb_api_token"
      }
    }
  }
}
```

### Method 3: Direct Python (if you have the file locally)

```json
{
  "mcpServers": {
    "nocodb": {
      "command": "python",
      "args": ["nocodb_mcp_server.py"],
      "cwd": "/path/to/your/server",
      "env": {
        "NOCODB_URL": "https://your-nocodb.com",
        "NOCODB_API_TOKEN": "your_nocodb_api_token"
      }
    }
  }
}
```

## Step 3: Coolify Deployment

In Coolify:

1. **Service Type**: Docker Image
2. **Image**: `gordov1su4/mcp-server-nocodb:1.1.0`
3. **Port**: `3001`
4. **Domain**: Set up your domain (e.g., `nocodb-mcp.yourdomain.com`)
5. **Environment Variables**:
   ```
   NOCODB_URL=https://your-nocodb.com
   NOCODB_API_TOKEN=your_nocodb_api_token
   PORT=3001
   ```

## Step 4: Quick Test Commands

```bash
# Build and push to Docker Hub
docker build -t gordov1su4/mcp-server-nocodb:1.1.0 .
docker push gordov1su4/mcp-server-nocodb:1.1.0

# Test locally
docker run -p 3001:3001 \
  -e NOCODB_URL="https://your-nocodb.com" \
  -e NOCODB_API_TOKEN="your_token" \
  gordov1su4/mcp-server-nocodb:1.1.0

# Test connection
curl http://localhost:3001/

# Deploy with docker-compose (see docker-compose.yaml)
docker-compose up -d
```

## Available Tools for Claude

Once connected, Claude will have access to:
- `health_check()` - Server status
- `nocodb_test_connection()` - Test NocoDB connection
- `nocodb_list_projects()` - List all projects  
- `nocodb_list_tables(project_id)` - List tables
- `nocodb_get_records()` - Get table records
- `nocodb_create_record()` - Create new records
- `nocodb_update_record()` - Update existing records
- `nocodb_delete_record()` - Delete records
- `nocodb_search_records()` - Search with filters
- `nocodb_create_discord_reactions_table()` - Create Discord table
- `nocodb_get_analytics()` - Get Discord analytics

## Troubleshooting

- **Claude Config Location**:
  - Windows: `%APPDATA%\Claude\mcp_servers.json`
  - Mac: `~/Library/Application Support/Claude/mcp_servers.json`
  - Linux: `~/.config/Claude/mcp_servers.json`

- **Test server response**:
  ```bash
  curl -X POST http://your-server:3001/ \
    -H "Content-Type: application/json" \
    -d '{"method": "tools/list", "params": {}}'
  ```

Your NocoDB MCP Server is ready for production! 🚀