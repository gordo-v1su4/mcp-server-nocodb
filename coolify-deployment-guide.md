# 🚀 Coolify Deployment Guide for NocoDB MCP Server

## 📋 Prerequisites

- **Coolify instance** running and accessible
- **GitHub repository** connected to Coolify
- **Domain name** (mcp.v1su4.com) pointed to your server
- **NocoDB API token** from your NocoDB instance

## 🎯 Best Practice Deployment Strategy

### Approach: Production-Ready with Monitoring

## Step 1: Connect GitHub Repository

1. **In Coolify Dashboard** → **Projects** → **Create Project**
2. **Project Name**: `mcp-server`
3. **Connect GitHub**: Link your `gordo-v1su4/mcp-server` repository
4. **Branch**: `main` (or your default branch)

## Step 2: Create Production Service

### Service Configuration:
- **Service Type**: Docker Compose
- **Source**: Git Repository
- **Repository URL**: `https://github.com/gordo-v1su4/mcp-server.git`
- **Branch**: `main`

### Environment Variables:
```bash
# Required Variables
NOCODB_API_TOKEN=your_nocodb_api_token_here
NOCODB_URL=https://nocodb.v1su4.com
PORT=3001
NODE_ENV=production

# Optional Variables
LOG_LEVEL=info
CORS_ORIGIN=*
RATE_LIMIT_WINDOW=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### Resource Allocation:
- **CPU**: 0.5-1 vCPU
- **Memory**: 512MB-1GB
- **Storage**: 1GB

## Step 3: Domain & Network Configuration

### Domain Setup:
1. **Add Domain**: `mcp.v1su4.com`
2. **SSL**: Enable (Coolify will handle Let's Encrypt)
3. **Port**: Map external port to container port 3001

### Network Settings:
- **Exposed Ports**: 3001
- **Internal Port**: 3001
- **Protocol**: HTTP/HTTPS

## Step 4: Health Checks & Monitoring

### Health Check Configuration:
```yaml
# In Coolify service settings
Health Check:
  Type: HTTP
  Endpoint: /health
  Method: GET
  Interval: 30s
  Timeout: 10s
  Retries: 3
  Start Period: 60s
```

### Monitoring:
- **Enable Logs**: View real-time application logs
- **Enable Metrics**: CPU, Memory, Network usage
- **Enable Notifications**: Get alerts on failures

## Step 5: Build Settings

### Build Configuration:
```yaml
# Dockerfile is already configured
Build Context: .
Dockerfile Path: Dockerfile

# Build Arguments (if needed):
NODE_ENV=production
```

### Environment:
- **Build Environment**: Node.js 18
- **Working Directory**: /app

## Step 6: Deploy & Test

### Initial Deployment:
1. **Deploy**: Click deploy in Coolify
2. **Monitor**: Watch logs for successful startup
3. **Test Health**: `curl https://mcp.v1su4.com/health`

### Test Endpoints:
```bash
# Test health
curl https://mcp.v1su4.com/health

# Test tools
curl https://mcp.v1su4.com/tools

# Test connection (with your token)
curl -X POST https://mcp.v1su4.com/call \
  -H "Content-Type: application/json" \
  -d '{"name": "nocodb_test_connection", "arguments": {"api_token": "your_token"}}'
```

## 🔧 Advanced Configuration

### Custom Docker Compose (Optional):
If you need custom services, Coolify supports docker-compose.yml:

```yaml
version: '3.8'
services:
  mcp-server:
    build: .
    ports:
      - "3001:3001"
    environment:
      - NOCODB_API_TOKEN=${NOCODB_API_TOKEN}
      - NOCODB_URL=https://nocodb.v1su4.com
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

### Environment-Specific Deployments:
Create multiple services for different environments:
- **Production**: `mcp-server-prod`
- **Staging**: `mcp-server-staging`
- **Development**: `mcp-server-dev`

### Backup & Recovery:
- **Enable Backups**: Daily database backups
- **Persistent Storage**: For logs and temporary files
- **Rollback**: Easy rollback to previous versions

## 🚨 Troubleshooting Common Issues

### 1. Deployment Fails
```bash
# Check build logs in Coolify
# Verify Dockerfile syntax
docker build -t test-build .

# Check environment variables
echo $NOCODB_API_TOKEN
```

### 2. Health Check Fails
```bash
# Test locally first
docker run -p 3001:3001 -e NOCODB_API_TOKEN=your_token mcp-server

# Check logs
docker logs <container_id>

# Test health endpoint
curl http://localhost:3001/health
```

### 3. SSL/HTTPS Issues
```bash
# Coolify handles SSL automatically
# Check domain DNS settings
nslookup mcp.v1su4.com

# Force SSL redirect in Coolify settings
```

### 4. Performance Issues
```bash
# Monitor resource usage
# Increase CPU/Memory allocation
# Check rate limiting settings
# Optimize Node.js for production
```

## 📊 Monitoring & Analytics

### Built-in Monitoring:
- **Application Logs**: Real-time log streaming
- **Performance Metrics**: CPU, Memory, Network
- **Health Status**: Automated health checks
- **Uptime Monitoring**: Service availability

### Custom Monitoring:
Add these to your MCP server for enhanced monitoring:
```javascript
// Prometheus metrics (optional)
const prometheus = require('prom-client');
const collectDefaultMetrics = prometheus.collectDefaultMetrics;
collectDefaultMetrics();
```

## 🔒 Security Best Practices

### 1. Environment Variables:
- Store secrets securely
- Use Coolify's built-in secret management
- Rotate tokens regularly

### 2. Network Security:
- Enable firewall rules
- Use HTTPS only
- Rate limiting configured

### 3. Access Control:
- IP whitelisting (if needed)
- API key validation
- Request logging

## 📈 Scaling & Optimization

### Horizontal Scaling:
- Deploy multiple instances behind load balancer
- Use Coolify's built-in load balancing
- Monitor performance metrics

### Performance Optimization:
```javascript
// In server.js, add these optimizations:
const compression = require('compression');
app.use(compression());

const helmet = require('helmet');
app.use(helmet());
```

## 🎯 Success Indicators

### ✅ Deployment Successful:
- Health check passes: `200 OK`
- Tools endpoint works: Returns JSON array
- SSL certificate active
- Logs show clean startup
- No error messages in logs

### ✅ Integration Working:
- Cursor can connect to MCP server
- NocoDB tools appear in Cursor
- API calls work without errors
- Rate limiting not triggered

## 🚀 Next Steps After Deployment:

1. **Test Cursor Integration**:
   ```bash
   # Set environment variable
   export NOCODB_API_TOKEN="your_token"
   ```

2. **Restart Cursor** to load MCP tools

3. **Test Tools**:
   - `nocodb_test_connection`
   - `nocodb_list_projects`
   - `nocodb_get_analytics`

4. **Monitor Usage** via Coolify dashboard

Your MCP server will be production-ready and automatically deploy on every GitHub push! 🎉
