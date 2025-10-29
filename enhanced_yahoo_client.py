"""
Enhanced Yahoo Finance Client
Adds earnings calendar and investment themes to your existing setup
No additional API keys required!
"""

import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

class EnhancedYahooClient:
    """Enhanced Yahoo Finance client with earnings and themes"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """Get real-time stock quote"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = hist['Close'].iloc[-1]
                open_price = hist['Open'].iloc[-1]
                change_pct = ((current_price - open_price) / open_price) * 100
                
                return {
                    'symbol': symbol,
                    'current_price': current_price,
                    'open_price': open_price,
                    'change_percent': change_pct,
                    'volume': hist['Volume'].iloc[-1],
                    'market_cap': info.get('marketCap'),
                    'pe_ratio': info.get('trailingPE'),
                    'company_name': info.get('longName', symbol)
                }
        except Exception as e:
            print(f"Error getting quote for {symbol}: {e}")
            return None
    
    def get_earnings_calendar(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get earnings calendar from Yahoo Finance
        """
        try:
            # Yahoo Finance earnings calendar URL
            url = "https://finance.yahoo.com/calendar/earnings"
            
            # Calculate date range
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            params = {
                'from': start_date.strftime('%Y-%m-%d'),
                'to': end_date.strftime('%Y-%m-%d'),
                'day': start_date.strftime('%Y-%m-%d')
            }
            
            response = self.session.get(url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            earnings_data = []
            
            # Look for earnings table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # Skip header
                    cells = row.find_all('td')
                    if len(cells) >= 4:
                        try:
                            symbol_cell = cells[0].find('a')
                            symbol = symbol_cell.text.strip() if symbol_cell else 'N/A'
                            
                            company_cell = cells[1]
                            company = company_cell.text.strip() if company_cell else 'N/A'
                            
                            earnings_data.append({
                                'symbol': symbol,
                                'company': company,
                                'date': start_date.strftime('%Y-%m-%d'),
                                'source': 'yahoo_finance'
                            })
                        except Exception:
                            continue
            
            # If web scraping fails, use known earnings from yfinance
            if not earnings_data:
                earnings_data = self._get_earnings_from_calendar_api(days_ahead)
            
            return earnings_data[:20]  # Limit to 20 results
            
        except Exception as e:
            print(f"Error getting earnings calendar: {e}")
            return []
    
    def _get_earnings_from_calendar_api(self, days_ahead: int) -> List[Dict]:
        """Fallback method to get earnings from alternative source"""
        # Use a list of major stocks and check their earnings dates
        major_stocks = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'AMD',
            'NFLX', 'CRM', 'ORCL', 'ADBE', 'PYPL', 'INTC', 'CSCO', 'PEP',
            'KO', 'DIS', 'BA', 'GE', 'JPM', 'BAC', 'WMT', 'HD', 'PG'
        ]
        
        earnings_data = []
        for symbol in major_stocks[:10]:  # Check first 10 to avoid rate limits
            try:
                ticker = yf.Ticker(symbol)
                calendar = ticker.calendar
                if calendar is not None and not calendar.empty:
                    next_earnings = calendar.index[0] if len(calendar.index) > 0 else None
                    if next_earnings:
                        earnings_data.append({
                            'symbol': symbol,
                            'company': ticker.info.get('longName', symbol),
                            'date': next_earnings.strftime('%Y-%m-%d'),
                            'source': 'yfinance_calendar'
                        })
            except Exception:
                continue
        
        return earnings_data
    
    def get_investment_themes(self) -> Dict:
        """
        Get investment themes and trending sectors
        """
        themes_data = {
            'trending_sectors': self._get_sector_performance(),
            'hot_stocks': self._get_trending_stocks(),
            'themes': self._get_market_themes()
        }
        return themes_data
    
    def _get_sector_performance(self) -> List[Dict]:
        """Get sector ETF performance as proxy for sector themes"""
        sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financial',
            'XLV': 'Healthcare', 
            'XLE': 'Energy',
            'XLI': 'Industrial',
            'XLY': 'Consumer Discretionary',
            'XLP': 'Consumer Staples',
            'XLB': 'Materials',
            'XLRE': 'Real Estate',
            'XLU': 'Utilities'
        }
        
        sector_data = []
        for etf, sector_name in sector_etfs.items():
            try:
                ticker = yf.Ticker(etf)
                hist = ticker.history(period="5d")
                if not hist.empty:
                    current = hist['Close'].iloc[-1]
                    previous = hist['Close'].iloc[0]
                    change_pct = ((current - previous) / previous) * 100
                    
                    sector_data.append({
                        'sector': sector_name,
                        'etf_symbol': etf,
                        'change_percent_5d': round(change_pct, 2),
                        'current_price': round(current, 2)
                    })
            except Exception:
                continue
        
        # Sort by performance
        sector_data.sort(key=lambda x: x['change_percent_5d'], reverse=True)
        return sector_data
    
    def _get_trending_stocks(self) -> List[Dict]:
        """Get trending/most active stocks"""
        try:
            # Yahoo Finance trending tickers
            url = "https://finance.yahoo.com/trending-tickers"
            response = self.session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            trending_stocks = []
            
            # Look for trending stocks table
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:10]:  # Get top 10
                    cells = row.find_all('td')
                    if len(cells) >= 3:
                        try:
                            symbol = cells[0].text.strip()
                            name = cells[1].text.strip() if len(cells) > 1 else symbol
                            
                            # Get additional data from yfinance
                            quote = self.get_stock_quote(symbol)
                            if quote:
                                trending_stocks.append({
                                    'symbol': symbol,
                                    'name': name,
                                    'change_percent': quote.get('change_percent', 0),
                                    'volume': quote.get('volume', 0),
                                    'source': 'yahoo_trending'
                                })
                        except Exception:
                            continue
            
            return trending_stocks
            
        except Exception as e:
            print(f"Error getting trending stocks: {e}")
            return []
    
    def _get_market_themes(self) -> List[Dict]:
        """Get current market themes"""
        # Define current market themes with representative stocks
        themes = [
            {
                'theme': 'Artificial Intelligence',
                'stocks': ['NVDA', 'AMD', 'GOOGL', 'MSFT', 'META'],
                'description': 'AI and machine learning companies'
            },
            {
                'theme': 'Electric Vehicles',
                'stocks': ['TSLA', 'RIVN', 'LCID', 'NIO', 'XPEV'],
                'description': 'Electric vehicle manufacturers and suppliers'
            },
            {
                'theme': 'Cloud Computing',
                'stocks': ['AMZN', 'MSFT', 'GOOGL', 'CRM', 'SNOW'],
                'description': 'Cloud infrastructure and services'
            },
            {
                'theme': 'Cybersecurity',
                'stocks': ['CRWD', 'ZS', 'PANW', 'OKTA', 'FTNT'],
                'description': 'Cybersecurity and data protection'
            },
            {
                'theme': 'Renewable Energy',
                'stocks': ['ENPH', 'SEDG', 'NEE', 'ICLN', 'PBW'],
                'description': 'Solar, wind, and clean energy'
            }
        ]
        
        # Calculate theme performance
        theme_performance = []
        for theme in themes:
            total_change = 0
            valid_stocks = 0
            
            for symbol in theme['stocks']:
                quote = self.get_stock_quote(symbol)
                if quote and quote.get('change_percent'):
                    total_change += quote['change_percent']
                    valid_stocks += 1
            
            if valid_stocks > 0:
                avg_change = total_change / valid_stocks
                theme_performance.append({
                    'theme': theme['theme'],
                    'description': theme['description'],
                    'avg_change_percent': round(avg_change, 2),
                    'stock_count': len(theme['stocks']),
                    'representative_stocks': theme['stocks'][:3]  # Show top 3
                })
        
        # Sort by performance
        theme_performance.sort(key=lambda x: x['avg_change_percent'], reverse=True)
        return theme_performance

def test_enhanced_yahoo():
    """Test the enhanced Yahoo Finance client"""
    print("🚀 Testing Enhanced Yahoo Finance Client")
    print("="*50)
    
    client = EnhancedYahooClient()
    
    # Test stock quote
    print("\n1. Testing stock quote...")
    quote = client.get_stock_quote('AAPL')
    if quote:
        print(f"✅ AAPL: ${quote['current_price']:.2f} ({quote['change_percent']:+.2f}%)")
    
    # Test earnings calendar
    print("\n2. Testing earnings calendar...")
    earnings = client.get_earnings_calendar()
    if earnings:
        print(f"✅ Found {len(earnings)} upcoming earnings")
        for earning in earnings[:5]:
            print(f"   📅 {earning['symbol']}: {earning['company']} - {earning['date']}")
    
    # Test investment themes
    print("\n3. Testing investment themes...")
    themes = client.get_investment_themes()
    
    if themes.get('trending_sectors'):
        print(f"✅ Top performing sectors:")
        for sector in themes['trending_sectors'][:3]:
            print(f"   📈 {sector['sector']}: {sector['change_percent_5d']:+.2f}%")
    
    if themes.get('themes'):
        print(f"✅ Market themes:")
        for theme in themes['themes'][:3]:
            print(f"   🎯 {theme['theme']}: {theme['avg_change_percent']:+.2f}%")

if __name__ == "__main__":
    test_enhanced_yahoo()