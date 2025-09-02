# Complete MCP Servers Setup

## Overview
This document contains the complete configuration for all three MCP servers:
1. **Archon MCP** - Knowledge management and RAG system
2. **NocoDB MCP** - Database operations and data management  
3. **Dart AI MCP** - Task and project management

## Server Status
All servers are confirmed working as of 2025-09-02:

| Server | URL | Status | Authentication |
|--------|-----|--------|----------------|
| Archon | https://mcp.v1su4.com | ✅ Running | None required |
| NocoDB | https://mcp-nocodb.v1su4.com | ✅ Running | API token in env |
| Dart AI | https://mcp.dartai.com/mcp | ✅ Running | Bearer token |

## Warp Configuration

### Option 1: Individual Configurations

Add each server separately in Warp's MCP Server UI:

#### Archon MCP Server
```json
{
  "command": "mcp-remote",
  "args": [
    "https://mcp.v1su4.com",
    "--stdio"
  ]
}
```

#### NocoDB MCP Server
```json
{
  "command": "mcp-remote",
  "args": [
    "https://mcp-nocodb.v1su4.com",
    "--stdio"
  ]
}
```

#### Dart AI MCP Server (with authentication)
```json
{
  "command": "mcp-remote",
  "args": [
    "https://mcp.dartai.com/mcp",
    "--header",
    "Authorization: Bearer dsa_45d8279ad3da851b0c59f826f63dd9d0d7079cc8177b5c55e922c00fdb174eee",
    "--stdio"
  ]
}
```

### Option 2: Combined Configuration File

Save this as `mcp-servers-config.json`:

```json
{
  "mcpServers": {
    "archon": {
      "command": "mcp-remote",
      "args": [
        "https://mcp.v1su4.com",
        "--stdio"
      ]
    },
    "nocodb": {
      "command": "mcp-remote",
      "args": [
        "https://mcp-nocodb.v1su4.com",
        "--stdio"
      ]
    },
    "dartai": {
      "command": "mcp-remote",
      "args": [
        "https://mcp.dartai.com/mcp",
        "--header",
        "Authorization: Bearer dsa_45d8279ad3da851b0c59f826f63dd9d0d7079cc8177b5c55e922c00fdb174eee",
        "--stdio"
      ]
    }
  }
}
```

## Testing Commands

### Test Archon MCP
```powershell
curl -X POST https://mcp.v1su4.com -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{"roots":{"listChanged":true},"sampling":{}}},"id":1}'
```

### Test NocoDB MCP
```powershell
curl -X POST https://mcp-nocodb.v1su4.com -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" -d '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{"roots":{"listChanged":true},"sampling":{}}},"id":1}'
```

### Test Dart AI MCP
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "Accept" = "application/json, text/event-stream"
    "Authorization" = "Bearer dsa_45d8279ad3da851b0c59f826f63dd9d0d7079cc8177b5c55e922c00fdb174eee"
}
$body = '{"jsonrpc":"2.0","method":"initialize","params":{"protocolVersion":"1.0","capabilities":{"tools":{},"prompts":{}},"clientInfo":{"name":"warp-test","version":"1.0.0"}},"id":1}'
Invoke-RestMethod -Uri "https://mcp.dartai.com/mcp" -Method POST -Headers $headers -Body $body
```

## Available Capabilities

### Archon MCP
- Knowledge base management
- Document retrieval and search
- Project information storage
- MCP projects listing

### NocoDB MCP
- Test connection: `nocodb_test_connection()`
- List projects: `nocodb_list_projects()`
- List tables: `nocodb_list_tables(project_id)`
- Get records: `nocodb_get_records(project_id, table_id)`
- Create records: `nocodb_create_record(project_id, table_id, record_data)`
- Update records: `nocodb_update_record(project_id, table_id, record_id, record_data)`
- Delete records: `nocodb_delete_record(project_id, table_id, record_id)`
- Search records: `nocodb_search_records(project_id, table_id, filters)`

### Dart AI MCP
- Task management (create, update, delete)
- Document management
- Project planning
- Skills and workflow automation
- Due date handling
- Assignee management
- Tag organization

## Important IDs for NocoDB

### Base Project
- **Project ID**: `pce7ccvwdlz09bx`
- **Project Name**: Base

### Tables in Base Project
| Table Name | Table ID | Created |
|------------|----------|---------|
| Storygen | m0q17m2gufkjp39 | 2025-08-19 |
| Ideas API 1755668008 | mft4y2s8qq862lk | 2025-08-20 |
| Discord Heart Reactions | mikjku7fjf8ebiw | 2025-08-23 |
| **Notion Imports** | **m2qn2emzlgcjzun** | **2025-09-02** |

## Notes
- All MCP servers use the standard MCP protocol over HTTP/SSE
- Dart AI requires authentication via Bearer token
- NocoDB authentication is handled server-side via environment variables
- Archon does not require authentication
- All servers support JSON-RPC 2.0 protocol

## Troubleshooting
1. If a server shows as "Not Found", check the URL and path
2. For authentication errors, verify the Bearer token is current
3. For connection timeouts, check if the servers are deployed and running
4. Use the test commands above to verify connectivity
