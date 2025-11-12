#!/usr/bin/env python3
"""
Gemma-Powered Advanced Market Analysis
Generates Top 10 Daily Stock Picks using AI
"""

import os
import json
from datetime import datetime
import yfinance as yf
from current_stock_summary import get_technical_analysis
from stock_universe import get_comprehensive_stock_list
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email settings
EMAIL_TO = "masterai6612@gmail.com"
EMAIL_FROM = os.getenv('EMAIL_FROM', 'masterai6612@gmail.com')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

# Try to import Gemma (optional - will use fallback if not available)
GEMMA_AVAILABLE = False
try:
    import keras_nlp
    import tensorflow as tf
    GEMMA_AVAILABLE = True
    print("✅ Gemma AI available")
except ImportError:
    print("⚠️ Gemma not available - using enhanced rule-based analysis")

class GemmaMarketAnalyst:
    """Advanced market analyst using Gemma AI"""
    
    def __init__(self):
        self.model = None
        if GEMMA_AVAILABLE and os.path.exists('models/gemma'):
            try:
                print("🤖 Loading Gemma model...")
                self.model = keras_nlp.models.GemmaCausalLM.from_preset(
                    "models/gemma",
                    dtype="float16"  # Use float16 for faster inference
                )
                print("✅ Gemma model loaded")
            except Exception as e:
                print(f"⚠️ Could not load Gemma: {e}")
                self.model = None
    
    def analyze_stock_with_ai(self, stock_data):
        """Use Gemma to provide deep analysis of a stock"""
        if not self.model:
            return self._fallback_analysis(stock_data)
        
        try:
            prompt = f"""You are an expert stock analyst. Analyze this stock and provide a brief assessment:

Stock: {stock_data['symbol']}
Current Price: ${stock_data['current_price']:.2f}
1-Week Change: {stock_data['change_1w']:+.2f}%
1-Month Change: {stock_data['change_1m']:+.2f}%
RSI: {stock_data['rsi']:.1f}
MACD: {stock_data['macd']:.3f}
Volume Ratio: {stock_data['volume_ratio']:.1f}x
Growth Potential: {stock_data.get('growth_potential', 0):.1f}%
Sector: {stock_data['sector']}

Technical Signals: {', '.join(stock_data['signals'][:3])}

Provide a 2-sentence analysis focusing on:
1. Why this is a good opportunity (or not)
2. Key risk or catalyst

Keep it concise and actionable."""

            response = self.model.generate(prompt, max_length=150)
            return response.strip()
        
        except Exception as e:
            print(f"Error with Gemma analysis: {e}")
            return self._fallback_analysis(stock_data)
    
    def _fallback_analysis(self, stock_data):
        """Rule-based analysis when Gemma is not available"""
        analysis = []
        
        # Growth analysis
        if stock_data.get('meets_growth_requirement'):
            analysis.append(f"Strong momentum with {max(stock_data['change_1w'], stock_data['change_1m']):.1f}% recent growth.")
        
        # Technical analysis
        if stock_data['rsi'] < 40:
            analysis.append("Oversold conditions suggest potential bounce.")
        elif 50 <= stock_data['rsi'] <= 70:
            analysis.append("Healthy momentum with room to run.")
        
        # Volume confirmation
        if stock_data['volume_ratio'] > 1.5:
            analysis.append("Strong volume confirms the move.")
        
        # Growth potential
        if stock_data.get('growth_potential', 0) >= 10:
            analysis.append(f"High growth potential of {stock_data['growth_potential']:.1f}%.")
        
        return " ".join(analysis[:2]) if analysis else "Technical setup looks favorable."
    
    def rank_stocks_with_ai(self, stocks_data):
        """Use AI to rank and select top 10 stocks"""
        print(f"🔍 Analyzing {len(stocks_data)} stocks with AI...")
        
        enhanced_stocks = []
        for i, stock in enumerate(stocks_data, 1):
            if i % 10 == 0:
                print(f"   Analyzed {i}/{len(stocks_data)} stocks...")
            
            # Add AI analysis
            stock['ai_analysis'] = self.analyze_stock_with_ai(stock)
            
            # Calculate AI confidence score
            stock['ai_score'] = self._calculate_ai_score(stock)
            
            enhanced_stocks.append(stock)
        
        # Sort by AI score
        enhanced_stocks.sort(key=lambda x: x['ai_score'], reverse=True)
        
        return enhanced_stocks[:10]
    
    def _calculate_ai_score(self, stock):
        """Calculate comprehensive AI score (0-100)"""
        score = 0
        
        # Base technical score (40 points)
        score += min(stock['score'] * 4, 40)
        
        # Growth requirement (20 points)
        if stock.get('meets_growth_requirement'):
            score += 20
        
        # Growth potential (15 points)
        growth_pot = stock.get('growth_potential', 0)
        score += min(growth_pot * 1.5, 15)
        
        # RSI optimization (10 points)
        rsi = stock['rsi']
        if 45 <= rsi <= 65:
            score += 10
        elif 30 <= rsi < 45:
            score += 8
        elif 65 < rsi <= 75:
            score += 5
        
        # Volume confirmation (10 points)
        if stock['volume_ratio'] > 2.0:
            score += 10
        elif stock['volume_ratio'] > 1.5:
            score += 7
        elif stock['volume_ratio'] > 1.2:
            score += 4
        
        # Sector bonus (5 points for hot sectors)
        hot_sectors = ['Technology', 'Healthcare', 'Financial Services', 'Communication Services']
        if stock['sector'] in hot_sectors:
            score += 5
        
        return min(score, 100)

def get_top_10_daily_picks():
    """Generate top 10 stock picks for the day using Gemma AI"""
    print("🚀 Gemma-Powered Daily Stock Picks")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    print()
    
    # Initialize Gemma analyst
    analyst = GemmaMarketAnalyst()
    
    # Get comprehensive stock list
    print("📊 Fetching stock universe...")
    all_symbols = get_comprehensive_stock_list()
    
    # Focus on most liquid stocks for faster analysis
    priority_symbols = [
        # US Mega caps
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
        # Large caps
        'AVGO', 'LLY', 'JPM', 'UNH', 'XOM', 'V', 'PG', 'JNJ', 'MA', 'HD',
        'CVX', 'ABBV', 'NFLX', 'BAC', 'CRM', 'KO', 'COST', 'PEP', 'MRK',
        'CSCO', 'AMD', 'INTC', 'QCOM', 'ORCL', 'ADBE', 'TXN', 'NOW',
        # Growth stocks
        'RIVN', 'LCID', 'RBLX', 'COIN', 'HOOD', 'SOFI', 'SNOW', 'CRWD',
        'PLTR', 'DKNG', 'SQ', 'SHOP', 'UBER', 'LYFT', 'ABNB', 'DASH',
        # Semiconductors
        'TSM', 'ASML', 'MU', 'AMAT', 'LRCX', 'KLAC', 'MRVL', 'ARM',
        # Healthcare
        'MRNA', 'BNTX', 'REGN', 'VRTX', 'GILD', 'BIIB', 'AMGN', 'ISRG',
        # Finance
        'GS', 'MS', 'C', 'WFC', 'SCHW', 'BLK', 'AXP', 'SPGI',
        # Energy
        'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX', 'OXY'
    ]
    
    # Analyze stocks
    print(f"🔬 Analyzing {len(priority_symbols)} priority stocks...")
    analyzed_stocks = []
    
    for i, symbol in enumerate(priority_symbols, 1):
        if i % 20 == 0:
            print(f"   Processed {i}/{len(priority_symbols)} stocks...")
        
        try:
            stock_data = get_technical_analysis(symbol)
            if stock_data and stock_data.get('meets_growth_requirement'):
                analyzed_stocks.append(stock_data)
        except Exception as e:
            continue
    
    print(f"✅ Found {len(analyzed_stocks)} stocks meeting 7% growth requirement")
    
    if not analyzed_stocks:
        print("❌ No stocks meet the 7% growth requirement today")
        return []
    
    # Use Gemma AI to rank and select top 10
    print()
    print("🤖 Applying Gemma AI analysis...")
    top_10 = analyst.rank_stocks_with_ai(analyzed_stocks)
    
    return top_10

def send_top_10_email(top_10_picks):
    """Send email with top 10 daily picks"""
    if not top_10_picks:
        print("No picks to send")
        return
    
    subject = f"🤖 Gemma AI: Top 10 Stock Picks - {datetime.now().strftime('%Y-%m-%d')}"
    
    body = f"""
🤖 GEMMA AI-POWERED DAILY STOCK PICKS
{'=' * 60}
📅 {datetime.now().strftime('%A, %B %d, %Y %I:%M %p EST')}

🎯 TOP 10 PICKS FOR TODAY
{'=' * 60}

"""
    
    for i, stock in enumerate(top_10_picks, 1):
        body += f"""
{i}. 🚀 {stock['symbol']} - AI Score: {stock['ai_score']:.0f}/100
   💰 Price: ${stock['current_price']:.2f}
   📈 Performance: 1W: {stock['change_1w']:+.2f}% | 1M: {stock['change_1m']:+.2f}%
   🎯 Technical: RSI: {stock['rsi']:.1f} | MACD: {stock['macd']:.3f}
   📊 Growth Potential: {stock.get('growth_potential', 0):.1f}% (confidence: {stock.get('growth_confidence', 0)*100:.0f}%)
   🏢 Sector: {stock['sector']}
   
   🤖 AI Analysis:
   {stock['ai_analysis']}
   
   🔍 Key Signals: {', '.join(stock['signals'][:3])}
   
"""
    
    body += f"""

📊 ANALYSIS SUMMARY
{'=' * 60}
• Total stocks analyzed: {len(top_10_picks)} meeting 7% growth requirement
• AI scoring combines: Technical analysis + Growth potential + Volume + Sector trends
• All picks have ≥7% recent growth OR ≥7% growth potential

⚠️ RISK DISCLAIMER
{'=' * 60}
This analysis is for informational purposes only. Not financial advice.
Always do your own research and consult with a financial advisor.

🤖 Powered by Gemma AI + Advanced Technical Analysis
"""
    
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = EMAIL_TO
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(EMAIL_FROM, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Email sent to {EMAIL_TO}")
        return True
    
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False

def main():
    """Main function"""
    print()
    print("🤖 GEMMA AI MARKET ANALYST")
    print("=" * 60)
    print()
    
    # Get top 10 picks
    top_10 = get_top_10_daily_picks()
    
    if top_10:
        print()
        print("🎉 TOP 10 PICKS GENERATED!")
        print("=" * 60)
        
        for i, stock in enumerate(top_10, 1):
            print(f"{i}. {stock['symbol']} - AI Score: {stock['ai_score']:.0f}/100")
        
        print()
        print("📧 Sending email...")
        send_top_10_email(top_10)
        
        # Save to file
        with open('gemma_top_10_picks.json', 'w') as f:
            json.dump({
                'date': datetime.now().isoformat(),
                'picks': top_10
            }, f, indent=2, default=str)
        
        print("💾 Saved to gemma_top_10_picks.json")
    else:
        print("❌ No qualifying stocks found today")
    
    print()
    print("✅ Analysis complete!")

if __name__ == "__main__":
    main()
