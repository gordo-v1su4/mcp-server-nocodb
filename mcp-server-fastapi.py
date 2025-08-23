"""
NocoDB MCP Server - FastAPI Implementation
Alternative to the Node.js version for better async performance
"""

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import asyncio
import aiohttp
import logging
import os
from typing import Dict, Any, Optional
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="NocoDB MCP Server",
    description="Model Context Protocol server for NocoDB integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ToolCall(BaseModel):
    name: str
    arguments: Dict[str, Any]

class MCPResponse(BaseModel):
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None

# Global state
class MCPState:
    def __init__(self):
        self.nocodb_url = os.getenv("NOCODB_URL", "https://nocodb.v1su4.com")
        self.api_token = os.getenv("NOCODB_API_TOKEN")
        self.session: Optional[aiohttp.ClientSession] = None

    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()

# Global MCP state
mcp_state = MCPState()

@app.on_event("startup")
async def startup_event():
    """Initialize the MCP server on startup"""
    logger.info("🚀 Starting NocoDB MCP Server (FastAPI)")
    logger.info(f"NocoDB URL: {mcp_state.nocodb_url}")
    logger.info(f"API Token: {'Set' if mcp_state.api_token else 'Not Set'}")

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    logger.info("👋 Shutting down NocoDB MCP Server")
    await mcp_state.close()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "nocodb_connected": bool(mcp_state.api_token),
        "server_info": {
            "framework": "FastAPI",
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}",
            "nocodb_url": mcp_state.nocodb_url
        }
    }

@app.get("/tools")
async def list_tools():
    """List available MCP tools"""
    tools = {
        "name": "nocodb-mcp-tools",
        "description": "NocoDB Model Context Protocol tools for Cursor IDE integration",
        "version": "1.0.0",
        "tools": [
            {
                "name": "nocodb_test_connection",
                "description": "Test connection to NocoDB instance",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "NocoDB instance URL"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["api_token"]
                }
            },
            {
                "name": "nocodb_list_projects",
                "description": "List all projects in NocoDB",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["api_token"]
                }
            },
            {
                "name": "nocodb_list_tables",
                "description": "List tables in a project",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "api_token"]
                }
            },
            {
                "name": "nocodb_get_records",
                "description": "Get records from table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "limit": {"type": "integer", "description": "Max records", "default": 10},
                        "offset": {"type": "integer", "description": "Offset", "default": 0},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "api_token"]
                }
            },
            {
                "name": "nocodb_create_record",
                "description": "Create new record",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "record_data": {"type": "object", "description": "Record data"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "record_data", "api_token"]
                }
            },
            {
                "name": "nocodb_search_records",
                "description": "Search records with filters",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "filters": {"type": "object", "description": "Search filters"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "filters", "api_token"]
                }
            },
            {
                "name": "nocodb_update_record",
                "description": "Update existing record",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "record_id": {"type": "string", "description": "Record ID"},
                        "record_data": {"type": "object", "description": "Updated data"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "record_id", "record_data", "api_token"]
                }
            },
            {
                "name": "nocodb_delete_record",
                "description": "Delete record",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "record_id": {"type": "string", "description": "Record ID"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "record_id", "api_token"]
                }
            },
            {
                "name": "nocodb_create_discord_reactions_table",
                "description": "Create Discord reactions table",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "api_token"]
                }
            },
            {
                "name": "nocodb_get_analytics",
                "description": "Get Discord reactions analytics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_id": {"type": "string", "description": "Project ID"},
                        "table_id": {"type": "string", "description": "Table ID"},
                        "api_token": {"type": "string", "description": "NocoDB API token"}
                    },
                    "required": ["project_id", "table_id", "api_token"]
                }
            }
        ]
    }
    return tools

@app.post("/call", response_model=MCPResponse)
async def execute_tool(tool_call: ToolCall):
    """Execute MCP tool calls"""
    try:
        logger.info(f"🔧 Executing tool: {tool_call.name}")

        # Get or override API token
        api_token = tool_call.arguments.get("api_token", mcp_state.api_token)
        if not api_token:
            raise HTTPException(status_code=400, detail="API token required")

        # Execute the tool
        result = await execute_nocodb_tool(tool_call.name, tool_call.arguments, api_token)

        return MCPResponse(success=True, result=result)

    except Exception as e:
        logger.error(f"❌ Tool execution failed: {str(e)}")
        return MCPResponse(success=False, error=str(e))

async def execute_nocodb_tool(tool_name: str, args: Dict[str, Any], api_token: str) -> Any:
    """Execute NocoDB-specific tools"""
    session = await mcp_state.get_session()

    headers = {
        "Content-Type": "application/json",
        "xc-auth": api_token
    }

    base_url = args.get("url", mcp_state.nocodb_url).rstrip("/")

    if tool_name == "nocodb_test_connection":
        async with session.get(f"{base_url}/api/v1/db/meta/projects", headers=headers) as response:
            if response.status != 200:
                raise HTTPException(status_code=response.status, detail="Connection failed")
            return await response.json()

    elif tool_name == "nocodb_list_projects":
        async with session.get(f"{base_url}/api/v1/db/meta/projects", headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_list_tables":
        project_id = args["project_id"]
        async with session.get(f"{base_url}/api/v1/db/meta/projects/{project_id}/tables", headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_get_records":
        project_id = args["project_id"]
        table_id = args["table_id"]
        params = {
            "limit": args.get("limit", 10),
            "offset": args.get("offset", 0)
        }
        async with session.get(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            params=params
        ) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_create_record":
        project_id = args["project_id"]
        table_id = args["table_id"]
        record_data = args["record_data"]
        async with session.post(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            json=record_data
        ) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_search_records":
        project_id = args["project_id"]
        table_id = args["table_id"]
        filters = args.get("filters", {})
        params = {"where": json.dumps(filters)}
        async with session.get(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            params=params
        ) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_update_record":
        project_id = args["project_id"]
        table_id = args["table_id"]
        record_id = args["record_id"]
        record_data = args["record_data"]
        async with session.patch(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}/{record_id}",
            headers=headers,
            json=record_data
        ) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_delete_record":
        project_id = args["project_id"]
        table_id = args["table_id"]
        record_id = args["record_id"]
        async with session.delete(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}/{record_id}",
            headers=headers
        ) as response:
            response.raise_for_status()
            return {"message": "Record deleted successfully"}

    elif tool_name == "nocodb_create_discord_reactions_table":
        project_id = args["project_id"]
        table_schema = {
            "table_name": "discord_heart_reactions",
            "title": "Discord Heart Reactions",
            "columns": [
                {"column_name": "message_content", "title": "Message Content", "uidt": "Text", "required": True},
                {"column_name": "sref_code", "title": "SREF Code", "uidt": "SingleLineText"},
                {"column_name": "image_url", "title": "Image URL", "uidt": "URL"},
                {"column_name": "cinematic", "title": "Cinematic", "uidt": "Checkbox", "default": False},
                {"column_name": "anime", "title": "Anime", "uidt": "Checkbox", "default": False},
                {"column_name": "colors", "title": "Colors", "uidt": "Text"},
                {"column_name": "shot_type", "title": "Shot Type", "uidt": "SingleLineText"},
                {"column_name": "mood", "title": "Mood", "uidt": "SingleLineText"},
                {"column_name": "style", "title": "Style", "uidt": "SingleLineText"},
                {"column_name": "subject", "title": "Subject", "uidt": "Text"},
                {"column_name": "discord_message_id", "title": "Discord Message ID", "uidt": "SingleLineText", "required": True, "unique": True},
                {"column_name": "discord_channel_id", "title": "Discord Channel ID", "uidt": "SingleLineText", "required": True},
                {"column_name": "timestamp", "title": "Timestamp", "uidt": "DateTime", "required": True}
            ]
        }
        async with session.post(
            f"{base_url}/api/v1/db/meta/projects/{project_id}/tables",
            headers=headers,
            json=table_schema
        ) as response:
            response.raise_for_status()
            return await response.json()

    elif tool_name == "nocodb_get_analytics":
        project_id = args["project_id"]
        table_id = args["table_id"]

        # Get all records for analytics
        async with session.get(
            f"{base_url}/api/v1/db/data/noco/{project_id}/{table_id}?limit=1000",
            headers=headers
        ) as response:
            response.raise_for_status()
            data = await response.json()
            records = data.get("list", [])

            # Calculate analytics
            analytics = {
                "total_reactions": len(records),
                "with_images": len([r for r in records if r.get("image_url")]),
                "cinematic_count": len([r for r in records if r.get("cinematic")]),
                "anime_count": len([r for r in records if r.get("anime")]),
                "with_sref_codes": len([r for r in records if r.get("sref_code")]),
                "shot_types": {},
                "recent_24h": 0
            }

            # Shot type breakdown
            for record in records:
                if record.get("shot_type"):
                    analytics["shot_types"][record["shot_type"]] = analytics["shot_types"].get(record["shot_type"], 0) + 1

            # Recent activity (24 hours)
            from datetime import datetime, timedelta
            cutoff = datetime.now() - timedelta(hours=24)
            analytics["recent_24h"] = len([
                r for r in records
                if r.get("timestamp") and datetime.fromisoformat(r["timestamp"].replace('Z', '+00:00')) > cutoff
            ])

            return {
                "success": True,
                "analytics": analytics,
                "summary": {
                    "message": f"📊 {analytics['total_reactions']} total reactions, {analytics['with_images']} with images, {analytics['recent_24h']} in last 24h",
                    "cinematic_percentage": round((analytics['cinematic_count'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0,
                    "anime_percentage": round((analytics['anime_count'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0,
                    "sref_coverage": round((analytics['with_sref_codes'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0
                }
            }

    else:
        raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "success": False}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "success": False}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "mcp-server-fastapi:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 3001)),
        reload=os.getenv("NODE_ENV") != "production",
        log_level="info"
    )
