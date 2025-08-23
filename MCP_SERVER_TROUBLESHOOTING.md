# 🔧 MCP Server Troubleshooting Guide

## Current Issue: "no available server"

The MCP server is running but responding with "no available server". Here's how to fix it:

## 🧪 Quick Diagnostic Tests

### 1. Test Health Endpoint
```bash
curl -k https://mcp.v1su4.com/health
# Should return: {"status": "healthy", ...}
```

### 2. Test Tools Endpoint
```bash
curl -k https://mcp.v1su4.com/tools
# Should return JSON with tools list
```

### 3. Test Tool Call
```bash
curl -k -X POST https://mcp.v1su4.com/call \
  -H "Content-Type: application/json" \
  -d '{"name": "nocodb_test_connection", "arguments": {"api_token": "test"}}'
```

## 🚨 Common Issues & Solutions

### Issue 1: Environment Variables Not Set
**Symptoms:** Server starts but returns "no available server"

**Solution:**
1. Go to your Coolify dashboard
2. Find your MCP server service
3. Add environment variables:
   ```
   NOCODB_API_TOKEN=your_actual_token_here
   NOCODB_URL=https://nocodb.v1su4.com
   PORT=3001
   PYTHONPATH=/app
   ```
4. Restart the service

### Issue 2: SSL Certificate Problems
**Symptoms:** curl fails with SSL errors

**Current Fix:** MCP config uses `-k` flag to skip SSL verification
**Permanent Fix:** Wait for SSL certificate to be issued (usually 5-10 minutes)

### Issue 3: Port Configuration
**Symptoms:** Server responds but on wrong port

**Check:**
```bash
# Test different ports
curl -k https://mcp.v1su4.com:3000/health
curl -k https://mcp.v1su4.com:8000/health
```

### Issue 4: Service Not Running
**Symptoms:** Connection timeout

**Check:**
1. Coolify dashboard → Service status
2. View service logs in Coolify
3. Check if Docker container is running

## 🔧 Quick Fix Commands

### If Environment Variables Are Missing:
```bash
# SSH into your server and check environment
docker exec -it <container_name> env

# Or check Coolify service configuration
```

### If Service Needs Restart:
```bash
# In Coolify: Force rebuild
# Or trigger new deployment
```

### If Logs Show Python Errors:
```bash
# Check Coolify logs for:
# - Import errors
# - Missing dependencies
# - Port binding issues
```

## 📊 Expected Server Response

### Health Check (Success):
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "version": "1.0.0",
  "nocodb_connected": true
}
```

### Tools List (Success):
```json
{
  "name": "nocodb-mcp-tools",
  "tools": [
    {
      "name": "nocodb_test_connection",
      "description": "Test connection to NocoDB instance"
    }
    // ... more tools
  ]
}
```

### Tool Call (Success):
```json
{
  "success": true,
  "result": { /* tool result */ }
}
```

## 🎯 Next Steps

1. **Check Coolify Environment Variables** - Make sure `NOCODB_API_TOKEN` is set
2. **Verify SSL Certificate** - Wait a few minutes for Let's Encrypt
3. **Test Endpoints** - Use the curl commands above
4. **Check Logs** - Look for Python errors in Coolify
5. **Restart Service** - If needed, trigger a rebuild

## 🆘 If Still Not Working

1. **Check Coolify Service Status**
2. **View Application Logs** in Coolify
3. **Verify Docker Image** is building correctly
4. **Test Locally** with docker-compose if possible

## 📞 Support

The server configuration is correct. The issue is likely:
- Missing environment variables
- SSL certificate still being issued
- Service not properly restarted after config changes

Once the environment variables are set and SSL is ready, the MCP server should work perfectly with Cursor! 🚀
