# MCP Server NocoDB - Deployment Guide

## Quick Start

Your NocoDB MCP Server is ready for deployment! It's a single-file FastAPI application that works perfectly with Claude.

### Current Status
✅ **Server Running**: http://localhost:3001  
✅ **Docker Ready**: Dockerfile configured  
✅ **Coolify Ready**: docker-compose.yaml configured  

## Local Testing

```bash
# 1. Set environment variables
export NOCODB_URL="https://your-nocodb.com"
export NOCODB_API_TOKEN="your_api_token"

# 2. Run locally
python nocodb_mcp_server.py
```

## Docker Deployment

### Build and Test Locally
```bash
# Build the image
docker build -t mcp-server-nocodb:1.1.0 .

# Test run
docker run -p 3001:3001 \
  -e NOCODB_URL="https://your-nocodb.com" \
  -e NOCODB_API_TOKEN="your_token" \
  mcp-server-nocodb:1.1.0
```

### Using Docker Compose
```bash
# Create .env file
cat > .env << EOF
NOCODB_URL=https://your-nocodb.com
NOCODB_API_TOKEN=your_api_token
EOF

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f mcp-server-nocodb

# Stop the service
docker-compose down
```

## Coolify Deployment

### Method 1: Git Repository
1. **Import Repository**: Add your Git repository to Coolify
2. **Set Environment Variables**:
   - `NOCODB_URL`: Your NocoDB instance URL
   - `NOCODB_API_TOKEN`: Your NocoDB API token
3. **Deploy**: Coolify will build and deploy automatically

### Method 2: Docker Image
1. **Build & Push** (optional):
   ```bash
   docker build -t your-registry/mcp-server-nocodb:1.1.0 .
   docker push your-registry/mcp-server-nocodb:1.1.0
   ```
2. **Deploy in Coolify**: Use the docker-compose.yaml or specify the image directly

### Environment Variables for Coolify
```
NOCODB_URL=https://your-nocodb-instance.com
NOCODB_API_TOKEN=your_nocodb_api_token
PORT=3001
```

## Health Check

The server includes health checks:
- **Endpoint**: `GET /` or `POST /` (MCP protocol)
- **Health Check**: Returns server status and NocoDB connection info
- **Docker Health**: Automated health checks every 30s

## Available MCP Tools

Your server provides these tools for Claude:

### Connection & Management
- `health_check()` - Check server and NocoDB status
- `nocodb_test_connection()` - Test connection and list projects  
- `nocodb_list_projects()` - List all projects
- `nocodb_list_tables(project_id)` - List tables in project

### Data Operations  
- `nocodb_get_records(project_id, table_id, limit, offset)` - Get records
- `nocodb_create_record(project_id, table_id, record_data)` - Create record
- `nocodb_update_record(project_id, table_id, record_id, record_data)` - Update record
- `nocodb_delete_record(project_id, table_id, record_id)` - Delete record
- `nocodb_search_records(project_id, table_id, filters)` - Search with filters

### Specialized Tools
- `nocodb_create_discord_reactions_table(project_id)` - Create Discord reactions table
- `nocodb_get_analytics(project_id, table_id)` - Get Discord analytics

## Troubleshooting

### Port Issues
- Default port: 3001
- Change with `PORT` environment variable
- Ensure port is not in use: `netstat -tulpn | grep :3001`

### Connection Issues
- Verify `NOCODB_URL` is accessible
- Check `NOCODB_API_TOKEN` is valid
- Test with: `curl -H "xc-token: YOUR_TOKEN" https://your-nocodb.com/api/v1/db/meta/projects`

### Docker Issues
- Build logs: `docker build --progress=plain .`
- Container logs: `docker logs container_name`
- Interactive shell: `docker run -it --entrypoint /bin/bash mcp-server-nocodb:1.1.0`

## Version Info
- **Project**: mcp-server-nocodb
- **Version**: 1.1.0
- **Python**: 3.12
- **FastMCP**: Latest
- **Architecture**: Single-file, lightweight