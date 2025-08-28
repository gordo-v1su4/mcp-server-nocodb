# Coolify Deployment Guide - NocoDB MCP Server

Your NocoDB MCP Server is ready to deploy alongside your existing NocoDB instance!

## 🏗️ **Your Setup**
- **NocoDB Instance**: https://nocodb.v1su4.com (running in Coolify)
- **MCP Server**: `gordov1su4/mcp-server-nocodb:1.1.0` (ready to deploy)
- **Network**: Both containers can communicate within Coolify

## 🚀 **Deploy in Coolify**

### Method 1: Docker Image Deployment
1. **Create New Resource** → **Docker Image**
2. **Image**: `gordov1su4/mcp-server-nocodb:1.1.0`
3. **Port**: `3001`
4. **Environment Variables**:
   ```
   NOCODB_URL=https://nocodb.v1su4.com
   NOCODB_API_TOKEN=your_nocodb_api_token
   PORT=3001
   ```
5. **Domain**: Set up domain (e.g., `mcp-nocodb.v1su4.com`)

### Method 2: Git Repository Deployment
1. **Create New Resource** → **Git Repository**
2. **Repository**: Your GitHub repo
3. **Build Pack**: Docker
4. **Environment Variables**: Same as above
5. **Deploy**: Coolify will build from your Dockerfile

## 🔧 **Environment Variables**
```bash
NOCODB_URL=https://nocodb.v1su4.com
NOCODB_API_TOKEN=your_api_token_here
PORT=3001
```

## 🌐 **Connect to Claude Code**

Once deployed, use your MCP server domain:

```json
{
  "mcpServers": {
    "nocodb": {
      "transport": {
        "type": "streamable-http",
        "url": "https://mcp-nocodb.v1su4.com/"
      }
    }
  }
}
```

## 📋 **Quick Test Commands**

```bash
# Test your deployed server
curl https://mcp-nocodb.v1su4.com/

# Test locally first
docker run -p 3001:3001 \
  -e NOCODB_URL="https://nocodb.v1su4.com" \
  -e NOCODB_API_TOKEN="your_token" \
  gordov1su4/mcp-server-nocodb:1.1.0

# Test with docker-compose
docker-compose up -d
```

## 🔍 **Available Tools**

Once connected to Claude, you'll have:
- `nocodb_test_connection()` - Test connection to nocodb.v1su4.com
- `nocodb_list_projects()` - List your NocoDB projects
- `nocodb_create_discord_reactions_table()` - Create Discord tables
- All CRUD operations on your NocoDB data

## ✅ **Network Configuration**

Since both containers run in Coolify:
- ✅ **HTTPS**: Both use SSL certificates
- ✅ **Domain Resolution**: Public domains work perfectly
- ✅ **Security**: API tokens handle authentication
- ✅ **Performance**: Direct connection between services

Your MCP server will connect to your NocoDB instance at `nocodb.v1su4.com` and provide all tools to Claude Code! 🚀