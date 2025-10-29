"""
MCP Server for Yahoo Finance Enhanced Data Integration
Provides tools to fetch stock data, earnings calendar, and investment themes from Yahoo Finance
"""

import json
import asyncio
from typing import Any, Sequence
from mcp.server import Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.server.stdio
import mcp.types as types

# Import our enhanced Yahoo Finance client
from enhanced_yahoo_client import EnhancedYahooClient

server = Server("yahoo-finance-enhanced-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available Yahoo Finance enhanced data tools"""
    return [
        Tool(
            name="get_stock_quote",
            description="Get real-time stock quote from Yahoo Finance",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, NVDA)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_earnings_calendar",
            description="Get earnings calendar from Yahoo Finance",
            inputSchema={
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to look for earnings (default: 7)",
                        "default": 7
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_investment_themes",
            description="Get investment themes, trending sectors, and market themes",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:
    """Handle tool calls for Yahoo Finance enhanced data"""
    
    try:
        client = EnhancedYahooClient()
        
        if name == "get_stock_quote":
            symbol = arguments["symbol"]
            
            quote = client.get_stock_quote(symbol)
            if quote:
                return [types.TextContent(
                    type="text",
                    text=json.dumps(quote, indent=2, default=str)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Failed to get quote for {symbol}"
                )]
        
        elif name == "get_earnings_calendar":
            days_ahead = arguments.get("days_ahead", 7)
            
            earnings_data = client.get_earnings_calendar(days_ahead)
            if earnings_data:
                result = {
                    "days_ahead": days_ahead,
                    "earnings_count": len(earnings_data),
                    "earnings_calendar": earnings_data
                }
                return [types.TextContent(
                    type="text",
                    text=json.dumps(result, indent=2, default=str)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="Failed to get earnings calendar"
                )]
        
        elif name == "get_investment_themes":
            themes_data = client.get_investment_themes()
            if themes_data:
                return [types.TextContent(
                    type="text",
                    text=json.dumps(themes_data, indent=2, default=str)
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text="Failed to get investment themes"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        return [types.TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]

async def main():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())