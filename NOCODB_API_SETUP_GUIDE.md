# 🔑 NocoDB API Setup Guide - Home Server Instance

## 📋 Complete Setup for Self-Hosted NocoDB with MCP Integration

### **🎯 Purpose:**
This guide documents the **correct API authentication setup** for NocoDB instances running on home servers, specifically optimized for the Discord Heart Reactions MCP workflow.

---

## 🏠 Home Server NocoDB Configuration

### **✅ Verified Working Setup:**

#### **1. Instance Details:**
- **URL**: `https://nocodb.v1su4.com`
- **Type**: Self-hosted PostgreSQL instance
- **Status**: ✅ Active and operational

#### **2. Authentication Method:**
```bash
# ❌ INCORRECT (Common mistake)
curl -H "xc-auth: token_here" https://nocodb.v1su4.com/api/v1/db/meta/projects

# ❌ INCORRECT (Another common mistake)
curl -H "Authorization: Bearer token_here" https://nocodb.v1su4.com/api/v1/db/meta/projects

# ✅ CORRECT (As per NocoDB API documentation)
curl -H "xc-token: token_here" https://nocodb.v1su4.com/api/v1/db/meta/projects
```

#### **3. Token Generation:**
1. Login to NocoDB: `nocodb.v1su4.com`
2. Navigate: **Account Settings** → **Tokens**
3. Click: **Generate New Token**
4. **Copy the exact token** (format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`)

---

## 🔧 MCP Server Integration

### **✅ Working MCP Configuration:**

#### **1. Server Architecture:**
```
Cursor IDE → MCP Client Wrapper → https://mcp.v1su4.com (FastAPI) → https://nocodb.v1su4.com
```

#### **2. Environment Variables:**
```bash
# Required for MCP Server (in Coolify)
MCP_API_KEY=E4C05E7E-913B4FAA-044D58EE-44ABDD51
NOCODB_API_TOKEN=your_nocodb_token_here
NOCODB_URL=https://nocodb.v1su4.com
PORT=3001
PYTHONPATH=/app
```

#### **3. Cursor MCP Configuration:**
```json
{
  "mcpServers": {
    "nocodb": {
      "command": "curl",
      "args": [
        "-k",
        "-X", "POST",
        "https://mcp.v1su4.com/call",
        "-H", "Content-Type: application/json",
        "-H", "Authorization: Bearer ${MCP_API_KEY}",
        "-d", "@-"
      ],
      "env": {
        "MCP_API_KEY": "${MCP_API_KEY}",
        "NOCODB_API_TOKEN": "${NOCODB_API_TOKEN}"
      },
      "timeout": 30000
    }
  }
}
```

---

## 🧪 Testing & Validation

### **✅ Token Testing Script:**
```bash
# Download and run the validation script
curl -s https://raw.githubusercontent.com/gordo-v1su4/mcp-server/main/test-nocodb-token.sh > test-token.sh
chmod +x test-token.sh
./test-token.sh YOUR_TOKEN_HERE
```

**Expected Output:**
```bash
🔍 Testing token: eyJhbGciOiJIUzI1NiI...
✅ Token is VALID!
Projects: {"list":[...]}
🎉 Your token is working correctly!
```

### **✅ MCP Server Testing:**
```bash
# Test health endpoint
curl -k https://mcp.v1su4.com/health

# Test tools endpoint
curl -k -H "Authorization: Bearer E4C05E7E-913B4FAA-044D58EE-44ABDD51" https://mcp.v1su4.com/tools

# Test MCP operation
curl -k -X POST https://mcp.v1su4.com/call \
  -H "Authorization: Bearer E4C05E7E-913B4FAA-044D58EE-44ABDD51" \
  -H "Content-Type: application/json" \
  -d '{"name": "nocodb_test_connection", "arguments": {}}'
```

---

## 🚨 Common Issues & Solutions

### **Issue 1: 401 Unauthorized**
**Symptoms:** `{"error":"AUTHENTICATION_REQUIRED","message":"Authentication required - Invalid token"}`

**Solutions:**
1. ✅ **Check header name**: Use `xc-token`, not `xc-auth`
2. ✅ **Verify token format**: Should be JWT-like string starting with `eyJ`
3. ✅ **Test token directly**: Use the validation script above
4. ✅ **Check token expiration**: Generate new token if expired

### **Issue 2: SSL Certificate Errors**
**Symptoms:** `curl: (60) SSL certificate problem`

**Solutions:**
1. ✅ **Use `-k` flag**: `curl -k` to bypass SSL verification during development
2. ✅ **Check SSL certificate**: Ensure Let's Encrypt is properly configured
3. ✅ **Update curl**: `curl --version` should show recent version

### **Issue 3: Connection Refused**
**Symptoms:** `Failed to connect to nocodb.v1su4.com port 443`

**Solutions:**
1. ✅ **Check server status**: Ensure NocoDB instance is running
2. ✅ **Verify URL**: Confirm `https://nocodb.v1su4.com` is accessible
3. ✅ **Check firewall**: Ensure port 443 is open
4. ✅ **DNS resolution**: `nslookup nocodb.v1su4.com`

---

## 📊 Available MCP Tools

### **Connection & Management:**
- `nocodb_test_connection` - Verify database connectivity
- `nocodb_list_projects` - Browse available projects
- `nocodb_list_tables` - View tables in a project

### **Data Operations:**
- `nocodb_get_records` - Retrieve records with pagination
- `nocodb_create_record` - Add new records
- `nocodb_update_record` - Modify existing records
- `nocodb_delete_record` - Remove records
- `nocodb_search_records` - Search with filters

### **Specialized:**
- `nocodb_create_discord_reactions_table` - Create Discord reactions table
- `nocodb_get_analytics` - Get Discord reactions analytics

---

## 🏗️ Deployment Architecture

### **Production Setup (Coolify):**
```yaml
# docker-compose.yaml
services:
  nocodb-mcp-server:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - NOCODB_API_TOKEN=${NOCODB_API_TOKEN}
      - MCP_API_KEY=${MCP_API_KEY}
      - NOCODB_URL=https://nocodb.v1su4.com
    ports:
      - "3001:3001"
```

### **Development Setup:**
```bash
# Local testing
npm run compose-up
npm run compose-logs
npm run compose-test
```

---

## 🔒 Security Best Practices

### **1. API Key Management:**
- ✅ **Store securely**: Never commit to GitHub
- ✅ **Use environment variables**: No hardcoded values
- ✅ **Rotate regularly**: Change tokens every 3-6 months
- ✅ **Different keys**: Separate MCP and NocoDB tokens

### **2. Network Security:**
- ✅ **HTTPS only**: Enforce SSL/TLS encryption
- ✅ **Rate limiting**: Implement request limits
- ✅ **Input validation**: Sanitize all user inputs
- ✅ **Logging**: Monitor all API requests

### **3. Authentication:**
- ✅ **Bearer tokens**: Use JWT for MCP server auth
- ✅ **xc-token header**: Use correct NocoDB API format
- ✅ **Token validation**: Verify tokens on every request
- ✅ **Expiration handling**: Implement token refresh logic

---

## 📚 API Reference

### **NocoDB API Endpoints:**
```bash
# Projects
GET /api/v1/db/meta/projects

# Tables
GET /api/v1/db/meta/projects/{project_id}/tables

# Records
GET /api/v1/db/data/noco/{project_id}/{table_id}
POST /api/v1/db/data/noco/{project_id}/{table_id}
PATCH /api/v1/db/data/noco/{project_id}/{table_id}/{record_id}
DELETE /api/v1/db/data/noco/{project_id}/{table_id}/{record_id}
```

### **MCP Server Endpoints:**
```bash
# Health check
GET /health

# Available tools
GET /tools (requires MCP_API_KEY)

# Execute tools
POST /call (requires MCP_API_KEY)
```

---

## 🎯 Use Cases

### **Discord Heart Reactions Workflow:**
```json
{
  "name": "nocodb_create_record",
  "arguments": {
    "project_id": "pce7ccvwdlz09bx",
    "table_id": "your_table_id",
    "record_data": {
      "message_content": "Discord message content",
      "discord_message_id": "msg_123",
      "discord_channel_id": "channel_456",
      "timestamp": "2024-01-01T00:00:00Z"
    }
  }
}
```

### **Analytics Query:**
```json
{
  "name": "nocodb_get_analytics",
  "arguments": {
    "project_id": "pce7ccvwdlz09bx",
    "table_id": "your_table_id"
  }
}
```

---

## 🚀 Quick Start

1. **Generate NocoDB token**: `nocodb.v1su4.com` → Account Settings → Tokens
2. **Test token**: `./test-nocodb-token.sh YOUR_TOKEN`
3. **Set environment variables**: `MCP_API_KEY` and `NOCODB_API_TOKEN`
4. **Update Cursor config**: Add MCP server configuration
5. **Test connection**: Use MCP tools in Cursor

---

## 📞 Support

**For NocoDB API issues:**
- Check: `nocodb.v1su4.com/api/v2/meta/bases/pce7ccvwdlz09bx/swagger`
- Use: `xc-token` header (not `xc-auth`)
- Test with: `./test-nocodb-token.sh`

**For MCP server issues:**
- Health: `curl -k https://mcp.v1su4.com/health`
- Tools: `curl -k -H "Authorization: Bearer ${MCP_API_KEY}" https://mcp.v1su4.com/tools`
- Logs: Check Coolify service logs

**This setup is optimized for home-ran NocoDB instances and provides robust API integration with Cursor IDE!** 🎉
