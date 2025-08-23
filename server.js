#!/usr/bin/env node

/**
 * Production NocoDB MCP Server
 * Hosted version for Cursor IDE integration
 * Runs on port 3001 with proper production settings
 */

const NocoDBClient = require('./nocodb-mcp-client.js');
const http = require('http');
const url = require('url');

class ProductionMCPServer {
  constructor(port = 3001) {
    this.port = port;
    this.client = null;
    this.server = null;
    this.isShuttingDown = false;
  }

  /**
   * Start the production server
   */
  async start() {
    console.log('🚀 Starting NocoDB MCP Server...');

    // Initialize HTTP server
    this.server = http.createServer(this.handleRequest.bind(this));

    // Graceful shutdown
    process.on('SIGINT', this.gracefulShutdown.bind(this));
    process.on('SIGTERM', this.gracefulShutdown.bind(this));

    // Handle uncaught exceptions
    process.on('uncaughtException', (err) => {
      console.error('❌ Uncaught Exception:', err);
      this.gracefulShutdown();
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('❌ Unhandled Rejection at:', promise, 'reason:', reason);
    });

    // Start listening
    return new Promise((resolve, reject) => {
      this.server.listen(this.port, () => {
        console.log(`✅ NocoDB MCP Server running on port ${this.port}`);
        console.log(`📋 Tools endpoint: http://localhost:${this.port}/tools`);
        console.log(`🔗 Health check: http://localhost:${this.port}/health`);
        console.log(`🌐 Ready for Cursor IDE integration`);
        resolve();
      });

      this.server.on('error', (err) => {
        console.error('❌ Server error:', err);
        reject(err);
      });
    });
  }

  /**
   * Handle HTTP requests
   */
  async handleRequest(req, res) {
    const parsedUrl = url.parse(req.url, true);
    const { pathname, query } = parsedUrl;
    const method = req.method;

    // Set CORS headers for Cursor
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-API-Key');
    res.setHeader('Access-Control-Max-Age', '86400');

    // Handle preflight requests
    if (method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    try {
      switch (pathname) {
        case '/tools':
          await this.handleToolsRequest(req, res);
          break;

        case '/call':
          await this.handleToolCallRequest(req, res);
          break;

        case '/health':
          await this.handleHealthRequest(req, res);
          break;

        case '/status':
          await this.handleStatusRequest(req, res);
          break;

        default:
          res.writeHead(404, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({
            error: 'Not found',
            available_endpoints: ['/tools', '/call', '/health', '/status']
          }));
      }
    } catch (error) {
      console.error('❌ Request error:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        error: error.message,
        timestamp: new Date().toISOString()
      }));
    }
  }

  /**
   * Handle tools listing request
   */
  async handleToolsRequest(req, res) {
    if (req.method !== 'GET') {
      res.writeHead(405);
      res.end(JSON.stringify({ error: 'Method not allowed' }));
      return;
    }

    const tools = require('./nocodb-mcp-tools.json');

    res.writeHead(200, {
      'Content-Type': 'application/json',
      'Cache-Control': 'public, max-age=300'
    });
    res.end(JSON.stringify(tools));
  }

  /**
   * Handle tool call requests
   */
  async handleToolCallRequest(req, res) {
    if (req.method !== 'POST') {
      res.writeHead(405);
      res.end(JSON.stringify({ error: 'Method not allowed' }));
      return;
    }

    let body = '';
    req.on('data', chunk => {
      body += chunk.toString();
    });

    req.on('end', async () => {
      try {
        const { name, arguments: args } = JSON.parse(body);

        console.log(`🔧 Executing tool: ${name} at ${new Date().toISOString()}`);

        // Rate limiting (simple implementation)
        if (!this.checkRateLimit(req)) {
          res.writeHead(429, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ error: 'Rate limit exceeded' }));
          return;
        }

        const result = await this.executeTool(name, args);

        res.writeHead(200, {
          'Content-Type': 'application/json',
          'X-Tool-Executed': name
        });
        res.end(JSON.stringify(result));

      } catch (error) {
        console.error('❌ Tool execution error:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({
          error: error.message,
          tool_error: true,
          timestamp: new Date().toISOString()
        }));
      }
    });
  }

  /**
   * Handle health check request
   */
  async handleHealthRequest(req, res) {
    const health = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      version: '1.0.0',
      uptime: process.uptime(),
      memory: process.memoryUsage(),
      tools_available: 10,
      nocodb_connected: this.client ? true : false,
      server_info: {
        port: this.port,
        node_version: process.version,
        platform: process.platform
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(health));
  }

  /**
   * Handle status request with detailed server info
   */
  async handleStatusRequest(req, res) {
    const status = {
      server: {
        status: 'running',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        pid: process.pid
      },
      nocodb: {
        connected: this.client ? true : false,
        url: process.env.NOCODB_URL || 'https://nocodb.v1su4.com'
      },
      environment: {
        node_env: process.env.NODE_ENV,
        port: this.port,
        timestamp: new Date().toISOString()
      }
    };

    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(status));
  }

  /**
   * Simple rate limiting
   */
  checkRateLimit(req) {
    // Simple in-memory rate limiting
    const clientIP = req.socket.remoteAddress;
    const now = Date.now();

    if (!this.rateLimit) {
      this.rateLimit = new Map();
    }

    const clientData = this.rateLimit.get(clientIP) || { count: 0, resetTime: now + 60000 };

    if (now > clientData.resetTime) {
      clientData.count = 0;
      clientData.resetTime = now + 60000;
    }

    if (clientData.count >= 30) { // 30 requests per minute
      return false;
    }

    clientData.count++;
    this.rateLimit.set(clientIP, clientData);
    return true;
  }

  /**
   * Execute a specific tool
   */
  async executeTool(name, args) {
    // Initialize client if needed
    if (!this.client) {
      const nocodbUrl = process.env.NOCODB_URL || args.url || 'https://nocodb.v1su4.com';
      const apiToken = process.env.NOCODB_API_TOKEN || args.api_token;

      if (!apiToken) {
        throw new Error('NOCODB_API_TOKEN is required');
      }

      this.client = new NocoDBClient(nocodbUrl, apiToken);
      console.log(`🔗 Initialized NocoDB client for ${nocodbUrl}`);
    } else if (args.api_token && args.api_token !== process.env.NOCODB_API_TOKEN) {
      // Allow token override via arguments
      this.client.setApiToken(args.api_token);
    }

    switch (name) {
      case 'nocodb_test_connection':
        return await this.client.testConnection();

      case 'nocodb_list_projects':
        return await this.client.listProjects();

      case 'nocodb_list_tables':
        return await this.client.listTables(args.project_id);

      case 'nocodb_get_records':
        const queryParams = {
          limit: args.limit || 10,
          offset: args.offset || 0
        };
        return await this.client.getRecords(args.project_id, args.table_id, queryParams);

      case 'nocodb_create_record':
        return await this.client.createRecord(args.project_id, args.table_id, args.record_data);

      case 'nocodb_search_records':
        return await this.client.searchRecords(args.project_id, args.table_id, args.filters);

      case 'nocodb_update_record':
        return await this.client.updateRecord(args.project_id, args.table_id, args.record_id, args.record_data);

      case 'nocodb_delete_record':
        return await this.client.deleteRecord(args.project_id, args.table_id, args.record_id);

      case 'nocodb_create_discord_reactions_table':
        return await this.client.createDiscordHeartReactionsTable(args.project_id);

      case 'nocodb_get_analytics':
        return await this.getAnalytics(args.project_id, args.table_id);

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  }

  /**
   * Get analytics for Discord Heart Reactions
   */
  async getAnalytics(projectId, tableId) {
    try {
      const result = await this.client.getRecords(projectId, tableId, { limit: 1000 });

      if (!result.success) {
        return result;
      }

      const records = result.records;

      // Calculate analytics
      const analytics = {
        total_reactions: records.length,
        with_images: records.filter(r => r.image_url).length,
        cinematic_count: records.filter(r => r.cinematic).length,
        anime_count: records.filter(r => r.anime).length,
        with_sref_codes: records.filter(r => r.sref_code).length,
        shot_types: {},
        recent_24h: 0
      };

      // Shot type breakdown
      records.forEach(r => {
        if (r.shot_type) {
          analytics.shot_types[r.shot_type] = (analytics.shot_types[r.shot_type] || 0) + 1;
        }
      });

      // Recent activity (24 hours)
      const last24Hours = new Date(Date.now() - 24 * 60 * 60 * 1000);
      analytics.recent_24h = records.filter(r => new Date(r.timestamp) > last24Hours).length;

      return {
        success: true,
        analytics,
        summary: {
          message: `📊 ${analytics.total_reactions} total reactions, ${analytics.with_images} with images, ${analytics.recent_24h} in last 24h`,
          cinematic_percentage: analytics.total_reactions > 0 ? ((analytics.cinematic_count / analytics.total_reactions) * 100).toFixed(1) : '0',
          anime_percentage: analytics.total_reactions > 0 ? ((analytics.anime_count / analytics.total_reactions) * 100).toFixed(1) : '0',
          sref_coverage: analytics.total_reactions > 0 ? ((analytics.with_sref_codes / analytics.total_reactions) * 100).toFixed(1) : '0'
        }
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Graceful shutdown
   */
  async gracefulShutdown() {
    if (this.isShuttingDown) return;
    this.isShuttingDown = true;

    console.log('\n👋 Shutting down NocoDB MCP Server gracefully...');

    if (this.server) {
      this.server.close(() => {
        console.log('✅ HTTP server closed');
        process.exit(0);
      });

      // Force close after 10 seconds
      setTimeout(() => {
        console.log('⚠️  Force closing server');
        process.exit(1);
      }, 10000);
    } else {
      process.exit(0);
    }
  }
}

// Start server if executed directly
if (require.main === module) {
  const port = parseInt(process.env.PORT) || parseInt(process.argv[2]) || 3001;

  const server = new ProductionMCPServer(port);
  server.start().catch(error => {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  });
}

module.exports = ProductionMCPServer;
