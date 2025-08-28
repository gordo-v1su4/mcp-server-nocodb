#!/usr/bin/env node

/**
 * MCP Client Wrapper for Cursor IDE
 * Connects to hosted NocoDB MCP server
 * Acts as a bridge between Cursor and the remote server
 */

const http = require('http');
const https = require('https');

class MCPClientWrapper {
  constructor() {
    this.serverUrl = process.env.MCP_SERVER_URL || 'https://mcp.v1su4.com';
    this.apiToken = process.env.NOCODB_API_TOKEN;

    if (!this.apiToken) {
      console.error('❌ NOCODB_API_TOKEN environment variable is required');
      console.error('Set it with: export NOCODB_API_TOKEN="your_token_here"');
      process.exit(1);
    }
  }

  /**
   * Make HTTP request to MCP server
   */
  async makeRequest(endpoint, data = null, method = 'GET') {
    return new Promise((resolve, reject) => {
      const url = new URL(endpoint, this.serverUrl);
      const client = url.protocol === 'https:' ? https : http;

      const options = {
        hostname: url.hostname,
        port: url.port,
        path: url.pathname + url.search,
        method: method,
        headers: {
          'Content-Type': 'application/json',
          'User-Agent': 'Cursor-MCP-Client/1.0.0'
        }
      };

      if (data) {
        options.headers['Content-Length'] = Buffer.byteLength(JSON.stringify(data));
      }

      const req = client.request(options, (res) => {
        let body = '';

        res.on('data', (chunk) => {
          body += chunk;
        });

        res.on('end', () => {
          try {
            if (res.statusCode >= 200 && res.statusCode < 300) {
              const result = body ? JSON.parse(body) : null;
              resolve(result);
            } else {
              reject(new Error(`HTTP ${res.statusCode}: ${body}`));
            }
          } catch (error) {
            reject(new Error(`Failed to parse response: ${error.message}`));
          }
        });
      });

      req.on('error', (error) => {
        reject(new Error(`Request failed: ${error.message}`));
      });

      if (data) {
        req.write(JSON.stringify(data));
      }

      req.end();
    });
  }

  /**
   * Handle MCP tool calls
   */
  async handleToolCall(toolName, args) {
    try {
      console.log(`🔧 Calling remote tool: ${toolName}`);

      const requestData = {
        name: toolName,
        arguments: {
          ...args,
          api_token: this.apiToken
        }
      };

      const result = await this.makeRequest('/call', requestData, 'POST');
      return result;

    } catch (error) {
      console.error(`❌ Tool call failed: ${error.message}`);
      return {
        error: error.message,
        success: false
      };
    }
  }

  /**
   * Get available tools from server
   */
  async getAvailableTools() {
    try {
      const tools = await this.makeRequest('/tools');
      return tools;
    } catch (error) {
      console.error(`❌ Failed to get tools: ${error.message}`);
      return { tools: [] };
    }
  }

  /**
   * Check server health
   */
  async checkHealth() {
    try {
      const health = await this.makeRequest('/health');
      return health;
    } catch (error) {
      return { status: 'unhealthy', error: error.message };
    }
  }

  /**
   * Process command line arguments
   */
  async processArgs() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
      // Show help
      console.log('🤖 NocoDB MCP Client Wrapper');
      console.log('');
      console.log('Usage:');
      console.log('  node mcp-client-wrapper.js <tool_name> [args...]');
      console.log('  node mcp-client-wrapper.js tools');
      console.log('  node mcp-client-wrapper.js health');
      console.log('');
      console.log('Examples:');
      console.log('  node mcp-client-wrapper.js nocodb_test_connection');
      console.log('  node mcp-client-wrapper.js nocodb_list_projects');
      console.log('  node mcp-client-wrapper.js nocodb_get_records project_id table_id');
      return;
    }

    const command = args[0];

    switch (command) {
      case 'tools':
        const toolsResult = await this.getAvailableTools();
        console.log(JSON.stringify(toolsResult, null, 2));
        break;

      case 'health':
        const healthResult = await this.checkHealth();
        console.log(JSON.stringify(healthResult, null, 2));
        break;

      default:
        // This is a tool call
        const toolArgs = {};

        // Parse additional arguments
        for (let i = 1; i < args.length; i += 2) {
          if (args[i] && args[i+1]) {
            toolArgs[args[i]] = args[i+1];
          }
        }

        const result = await this.handleToolCall(command, toolArgs);
        console.log(JSON.stringify(result, null, 2));
    }
  }
}

// Run if executed directly
if (require.main === module) {
  const wrapper = new MCPClientWrapper();
  wrapper.processArgs().catch(error => {
    console.error('❌ Error:', error.message);
    process.exit(1);
  });
}

module.exports = MCPClientWrapper;
