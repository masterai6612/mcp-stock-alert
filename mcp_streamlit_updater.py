#!/usr/bin/env python3
"""
MCP Tool for Streamlit Data Updates
Provides MCP interface to update Streamlit dashboard data
"""

import json
import sys
from datetime import datetime

# Check if MCP is available
try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent
    import mcp.server.stdio
    import mcp.types as types
    MCP_AVAILABLE = True
except ImportError:
    print("⚠️ MCP not available")
    MCP_AVAILABLE = False

if MCP_AVAILABLE:
    server = Server("streamlit-updater")

    @server.list_tools()
    async def handle_list_tools() -> list[Tool]:
        """List available Streamlit update tools"""
        return [
            Tool(
                name="update_streamlit_data",
                description="Update Streamlit dashboard data with latest stock analysis",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "force": {
                            "type": "boolean",
                            "description": "Force update even if recently updated",
                            "default": False
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="get_streamlit_status",
                description="Get current status of Streamlit dashboard data",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="trigger_github_workflow",
                description="Trigger GitHub Actions workflow to update data",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            )
        ]

    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls for Streamlit updates"""
        
        if name == "update_streamlit_data":
            try:
                import subprocess
                
                force = arguments.get("force", False)
                
                # Run the update script
                result = subprocess.run(
                    [sys.executable, "update_streamlit_data.py"],
                    capture_output=True,
                    text=True,
                    timeout=600
                )
                
                if result.returncode == 0:
                    return [types.TextContent(
                        type="text",
                        text=f"✅ Streamlit data updated successfully!\n\n{result.stdout}"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"⚠️ Update completed with warnings:\n\n{result.stdout}\n\nErrors:\n{result.stderr}"
                    )]
            
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error updating data: {str(e)}"
                )]
        
        elif name == "get_streamlit_status":
            try:
                import os
                
                status = {
                    "timestamp": datetime.now().isoformat(),
                    "files": {}
                }
                
                # Check data files
                files_to_check = [
                    "gemma_top_10_picks.json",
                    "streamlit_data_summary.json",
                    "last_recommendations.json"
                ]
                
                for file in files_to_check:
                    if os.path.exists(file):
                        stat = os.stat(file)
                        status["files"][file] = {
                            "exists": True,
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        }
                    else:
                        status["files"][file] = {"exists": False}
                
                # Read summary if available
                if os.path.exists("streamlit_data_summary.json"):
                    with open("streamlit_data_summary.json", "r") as f:
                        summary = json.load(f)
                    status["summary"] = summary
                
                return [types.TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]
            
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error getting status: {str(e)}"
                )]
        
        elif name == "trigger_github_workflow":
            try:
                import subprocess
                
                # Try to trigger GitHub workflow using gh CLI
                result = subprocess.run(
                    ["gh", "workflow", "run", "update-streamlit-data.yml"],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    return [types.TextContent(
                        type="text",
                        text="✅ GitHub Actions workflow triggered!\n\nThe workflow will run and update data automatically.\nCheck: https://github.com/masterai6612/mcp-stock-alert/actions"
                    )]
                else:
                    return [types.TextContent(
                        type="text",
                        text=f"⚠️ Could not trigger workflow. You may need to install GitHub CLI (gh).\n\nManual trigger: Go to https://github.com/masterai6612/mcp-stock-alert/actions and click 'Run workflow'"
                    )]
            
            except FileNotFoundError:
                return [types.TextContent(
                    type="text",
                    text="⚠️ GitHub CLI (gh) not installed.\n\nTo trigger manually:\n1. Go to https://github.com/masterai6612/mcp-stock-alert/actions\n2. Click 'Update Streamlit Data'\n3. Click 'Run workflow'\n4. Select branch and click 'Run workflow'"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"❌ Error: {str(e)}"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]

    async def main():
        """Main entry point for MCP server"""
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

if __name__ == "__main__":
    if not MCP_AVAILABLE:
        print("❌ MCP not available. Install with: pip install mcp")
        sys.exit(1)
    
    import asyncio
    asyncio.run(main())
