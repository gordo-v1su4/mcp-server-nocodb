/**
 * NocoDB MCP (Model Context Protocol) Client
 * For interacting with NocoDB instance at nocodb.v1su4.com
 * Built for Discord Heart Reaction workflow
 */

class NocoDBClient {
  constructor(baseUrl = 'https://nocodb.v1su4.com', apiToken = null) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.apiToken = apiToken;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
      'xc-auth': apiToken || process.env.NOCODB_API_TOKEN
    };
  }

  /**
   * Set API token for authentication
   */
  setApiToken(token) {
    this.apiToken = token;
    this.defaultHeaders['xc-auth'] = token;
  }

  /**
   * Test connection to NocoDB
   */
  async testConnection() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return {
        success: true,
        message: 'Connected to NocoDB successfully',
        projects: data
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        message: 'Failed to connect to NocoDB'
      };
    }
  }

  /**
   * List all projects
   */
  async listProjects() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const projects = await response.json();
      return {
        success: true,
        projects: projects.list || projects
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get project metadata
   */
  async getProject(projectId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects/${projectId}`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const project = await response.json();
      return {
        success: true,
        project
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * List tables in a project
   */
  async listTables(projectId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects/${projectId}/tables`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const tables = await response.json();
      return {
        success: true,
        tables: tables.list || tables
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get table metadata
   */
  async getTable(projectId, tableId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects/${projectId}/tables/${tableId}`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const table = await response.json();
      return {
        success: true,
        table
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create a new table
   */
  async createTable(projectId, tableData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/meta/projects/${projectId}/tables`, {
        method: 'POST',
        headers: this.defaultHeaders,
        body: JSON.stringify(tableData)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        success: true,
        table: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get table records
   */
  async getRecords(projectId, tableId, queryParams = {}) {
    try {
      const queryString = new URLSearchParams(queryParams).toString();
      const url = `${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}?${queryString}`;

      const response = await fetch(url, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const records = await response.json();
      return {
        success: true,
        records: records.list || records,
        pageInfo: records.pageInfo
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create a new record
   */
  async createRecord(projectId, tableId, recordData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}`, {
        method: 'POST',
        headers: this.defaultHeaders,
        body: JSON.stringify(recordData)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        success: true,
        record: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Update a record
   */
  async updateRecord(projectId, tableId, recordId, recordData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}/${recordId}`, {
        method: 'PATCH',
        headers: this.defaultHeaders,
        body: JSON.stringify(recordData)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        success: true,
        record: result
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Delete a record
   */
  async deleteRecord(projectId, tableId, recordId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}/${recordId}`, {
        method: 'DELETE',
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return {
        success: true,
        message: 'Record deleted successfully'
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Get record by ID
   */
  async getRecord(projectId, tableId, recordId) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}/${recordId}`, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const record = await response.json();
      return {
        success: true,
        record
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Search records with filters
   */
  async searchRecords(projectId, tableId, filters = {}, queryParams = {}) {
    try {
      const searchParams = {
        ...queryParams,
        where: JSON.stringify(filters)
      };

      const queryString = new URLSearchParams(searchParams).toString();
      const url = `${this.baseUrl}/api/v1/db/data/noco/${projectId}/${tableId}?${queryString}`;

      const response = await fetch(url, {
        headers: this.defaultHeaders
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const records = await response.json();
      return {
        success: true,
        records: records.list || records,
        pageInfo: records.pageInfo
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Execute SQL query (if enabled in NocoDB)
   */
  async executeQuery(projectId, query) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/db/data/noco/${projectId}/query`, {
        method: 'POST',
        headers: this.defaultHeaders,
        body: JSON.stringify({ query })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const result = await response.json();
      return {
        success: true,
        result
      };
    } catch (error) {
      return {
        success: false,
        error: error.message
      };
    }
  }

  /**
   * Create Discord Heart Reactions table schema
   */
  async createDiscordHeartReactionsTable(projectId) {
    const tableSchema = {
      table_name: 'discord_heart_reactions',
      title: 'Discord Heart Reactions',
      columns: [
        {
          column_name: 'message_content',
          title: 'Message Content',
          uidt: 'Text',
          required: true
        },
        {
          column_name: 'sref_code',
          title: 'SREF Code',
          uidt: 'SingleLineText'
        },
        {
          column_name: 'image_url',
          title: 'Image URL',
          uidt: 'URL'
        },
        {
          column_name: 'cinematic',
          title: 'Cinematic',
          uidt: 'Checkbox',
          default: false
        },
        {
          column_name: 'anime',
          title: 'Anime',
          uidt: 'Checkbox',
          default: false
        },
        {
          column_name: 'colors',
          title: 'Colors',
          uidt: 'Text'
        },
        {
          column_name: 'shot_type',
          title: 'Shot Type',
          uidt: 'SingleLineText'
        },
        {
          column_name: 'mood',
          title: 'Mood',
          uidt: 'SingleLineText'
        },
        {
          column_name: 'style',
          title: 'Style',
          uidt: 'SingleLineText'
        },
        {
          column_name: 'subject',
          title: 'Subject',
          uidt: 'Text'
        },
        {
          column_name: 'discord_message_id',
          title: 'Discord Message ID',
          uidt: 'SingleLineText',
          required: true,
          unique: true
        },
        {
          column_name: 'discord_channel_id',
          title: 'Discord Channel ID',
          uidt: 'SingleLineText',
          required: true
        },
        {
          column_name: 'timestamp',
          title: 'Timestamp',
          uidt: 'DateTime',
          required: true,
          default: 'now()'
        }
      ]
    };

    return await this.createTable(projectId, tableSchema);
  }
}

// Export for Node.js usage
if (typeof module !== 'undefined' && module.exports) {
  module.exports = NocoDBClient;
}

// Export for browser usage
if (typeof window !== 'undefined') {
  window.NocoDBClient = NocoDBClient;
}

console.log('NocoDB MCP Client loaded successfully!');
