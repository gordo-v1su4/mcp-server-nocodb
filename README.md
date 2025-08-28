# NocoDB MCP Server

A standard FastMCP Model Context Protocol server for seamless NocoDB integration with Claude Code.

## 🎯 What This Is

This MCP server provides Claude Code users with direct access to NocoDB operations. Built using the standard FastMCP library with streamable-http transport for remote hosting. Perfect for Discord Heart Reactions workflow and other NocoDB automation projects.

## ✨ Features

- **Complete NocoDB API Integration** - All CRUD operations supported
- **Discord Heart Reactions Optimized** - Built specifically for the Discord workflow
- **Production Ready** - Health checks, rate limiting, graceful shutdown
- **Docker Ready** - Easy deployment with Docker or Coolify
- **Auto-deployment** - GitHub Actions for automated builds
- **Comprehensive Monitoring** - Built-in health checks and metrics

## 🚀 Quick Deployment

### Option 1: Coolify (Recommended)
1. **Create New Resource** → Docker Image
2. **Image**: `gordo-v1su4/nocodb-mcp-server:latest`
3. **Port**: `3001`
4. **Environment Variables**:
   - `NOCODB_API_TOKEN=your_token`
   - `NOCODB_URL=https://nocodb.v1su4.com`
   - `PORT=3001`
5. **Health Check**: `/health` endpoint
6. Deploy and enjoy!

### Option 2: Docker
```bash
# Use pre-built image
docker run -p 3001:3001 \
  -e NOCODB_API_TOKEN=your_token \
  -e NOCODB_URL=https://nocodb.v1su4.com \
  gordo-v1su4/nocodb-mcp-server:latest

# Or build locally
bun run docker-build
bun run docker-run
```

### Option 3: Docker Compose
```bash
# Standard deployment
bun run compose-up

# With monitoring (Prometheus/Loki)
docker-compose --profile monitoring up -d
```

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NOCODB_API_TOKEN` | Yes | - | Your NocoDB API token |
| `NOCODB_URL` | No | `https://nocodb.v1su4.com` | NocoDB instance URL |
| `PORT` | No | `3001` | Server port |
| `NODE_ENV` | No | `production` | Environment |
| `LOG_LEVEL` | No | `info` | Logging level |

## 📊 Available MCP Tools

### Connection & Management
- `nocodb_test_connection` - Test NocoDB connection
- `nocodb_list_projects` - List all projects
- `nocodb_list_tables` - List tables in project

### Data Operations
- `nocodb_get_records` - Retrieve records with pagination
- `nocodb_create_record` - Create new records
- `nocodb_update_record` - Update existing records
- `nocodb_delete_record` - Delete records
- `nocodb_search_records` - Search with filters

### Specialized Tools
- `nocodb_create_discord_reactions_table` - Create Discord reactions table
- `nocodb_get_analytics` - Get Discord reactions analytics

## 🧪 Testing

### Health Check
```bash
curl https://mcp.v1su4.com/health
```

### Tools List
```bash
curl https://mcp.v1su4.com/tools
```

### Test Tool Call
```bash
curl -X POST https://mcp.v1su4.com/call \
  -H "Content-Type: application/json" \
  -d '{"name": "nocodb_test_connection", "arguments": {"api_token": "your_token"}}'
```

## 📋 Claude Code Integration

1. **Update MCP Configuration**:
   ```json
   {
     "mcpServers": {
       "nocodb": {
         "command": "node",
         "args": ["-e", "console.log(JSON.stringify({method:'GET',url:'https://mcp.v1su4.com'}))"],
         "env": {
           "NOCODB_API_TOKEN": "${NOCODB_API_TOKEN}"
         }
       }
     }
   }
   ```

2. **Set Environment Variable**:
   ```bash
   export NOCODB_API_TOKEN="your_nocodb_api_token"
   ```

3. **Restart Claude Code** and enjoy NocoDB tools!

### Option 2: Claude CLI (Recommended for newer versions)

1. **Add your MCP server**:
   ```bash
   claude mcp add --transport http nocodb https://mcp-nocodb-v1su4.com
   ```

2. **Manage existing connections**:
   ```bash
   # List all connected servers
   claude mcp list
   
   # Remove old connections (if needed)
   claude mcp remove server-name
   ```

3. **Test the connection**:
   ```bash
   claude mcp test nocodb
   ```

## 🏗️ Architecture

```
Claude Code → Hosted FastMCP Server (SSE) → NocoDB API
```

- **FastMCP Server**: Standard MCP server with streamable-http transport
- **Server-Sent Events**: Real-time communication via SSE protocol
- **NocoDB API**: Your actual database instance

## 📚 Documentation

- **[Coolify Deployment Guide](coolify-deployment-guide.md)** - Detailed deployment instructions
- **[API Reference](nocodb-mcp-tools.json)** - All available tools and schemas
- **[Docker Configuration](Dockerfile)** - Container setup details

## 🔒 Security

- Rate limiting to prevent abuse
- API token authentication required
- HTTPS enforced
- Comprehensive logging
- Environment variable configuration

## 📈 Monitoring

- Real-time health checks
- Performance metrics
- Request logging
- Error tracking
- Resource usage monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use and modify as needed.

## 🆘 Support

For issues or questions:
1. Check the health endpoint
2. Review server logs
3. Test with the CLI tools
4. Check environment variables

---

**Built for Discord Heart Reactions workflow** 🎉
