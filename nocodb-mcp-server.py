"""
NocoDB MCP Server - Standard FastMCP Implementation

Production-ready Model Context Protocol server for NocoDB integration,
following the same pattern as Archon MCP server.
"""

import json
import logging
import os
import sys
import time
import traceback
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp
from dotenv import load_dotenv
from mcp.server.fastmcp import Context, FastMCP

# Load environment variables
load_dotenv()

# Configure logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("/tmp/nocodb_mcp_server.log", mode="a", encoding="utf-8")
        if os.path.exists("/tmp")
        else logging.NullHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Server configuration
server_host = "0.0.0.0"
server_port = int(os.getenv("PORT", 3001))


@dataclass
class NocoDBContext:
    """
    Context for NocoDB MCP server.
    """
    nocodb_url: str
    api_token: str
    session: Optional[aiohttp.ClientSession] = None
    startup_time: float = None

    def __post_init__(self):
        if self.startup_time is None:
            self.startup_time = time.time()

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session

    async def close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[NocoDBContext]:
    """
    Lifecycle manager for NocoDB MCP server
    """
    logger.info("Starting NocoDB MCP Server...")

    try:
        # Get configuration from environment
        nocodb_url = os.getenv("NOCODB_URL", "https://nocodb.v1su4.com")
        api_token = os.getenv("NOCODB_API_TOKEN")

        if not api_token:
            raise ValueError("NOCODB_API_TOKEN environment variable is required")

        # Create context
        context = NocoDBContext(
            nocodb_url=nocodb_url.rstrip("/"),
            api_token=api_token
        )

        logger.info(f"NocoDB URL: {context.nocodb_url}")
        logger.info("NocoDB MCP server ready")

        yield context

    except Exception as e:
        logger.error(f"Critical error in lifespan setup: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        # Clean up resources
        logger.info("Cleaning up NocoDB MCP server...")
        if hasattr(context, 'session'):
            await context.close_session()
        logger.info("NocoDB MCP server shutdown complete")


# Define MCP instructions
MCP_INSTRUCTIONS = """
# NocoDB MCP Server Instructions

## 🚨 CRITICAL RULES
1. **Always provide api_token** - All NocoDB operations require authentication
2. **Use correct project_id and table_id** - Get these from list operations first
3. **Handle pagination** - Use limit/offset for large datasets

## 📋 Available Tools

### Connection & Management
- `nocodb_test_connection()` - Test NocoDB connection and list projects
- `nocodb_list_projects()` - List all accessible projects
- `nocodb_list_tables(project_id)` - List tables in a project

### Data Operations
- `nocodb_get_records(project_id, table_id, limit=10, offset=0)` - Retrieve records
- `nocodb_create_record(project_id, table_id, record_data)` - Create new record
- `nocodb_update_record(project_id, table_id, record_id, record_data)` - Update record
- `nocodb_delete_record(project_id, table_id, record_id)` - Delete record
- `nocodb_search_records(project_id, table_id, filters)` - Search with filters

### Specialized Tools
- `nocodb_create_discord_reactions_table(project_id)` - Create Discord reactions table
- `nocodb_get_analytics(project_id, table_id)` - Get Discord reactions analytics

## 🔍 Common Workflows

### Discord Heart Reactions Workflow
1. Test connection: `nocodb_test_connection()`
2. Create table: `nocodb_create_discord_reactions_table(project_id)`
3. Add records: `nocodb_create_record(project_id, table_id, reaction_data)`
4. Get analytics: `nocodb_get_analytics(project_id, table_id)`

### General Data Management
1. List projects: `nocodb_list_projects()`
2. List tables: `nocodb_list_tables(project_id)`
3. Get records: `nocodb_get_records(project_id, table_id)`
4. Perform operations as needed

## 🎯 Best Practices
- Always test connection before starting work
- Use meaningful record data with proper field names
- Handle errors gracefully and provide user feedback
- Use analytics tools to understand data patterns
"""

# Initialize FastMCP server
try:
    logger.info("NOCODB MCP SERVER INITIALIZATION")
    logger.info("   Server Name: nocodb-mcp-server")
    logger.info("   Description: Standard MCP server for NocoDB integration")

    mcp = FastMCP(
        "nocodb-mcp-server",
        instructions=MCP_INSTRUCTIONS,
        lifespan=lifespan,
        host=server_host,
        port=server_port,
        streamable_http_path="/"
    )
    logger.info("FastMCP server instance created successfully")

except Exception as e:
    logger.error(f"Failed to create FastMCP server: {e}")
    logger.error(traceback.format_exc())
    raise


# Health check tool
@mcp.tool()
async def health_check(ctx: Context) -> str:
    """
    Check health status of NocoDB MCP server.
    
    Returns:
        JSON with health status, uptime, and NocoDB connection info
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context", None)
        
        if context is None:
            return json.dumps({
                "success": True,
                "status": "starting",
                "message": "NocoDB MCP server is initializing...",
                "timestamp": datetime.now().isoformat(),
            })

        # Test NocoDB connection
        session = await context.get_session()
        headers = {"xc-token": context.api_token}
        
        nocodb_status = "unknown"
        try:
            async with session.get(f"{context.nocodb_url}/api/v1/db/meta/projects", headers=headers) as response:
                nocodb_status = "healthy" if response.status == 200 else "unhealthy"
        except Exception as e:
            nocodb_status = f"error: {str(e)}"

        return json.dumps({
            "success": True,
            "status": "healthy",
            "nocodb_status": nocodb_status,
            "uptime_seconds": time.time() - context.startup_time,
            "nocodb_url": context.nocodb_url,
            "timestamp": datetime.now().isoformat(),
        })

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Health check failed: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        })


# NocoDB Tools
@mcp.tool()
async def nocodb_test_connection(ctx: Context) -> str:
    """
    Test connection to NocoDB instance and list available projects.
    
    Returns:
        JSON with connection status and project list
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}

        async with session.get(f"{context.nocodb_url}/api/v1/db/meta/projects", headers=headers) as response:
            if response.status != 200:
                error_text = await response.text()
                return json.dumps({
                    "success": False,
                    "error": f"Connection failed with status {response.status}: {error_text}",
                })

            projects = await response.json()
            return json.dumps({
                "success": True,
                "message": "Connection successful",
                "projects_count": len(projects.get("list", [])),
                "projects": projects,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"NocoDB connection test failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Connection test failed: {str(e)}",
        })


@mcp.tool()
async def nocodb_list_projects(ctx: Context) -> str:
    """
    List all projects in NocoDB.
    
    Returns:
        JSON with list of projects
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}

        async with session.get(f"{context.nocodb_url}/api/v1/db/meta/projects", headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "projects": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"List projects failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to list projects: {str(e)}",
        })


@mcp.tool()
async def nocodb_list_tables(ctx: Context, project_id: str) -> str:
    """
    List tables in a NocoDB project.
    
    Args:
        project_id: The project ID to list tables from
        
    Returns:
        JSON with list of tables in the project
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}

        async with session.get(f"{context.nocodb_url}/api/v1/db/meta/projects/{project_id}/tables", headers=headers) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "tables": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"List tables failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to list tables: {str(e)}",
        })


@mcp.tool()
async def nocodb_get_records(ctx: Context, project_id: str, table_id: str, limit: int = 10, offset: int = 0) -> str:
    """
    Get records from a NocoDB table.
    
    Args:
        project_id: The project ID
        table_id: The table ID
        limit: Maximum number of records to return (default: 10)
        offset: Number of records to skip (default: 0)
        
    Returns:
        JSON with records from the table
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}
        
        params = {"limit": limit, "offset": offset}

        async with session.get(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "records": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Get records failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to get records: {str(e)}",
        })


@mcp.tool()
async def nocodb_create_record(ctx: Context, project_id: str, table_id: str, record_data: dict) -> str:
    """
    Create a new record in a NocoDB table.
    
    Args:
        project_id: The project ID
        table_id: The table ID
        record_data: Dictionary with field names and values for the new record
        
    Returns:
        JSON with the created record
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token, "Content-Type": "application/json"}

        async with session.post(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            json=record_data
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "record": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Create record failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to create record: {str(e)}",
        })


@mcp.tool()
async def nocodb_update_record(ctx: Context, project_id: str, table_id: str, record_id: str, record_data: dict) -> str:
    """
    Update an existing record in a NocoDB table.
    
    Args:
        project_id: The project ID
        table_id: The table ID
        record_id: The record ID to update
        record_data: Dictionary with field names and new values
        
    Returns:
        JSON with the updated record
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token, "Content-Type": "application/json"}

        async with session.patch(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}/{record_id}",
            headers=headers,
            json=record_data
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "record_id": record_id,
                "record": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Update record failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to update record: {str(e)}",
        })


@mcp.tool()
async def nocodb_delete_record(ctx: Context, project_id: str, table_id: str, record_id: str) -> str:
    """
    Delete a record from a NocoDB table.
    
    Args:
        project_id: The project ID
        table_id: The table ID
        record_id: The record ID to delete
        
    Returns:
        JSON with deletion confirmation
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}

        async with session.delete(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}/{record_id}",
            headers=headers
        ) as response:
            response.raise_for_status()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "record_id": record_id,
                "message": "Record deleted successfully",
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Delete record failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to delete record: {str(e)}",
        })


@mcp.tool()
async def nocodb_search_records(ctx: Context, project_id: str, table_id: str, filters: dict) -> str:
    """
    Search records in a NocoDB table with filters.
    
    Args:
        project_id: The project ID
        table_id: The table ID
        filters: Dictionary with search filters
        
    Returns:
        JSON with matching records
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}
        
        params = {"where": json.dumps(filters)}

        async with session.get(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}",
            headers=headers,
            params=params
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "filters": filters,
                "records": data,
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Search records failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to search records: {str(e)}",
        })


@mcp.tool()
async def nocodb_create_discord_reactions_table(ctx: Context, project_id: str) -> str:
    """
    Create a Discord Heart Reactions table with predefined schema.
    
    Args:
        project_id: The project ID where the table will be created
        
    Returns:
        JSON with the created table information
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token, "Content-Type": "application/json"}

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
            f"{context.nocodb_url}/api/v1/db/meta/projects/{project_id}/tables",
            headers=headers,
            json=table_schema
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table": data,
                "message": "Discord Heart Reactions table created successfully",
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Create Discord reactions table failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to create Discord reactions table: {str(e)}",
        })


@mcp.tool()
async def nocodb_get_analytics(ctx: Context, project_id: str, table_id: str) -> str:
    """
    Get Discord reactions analytics from a table.
    
    Args:
        project_id: The project ID
        table_id: The table ID (should be Discord reactions table)
        
    Returns:
        JSON with analytics data and summary
    """
    try:
        context = getattr(ctx.request_context, "lifespan_context")
        session = await context.get_session()
        headers = {"xc-token": context.api_token}

        # Get all records for analytics
        async with session.get(
            f"{context.nocodb_url}/api/v1/db/data/noco/{project_id}/{table_id}?limit=1000",
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
                    shot_type = record["shot_type"]
                    analytics["shot_types"][shot_type] = analytics["shot_types"].get(shot_type, 0) + 1

            # Recent activity (24 hours)
            from datetime import timedelta
            cutoff = datetime.now() - timedelta(hours=24)
            for record in records:
                if record.get("timestamp"):
                    try:
                        record_time = datetime.fromisoformat(record["timestamp"].replace('Z', '+00:00'))
                        if record_time > cutoff:
                            analytics["recent_24h"] += 1
                    except (ValueError, AttributeError):
                        pass

            return json.dumps({
                "success": True,
                "project_id": project_id,
                "table_id": table_id,
                "analytics": analytics,
                "summary": {
                    "message": f"{analytics['total_reactions']} total reactions, {analytics['with_images']} with images, {analytics['recent_24h']} in last 24h",
                    "cinematic_percentage": round((analytics['cinematic_count'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0,
                    "anime_percentage": round((analytics['anime_count'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0,
                    "sref_coverage": round((analytics['with_sref_codes'] / analytics['total_reactions']) * 100, 1) if analytics['total_reactions'] > 0 else 0
                },
                "timestamp": datetime.now().isoformat(),
            })

    except Exception as e:
        logger.error(f"Get analytics failed: {e}")
        return json.dumps({
            "success": False,
            "error": f"Failed to get analytics: {str(e)}",
        })


def main():
    """Main entry point for the NocoDB MCP server."""
    try:
        logger.info("Starting NocoDB MCP Server")
        logger.info("   Mode: Streamable HTTP")
        logger.info(f"   URL: http://{server_host}:{server_port}/")
        
        # Run with streamable-http transport
        mcp.run(transport="streamable-http")

    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("NocoDB MCP server stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)