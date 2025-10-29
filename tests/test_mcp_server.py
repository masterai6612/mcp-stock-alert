#!/usr/bin/env python3
"""
Test script for the Yahoo Finance Enhanced MCP Server
"""

import asyncio
import json
from yahoo_finance_mcp_server import handle_list_tools, handle_call_tool

async def test_mcp_server():
    """Test the MCP server functionality"""
    print("🧪 Testing Yahoo Finance Enhanced MCP Server")
    print("=" * 50)
    
    # Test list tools
    print("\n1. Testing list_tools...")
    try:
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   - {tool.name}: {tool.description}")
    except Exception as e:
        print(f"❌ Error listing tools: {e}")
        return
    
    # Test get_stock_quote
    print("\n2. Testing get_stock_quote...")
    try:
        result = await handle_call_tool("get_stock_quote", {"symbol": "AAPL"})
        if result and result[0].text:
            data = json.loads(result[0].text)
            print(f"✅ AAPL quote: ${data.get('current_price', 'N/A')}")
        else:
            print("❌ No quote data returned")
    except Exception as e:
        print(f"❌ Error getting quote: {e}")
    
    # Test get_earnings_calendar
    print("\n3. Testing get_earnings_calendar...")
    try:
        result = await handle_call_tool("get_earnings_calendar", {"days_ahead": 7})
        if result and result[0].text:
            data = json.loads(result[0].text)
            earnings_count = data.get('earnings_count', 0)
            print(f"✅ Found {earnings_count} upcoming earnings")
            
            # Show first few earnings
            earnings = data.get('earnings_calendar', [])
            for i, earning in enumerate(earnings[:3]):
                print(f"   📅 {earning.get('symbol', 'N/A')}: {earning.get('company', 'N/A')}")
        else:
            print("❌ No earnings data returned")
    except Exception as e:
        print(f"❌ Error getting earnings: {e}")
    
    # Test get_investment_themes
    print("\n4. Testing get_investment_themes...")
    try:
        result = await handle_call_tool("get_investment_themes", {})
        if result and result[0].text:
            data = json.loads(result[0].text)
            
            # Show themes
            themes = data.get('themes', [])
            if themes:
                print(f"✅ Found {len(themes)} investment themes:")
                for theme in themes[:3]:
                    name = theme.get('theme', 'N/A')
                    change = theme.get('avg_change_percent', 0)
                    print(f"   🎯 {name}: {change:+.2f}%")
            
            # Show sectors
            sectors = data.get('trending_sectors', [])
            if sectors:
                print(f"✅ Found {len(sectors)} sectors:")
                for sector in sectors[:3]:
                    name = sector.get('sector', 'N/A')
                    change = sector.get('change_percent_5d', 0)
                    print(f"   📈 {name}: {change:+.2f}%")
        else:
            print("❌ No themes data returned")
    except Exception as e:
        print(f"❌ Error getting themes: {e}")
    
    print("\n" + "=" * 50)
    print("✅ MCP Server test completed!")

if __name__ == "__main__":
    asyncio.run(test_mcp_server())