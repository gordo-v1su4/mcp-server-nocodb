# 🚀 NocoDB MCP Server

A production-ready Model Context Protocol (MCP) server for seamless NocoDB integration with Cursor IDE.

## 🎯 What This Is

This MCP server provides Cursor IDE users with direct access to NocoDB operations without leaving their development environment. Perfect for Discord Heart Reactions workflow and other NocoDB automation projects.

## ✨ Features

- **Complete NocoDB API Integration** - All CRUD operations supported
- **Discord Heart Reactions Optimized** - Built specifically for the Discord workflow
- **Production Ready** - Health checks, rate limiting, graceful shutdown
- **Docker Ready** - Easy deployment with Docker or Coolify
- **Auto-deployment** - GitHub Actions for automated builds
- **Comprehensive Monitoring** - Built-in health checks and metrics

## 🚀 Quick Deployment

### Option 1: Coolify (Recommended)
1. Connect your GitHub repo to Coolify
2. Set environment variables:
   - `NOCODB_API_TOKEN=your_token`
   - `NOCODB_URL=https://nocodb.v1su4.com`
3. Deploy and enjoy!

### Option 2: Docker
```bash
docker build -t mcp-server .
docker run -p 3001:3001 -e NOCODB_API_TOKEN=your_token mcp-server
```

### Option 3: Docker Compose
```bash
docker-compose up -d
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

## 📋 Cursor IDE Integration

1. **Update MCP Configuration**:
   ```json
   {
     "mcpServers": {
       "nocodb": {
         "command": "node",
         "args": ["/Users/your-username/Documents/Github/mcp-server/mcp-client-wrapper.js"],
         "env": {
           "MCP_SERVER_URL": "https://mcp.v1su4.com",
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

3. **Restart Cursor** and enjoy NocoDB tools!

## 🏗️ Architecture

```
Cursor IDE → Local MCP Wrapper → Hosted MCP Server → NocoDB API
```

- **Local Wrapper**: Handles Cursor integration and communication
- **Hosted Server**: Production server with all NocoDB operations
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
