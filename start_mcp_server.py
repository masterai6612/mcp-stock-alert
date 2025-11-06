#!/usr/bin/env python3
"""
MCP Server for Yahoo Finance Enhanced
"""
import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

# MCP Server Implementation
class MCPServer:
    def __init__(self):
        self.tools = {
            "get_stock_quote": self.get_stock_quote,
            "get_earnings_calendar": self.get_earnings_calendar,
            "get_investment_themes": self.get_investment_themes,
            "analyze_stock": self.analyze_stock
        }
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            current_price = hist['Close'].iloc[-1]
            
            return {
                "symbol": symbol,
                "price": float(current_price),
                "currency": info.get("currency", "USD"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
                "52_week_high": info.get("fiftyTwoWeekHigh"),
                "52_week_low": info.get("fiftyTwoWeekLow"),
                "volume": int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else None,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_earnings_calendar(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get earnings calendar"""
        try:
            # This is a simplified version - in production you'd use a proper earnings API
            end_date = datetime.now() + timedelta(days=days_ahead)
            
            return {
                "earnings_calendar": [],
                "days_ahead": days_ahead,
                "note": "Earnings calendar requires premium data source",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def get_investment_themes(self) -> Dict[str, Any]:
        """Get investment themes"""
        try:
            themes = [
                {"name": "AI & Technology", "trend": "bullish"},
                {"name": "Clean Energy", "trend": "bullish"},
                {"name": "Healthcare Innovation", "trend": "neutral"},
                {"name": "Cybersecurity", "trend": "bullish"},
                {"name": "E-commerce", "trend": "neutral"}
            ]
            
            return {
                "themes": themes,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def analyze_stock(self, symbol: str) -> Dict[str, Any]:
        """Comprehensive stock analysis"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="3mo")
            info = ticker.info
            
            if hist.empty:
                return {"error": f"No data found for {symbol}"}
            
            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else None
            
            # Price analysis
            current_price = hist['Close'].iloc[-1]
            price_change_pct = ((current_price - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            
            return {
                "symbol": symbol,
                "analysis": {
                    "current_price": float(current_price),
                    "price_change_pct": float(price_change_pct),
                    "rsi": float(current_rsi) if current_rsi else None,
                    "volume": int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else None,
                    "market_cap": info.get("marketCap"),
                    "pe_ratio": info.get("trailingPE"),
                    "recommendation": self._get_recommendation(current_rsi, price_change_pct)
                },
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _get_recommendation(self, rsi: Optional[float], price_change_pct: float) -> str:
        """Get stock recommendation based on indicators"""
        if rsi is None:
            return "INSUFFICIENT_DATA"
        
        if rsi < 30 and price_change_pct > 2:
            return "BUY"
        elif rsi > 70 and price_change_pct < -2:
            return "SELL"
        elif 40 <= rsi <= 60:
            return "HOLD"
        else:
            return "WATCH"
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request"""
        try:
            method = request.get("method")
            params = request.get("params", {})
            
            if method in self.tools:
                result = await self.tools[method](**params)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

async def main():
    """Main MCP server loop"""
    server = MCPServer()
    
    print("🚀 MCP Yahoo Finance Server started", file=sys.stderr)
    print("Available tools:", list(server.tools.keys()), file=sys.stderr)
    
    try:
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                request = json.loads(line.strip())
                response = await server.handle_request(request)
                
                print(json.dumps(response))
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error"
                    }
                }
                print(json.dumps(error_response))
                sys.stdout.flush()
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
                
    except KeyboardInterrupt:
        print("🛑 MCP Server stopped", file=sys.stderr)

if __name__ == "__main__":
    asyncio.run(main())