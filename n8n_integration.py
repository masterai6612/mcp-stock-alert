#!/usr/bin/env python3
"""
n8n Integration for Agentic Stock Alert System
Provides API endpoints and webhook handlers for n8n workflows
"""

import os
import json
import asyncio
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from flask import Flask, request, jsonify
from threading import Thread
import requests
import time
from dotenv import load_dotenv
from main_enhanced import fetch_stocks, make_recommendation, get_enhanced_data
from stock_universe import get_comprehensive_stock_list
from enhanced_yahoo_client import EnhancedYahooClient
from market_sentiment import MarketSentimentAnalyzer
import numpy as np
import pandas as pd

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security: Helper function to sanitize error messages
def sanitize_error(error):
    """Sanitize error messages to prevent information exposure"""
    # In production, return generic error message
    if os.getenv('FLASK_DEBUG', 'False').lower() != 'true':
        return "An error occurred while processing your request"
    # In development, return actual error for debugging
    return str(error)

# n8n Configuration
N8N_BASE_URL = "http://localhost:5678"

def make_json_serializable(obj):
    """Convert numpy/pandas types to JSON serializable types"""
    if isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(item) for item in obj]
    elif pd.isna(obj):
        return None
    else:
        return obj
N8N_AUTH = ("admin", "stockagent123")

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

class N8NStockAgent:
    def __init__(self):
        self.client = EnhancedYahooClient()
        self.symbols = get_comprehensive_stock_list()
        
    def trigger_n8n_workflow(self, workflow_name, data):
        """Trigger an n8n workflow with data"""
        try:
            webhook_url = f"{N8N_BASE_URL}/webhook/{workflow_name}"
            response = requests.post(webhook_url, json=data, timeout=30)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error triggering n8n workflow {workflow_name}: {e}")
            return None

# Initialize agent
agent = N8NStockAgent()

def send_telegram_message(message, parse_mode='Markdown'):
    """Send message to Telegram"""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Telegram credentials not configured")
        return False
    
    try:
        # Split long messages (Telegram has 4096 character limit)
        max_length = 4000  # Leave some buffer
        
        if len(message) <= max_length:
            messages = [message]
        else:
            # Split message into chunks
            messages = []
            current_msg = ""
            lines = message.split('\n')
            
            for line in lines:
                if len(current_msg + line + '\n') <= max_length:
                    current_msg += line + '\n'
                else:
                    if current_msg:
                        messages.append(current_msg.strip())
                    current_msg = line + '\n'
            
            if current_msg:
                messages.append(current_msg.strip())
        
        # Send each message part
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        for i, msg_part in enumerate(messages):
            if i > 0:
                msg_part = f"📄 *Part {i+1}/{len(messages)}*\n\n{msg_part}"
            
            payload = {
                'chat_id': TELEGRAM_CHAT_ID,
                'text': msg_part,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Telegram message sent (part {i+1}/{len(messages)})")
            else:
                print(f"❌ Telegram error (part {i+1}): {response.status_code} - {response.text}")
                return False
            
            # Small delay between parts
            if len(messages) > 1 and i < len(messages) - 1:
                time.sleep(1)
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending Telegram message: {e}")
        return False

def convert_html_to_telegram(html_content, subject):
    """Convert HTML email content to Telegram Markdown format"""
    try:
        # Start with subject as header
        telegram_msg = f"*{subject}*\n\n"
        
        # Extract key information from HTML
        lines = html_content.split('\n')
        in_table = False
        table_data = []
        
        for line in lines:
            line = line.strip()
            
            # Skip HTML tags and empty lines
            if not line or line.startswith('<') or line.startswith('</'):
                continue
            
            # Process content
            if 'Analysis Summary' in line:
                telegram_msg += "*📊 Analysis Summary*\n"
            elif 'X (Twitter) Sentiment Analysis' in line:
                telegram_msg += "*🐦 X Sentiment Analysis*\n"
            elif 'BUY SIGNALS' in line:
                telegram_msg += "*🚀 BUY SIGNALS*\n"
            elif 'Market Sentiment:' in line:
                telegram_msg += f"📈 {line}\n"
            elif 'Stocks Analyzed:' in line:
                telegram_msg += f"📊 {line}\n"
            elif 'Earnings Today:' in line:
                telegram_msg += f"📅 {line}\n"
            elif 'Bullish X Sentiment:' in line:
                telegram_msg += f"📈 {line}\n"
            elif 'Bearish X Sentiment:' in line:
                telegram_msg += f"📉 {line}\n"
            elif 'Neutral X Sentiment:' in line:
                telegram_msg += f"😐 {line}\n"
            elif line and not any(skip in line.lower() for skip in ['html', 'body', 'style', 'table', 'tr', 'td', 'th']):
                telegram_msg += f"{line}\n"
        
        # Add footer
        telegram_msg += "\n🤖 *Generated by Agentic Stock Alert System*\n"
        telegram_msg += "📊 Dashboard: http://localhost:5001\n"
        telegram_msg += "🔧 n8n Workflows: http://localhost:5678"
        
        return telegram_msg
        
    except Exception as e:
        print(f"❌ Error converting HTML to Telegram: {e}")
        return f"*{subject}*\n\nError formatting message. Please check email for details."

def send_gmail_email(to_email, subject, html_body):
    """Send email using Gmail SMTP"""
    try:
        # Email configuration
        from_email = os.getenv('EMAIL_FROM', 'masterai6612@gmail.com')
        password = os.getenv('EMAIL_PASSWORD', '')
        
        if not password:
            print("⚠️ Warning: EMAIL_PASSWORD not set in .env file")
            return False
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add HTML content
        html_part = MIMEText(html_body, 'html')
        msg.attach(html_part)
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent successfully to {to_email}")
        
        # Also send to Telegram
        telegram_msg = convert_html_to_telegram(html_body, subject)
        telegram_success = send_telegram_message(telegram_msg)
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False

# API Endpoints for n8n

@app.route('/api/quick-analysis', methods=['GET', 'POST'])
def quick_analysis():
    """Quick analysis with reduced features for faster processing"""
    try:
        data = request.get_json() or {}
        stock_limit = min(data.get('stock_limit', 50), 100)  # Cap at 100 for speed
        
        print(f"🚀 Starting quick analysis: {stock_limit} stocks")
        
        # Get stock universe
        from stock_universe import get_comprehensive_stock_list
        all_stocks = get_comprehensive_stock_list()
        symbols_to_analyze = all_stocks[:stock_limit]
        
        # Quick analysis without sentiment (faster)
        results = []
        for symbol in symbols_to_analyze[:stock_limit]:
            try:
                stock_data = fetch_stocks([symbol], include_sentiment=False)
                if symbol in stock_data:
                    info = stock_data[symbol]
                    
                    # Quick result with essential data only
                    result = {
                        'symbol': symbol,
                        'price': float(info.get('current_price', 0)),
                        'change_percent': float(info.get('change_percent', 0)),
                        'rsi': float(info.get('rsi', 0)),
                        'technical_score': make_json_serializable(info.get('technical_score', 0)),
                        'recommendation': 'BUY' if info.get('technical_score', 0) >= 70 else 'WATCH' if info.get('technical_score', 0) >= 50 else 'NO SIGNAL',
                        'timestamp': datetime.now().isoformat()
                    }
                    results.append(result)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': results,
            'total_analyzed': len(results),
            'analysis_type': 'quick',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Quick analysis error: {e}")
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/comprehensive-analysis', methods=['GET', 'POST'])
def comprehensive_analysis():
    """Comprehensive analysis using all our sophisticated features"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            # Use default parameters for GET requests
            analysis_type = 'full_universe'
            include_earnings = True
            include_themes = True
            include_sentiment = True
            stock_limit = 269  # Full universe for GET requests
            print("⚠️ Warning: Received GET request, using full universe parameters")
        else:
            # POST request with JSON data
            data = request.get_json() or {}
            analysis_type = data.get('analysis_type', 'full_universe')
            include_earnings = data.get('include_earnings', True)
            include_themes = data.get('include_themes', True)
            include_sentiment = data.get('include_sentiment', True)
            stock_limit = data.get('stock_limit', 269)  # Default to full universe
        
        print(f"🚀 Starting comprehensive analysis: {analysis_type}")
        
        # Get enhanced data (earnings, themes)
        earnings_symbols, hot_theme_stocks, themes = get_enhanced_data()
        
        # Select stocks to analyze
        if analysis_type == 'full_universe':
            symbols_to_analyze = agent.symbols[:stock_limit]
        else:
            symbols_to_analyze = data.get('symbols', agent.symbols[:50])
        
        print(f"📊 Analyzing {len(symbols_to_analyze)} stocks")
        
        # Initialize sentiment analyzer
        sentiment_analyzer = MarketSentimentAnalyzer() if include_sentiment else None
        
        # Get market-wide sentiment indicators
        market_sentiment = sentiment_analyzer.get_market_fear_greed_index() if sentiment_analyzer else {}
        
        # Perform comprehensive analysis with enhanced sentiment
        results = []
        sentiment_batch = {}
        
        # Get sentiment for all symbols in batch (more efficient)
        if sentiment_analyzer and len(symbols_to_analyze) > 0:
            print("🔍 Analyzing market sentiment from multiple sources...")
            sentiment_batch = sentiment_analyzer.analyze_market_sentiment_batch(symbols_to_analyze, max_symbols=100)
        
        for symbol in symbols_to_analyze:
            try:
                # Get stock data using our enhanced system
                stock_data = fetch_stocks([symbol], include_sentiment=False)  # We'll add our own sentiment
                if symbol in stock_data:
                    info = stock_data[symbol]
                    
                    # Add comprehensive sentiment analysis
                    if symbol in sentiment_batch:
                        sentiment_data = sentiment_batch[symbol]
                        info['sentiment_analysis'] = sentiment_data
                        info['sentiment_score'] = sentiment_data['composite_sentiment']
                        info['sentiment_category'] = sentiment_data['sentiment_category']
                        info['sentiment_confidence'] = sentiment_data['confidence']
                    else:
                        info['sentiment_analysis'] = None
                        info['sentiment_score'] = 0
                        info['sentiment_category'] = 'neutral'
                        info['sentiment_confidence'] = 0
                    
                    # Check if stock has upcoming earnings
                    earnings_soon = symbol in earnings_symbols if include_earnings else False
                    
                    # Check if stock is in hot themes
                    in_hot_theme = symbol in hot_theme_stocks if include_themes else False
                    
                    # Get enhanced recommendation with sentiment
                    recommendation = make_recommendation(
                        info, [], "Neutral", 
                        earnings_soon=earnings_soon, 
                        in_hot_theme=in_hot_theme
                    )
                    
                    # Handle NaN values
                    rsi_val = info.get('rsi', 0)
                    if math.isnan(rsi_val) if isinstance(rsi_val, float) else False:
                        rsi_val = 0
                    
                    # Create comprehensive result with all technical analysis data
                    result = {
                        'symbol': symbol,
                        'price': float(info.get('current_price', 0)) if info.get('current_price') else 0,
                        'change_percent': float(info.get('change_percent', 0)) if info.get('change_percent') else 0,
                        'volume': int(info.get('volume', 0)) if info.get('volume') else 0,
                        'rsi': float(rsi_val) if rsi_val else 0,
                        'recommendation': str(recommendation) if recommendation else 'NO SIGNAL',
                        'earnings_soon': earnings_soon,
                        'in_hot_theme': in_hot_theme,
                        'x_sentiment': info.get('x_sentiment', 'Unknown'),
                        'social_sentiment': info.get('x_sentiment', 'Unknown'),
                        'timestamp': datetime.now().isoformat(),
                        
                        # COMPREHENSIVE TECHNICAL ANALYSIS DATA
                        'technical_score': make_json_serializable(info.get('technical_score', 0)),
                        'technical_signals': make_json_serializable(info.get('technical_signals', [])),
                        'macd': make_json_serializable(info.get('macd', {})),
                        'bollinger': make_json_serializable(info.get('bollinger', {})),
                        'moving_averages': make_json_serializable(info.get('moving_averages', {})),
                        'volume_analysis': make_json_serializable(info.get('volume_analysis', {})),
                        'momentum': make_json_serializable(info.get('momentum', {})),
                        
                        # SENTIMENT ANALYSIS DATA
                        'sentiment_analysis': make_json_serializable(info.get('sentiment_analysis', {})),
                        'sentiment_score': make_json_serializable(info.get('sentiment_score', 0)),
                        'sentiment_category': info.get('sentiment_category', 'neutral'),
                        'sentiment_confidence': make_json_serializable(info.get('sentiment_confidence', 0)),
                        
                        # ADDITIONAL PRICE DATA
                        'open': float(info.get('open', 0)) if info.get('open') else 0,
                        'high': float(info.get('high', 0)) if info.get('high') else 0,
                        'low': float(info.get('low', 0)) if info.get('low') else 0,
                        'daily_range': float(info.get('daily_range', 0)) if info.get('daily_range') else 0,
                        'support_level': float(info.get('support_level', 0)) if info.get('support_level') else 0,
                        'resistance_level': float(info.get('resistance_level', 0)) if info.get('resistance_level') else 0,
                        'price_near_support': bool(info.get('price_near_support', False)),
                        'price_near_resistance': bool(info.get('price_near_resistance', False))
                    }
                    
                    results.append(result)
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        # Create market context
        market_context = {
            'earnings_today': len(earnings_symbols),
            'hot_themes': len(themes.get('themes', [])) if themes else 0,
            'total_universe': len(agent.symbols),
            'sentiment': 'BULLISH' if len([r for r in results if 'BUY' in r['recommendation']]) > len(results) * 0.3 else 'NEUTRAL'
        }
        
        print(f"✅ Analysis complete: {len(results)} stocks analyzed")
        
        return jsonify({
            'success': True,
            'data': results,
            'total_analyzed': len(results),
            'market_context': market_context,
            'earnings_symbols': list(earnings_symbols)[:10],  # Sample
            'hot_theme_stocks': list(hot_theme_stocks)[:10],  # Sample
            'themes_summary': themes.get('themes', [])[:3] if themes else [],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Comprehensive analysis error: {e}")
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/stock-analysis', methods=['POST'])
def stock_analysis():
    """Legacy endpoint for basic stock analysis"""
    try:
        data = request.get_json()
        symbols = data.get('symbols', agent.symbols[:20])  # Smaller limit for basic analysis
        
        # Perform basic analysis
        results = []
        for symbol in symbols:
            try:
                # Get stock data
                stock_data = fetch_stocks([symbol])
                if symbol in stock_data:
                    info = stock_data[symbol]
                    
                    # Get recommendation
                    recommendation = make_recommendation(
                        info, [], "Neutral", 
                        earnings_soon=False, 
                        in_hot_theme=False
                    )
                    
                    # Handle NaN values
                    rsi_val = info.get('rsi', 0)
                    if math.isnan(rsi_val) if isinstance(rsi_val, float) else False:
                        rsi_val = 0
                    
                    results.append({
                        'symbol': symbol,
                        'price': float(info.get('current_price', 0)) if info.get('current_price') else 0,
                        'change_percent': float(info.get('change_percent', 0)) if info.get('change_percent') else 0,
                        'volume': int(info.get('volume', 0)) if info.get('volume') else 0,
                        'rsi': float(rsi_val) if rsi_val else 0,
                        'recommendation': str(recommendation) if recommendation else 'NO SIGNAL',
                        'timestamp': datetime.now().isoformat()
                    })
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'data': results,
            'total_analyzed': len(results),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/market-data', methods=['GET'])
def market_data():
    """Get current market data for n8n workflows"""
    try:
        # Get market indices
        indices = ['SPY', 'QQQ', 'DIA', 'IWM']
        market_data = {}
        
        for index in indices:
            try:
                quote = agent.client.get_stock_quote(index)
                if quote:
                    market_data[index] = {
                        'price': float(quote.get('regularMarketPrice', 0)) if quote.get('regularMarketPrice') else 0,
                        'change': float(quote.get('regularMarketChange', 0)) if quote.get('regularMarketChange') else 0,
                        'change_percent': float(quote.get('regularMarketChangePercent', 0)) if quote.get('regularMarketChangePercent') else 0
                    }
            except Exception as e:
                print(f"Error getting data for {index}: {e}")
        
        # Get enhanced data
        earnings_symbols, hot_theme_stocks, themes = get_enhanced_data()
        
        return jsonify({
            'success': True,
            'market_indices': market_data,
            'earnings_today': len(earnings_symbols),
            'hot_themes': len(themes.get('themes', [])) if themes else 0,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    """Create alert and trigger n8n notification workflow"""
    try:
        data = request.get_json()
        
        # Trigger n8n alert workflow
        workflow_data = {
            'alert_type': data.get('type', 'STOCK_ALERT'),
            'symbol': data.get('symbol'),
            'message': data.get('message'),
            'priority': data.get('priority', 'MEDIUM'),
            'timestamp': datetime.now().isoformat()
        }
        
        # Trigger n8n workflow
        result = agent.trigger_n8n_workflow('stock-alert', workflow_data)
        
        return jsonify({
            'success': True,
            'alert_sent': result is not None,
            'workflow_result': result
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def portfolio_status():
    """Get portfolio status for n8n workflows"""
    try:
        # This would integrate with your actual portfolio data
        # For now, return mock data structure
        portfolio_data = {
            'total_value': 100000,  # Mock value
            'daily_change': 1250,
            'daily_change_percent': 1.25,
            'positions': [
                {'symbol': 'AAPL', 'shares': 100, 'value': 15000},
                {'symbol': 'NVDA', 'shares': 50, 'value': 12000},
                # Add more positions as needed
            ],
            'cash': 25000,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'portfolio': portfolio_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/send-telegram-alert', methods=['POST'])
def send_telegram_alert():
    """Send alert directly to Telegram (for n8n workflows)"""
    try:
        data = request.get_json() or {}
        
        # Extract alert data
        message = data.get('message', '')
        subject = data.get('subject', 'Stock Alert')
        buy_signals = data.get('buy_signals', [])
        
        if not message and not buy_signals:
            return jsonify({'success': False, 'error': 'No message or signals provided'})
        
        # Create Telegram message
        if message:
            # Use provided message
            telegram_msg = f"*{subject}*\n\n{message}"
        else:
            # Create message from buy signals
            telegram_msg = f"*{subject}*\n\n"
            telegram_msg += f"🚀 *{len(buy_signals)} BUY SIGNALS DETECTED*\n\n"
            
            for i, signal in enumerate(buy_signals[:10], 1):  # Top 10
                x_sentiment = signal.get('x_sentiment', 'Unknown')
                sentiment_emoji = '📈' if x_sentiment == 'Bullish' else '📉' if x_sentiment == 'Bearish' else '😐'
                
                telegram_msg += f"`{i}. {signal['symbol']}` - ${signal['price']:.2f}\n"
                telegram_msg += f"   📊 {signal['recommendation']} | RSI: {signal['rsi']:.1f}\n"
                telegram_msg += f"   🐦 {sentiment_emoji} {x_sentiment} | {signal['change_percent']:+.2f}%\n\n"
            
            if len(buy_signals) > 10:
                remaining = [s['symbol'] for s in buy_signals[10:]]
                telegram_msg += f"📋 *Additional signals:* {', '.join(remaining)}\n\n"
            
            telegram_msg += "🤖 *n8n Workflow Alert*"
        
        # Send to Telegram
        success = send_telegram_message(telegram_msg)
        
        return jsonify({
            'success': success,
            'message': 'Telegram alert sent' if success else 'Failed to send Telegram alert',
            'signals_count': len(buy_signals) if buy_signals else 0
        })
        
    except Exception as e:
        print(f"❌ Telegram alert error: {e}")
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/send-email-alert', methods=['GET', 'POST'])
def send_email_alert():
    """Send comprehensive email alerts using our enhanced system"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            # Use default test data for GET requests
            print("⚠️ Warning: Received GET request for email alert, using test data")
            buy_signals = [
                {
                    'symbol': 'TEST',
                    'price': 100.0,
                    'recommendation': 'BUY',
                    'change_percent': 5.0,
                    'rsi': 65.0,
                    'earnings_soon': False,
                    'in_hot_theme': True
                }
            ]
            market_context = {'sentiment': 'BULLISH', 'earnings_today': 3, 'hot_themes': 2}
            summary = {'total_analyzed': 50, 'timestamp': 'Test timestamp'}
            custom_subject = ''
            email_to = 'masterai6612@gmail.com'
        else:
            # POST request with JSON data
            data = request.get_json() or {}
            
            # Extract alert data
            buy_signals = data.get('buy_signals', [])
            market_context = data.get('market_context', {})
            summary = data.get('summary', {})
            
            # Extract subject from n8n or create default
            custom_subject = data.get('subject', '')
            email_to = data.get('email_to', 'masterai6612@gmail.com')
        
        if not buy_signals:
            return jsonify({'success': True, 'message': 'No alerts to send'})
        
        # Create email subject
        if custom_subject:
            subject = custom_subject
        else:
            # Calculate X sentiment for subject enhancement
            bullish_x_count = len([s for s in buy_signals if s.get('x_sentiment') == 'Bullish'])
            bearish_x_count = len([s for s in buy_signals if s.get('x_sentiment') == 'Bearish'])
            
            # Default subject with market context and X sentiment
            market_sentiment = market_context.get('sentiment', 'NEUTRAL')
            
            if bullish_x_count >= 3:
                subject = f"🐦🚀 X BULLISH: {bullish_x_count} Stocks + {len(buy_signals)} BUY Signals!"
            elif bullish_x_count > bearish_x_count and bullish_x_count >= 2:
                subject = f"🐦📈 Strong X Sentiment: {len(buy_signals)} BUY Signals ({bullish_x_count} Bullish)"
            else:
                subject = f"🚨 {market_sentiment} Market: {len(buy_signals)} BUY Signals Detected"
        
        # Create enhanced email content with custom styling
        timestamp = summary.get('timestamp', 'Unknown')
        total_analyzed = summary.get('total_analyzed', 0)
        sentiment = market_context.get('sentiment', 'NEUTRAL')
        earnings_today = market_context.get('earnings_today', 0)
        hot_themes = market_context.get('hot_themes', 0)
        
        email_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #1f2937; color: white; padding: 20px; border-radius: 8px; }}
                .summary {{ background-color: #f3f4f6; padding: 15px; border-radius: 8px; margin: 15px 0; }}
                .signals-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .signals-table th {{ background-color: #374151; color: white; padding: 12px; text-align: left; }}
                .signals-table td {{ padding: 10px; border-bottom: 1px solid #e5e7eb; }}
                .buy-signal {{ background-color: #dcfce7; }}
                .strong-buy {{ background-color: #bbf7d0; font-weight: bold; }}
                .bullish-sentiment {{ background-color: #d1fae5; border-left: 4px solid #059669; }}
                .footer {{ margin-top: 30px; padding: 15px; background-color: #f9fafb; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 Agentic Stock Alert System</h2>
                <p>Intelligent Trading Recommendations</p>
            </div>
            
            <div class="summary">
                <h3>📊 Analysis Summary</h3>
                <p><strong>Analysis Time:</strong> {timestamp}</p>
                <p><strong>Market Sentiment:</strong> <span style="color: {'#059669' if sentiment == 'BULLISH' else '#dc2626' if sentiment == 'BEARISH' else '#6b7280'};">{sentiment}</span></p>
                <p><strong>Stocks Analyzed:</strong> {total_analyzed}</p>
                <p><strong>Earnings Today:</strong> {earnings_today}</p>
                <p><strong>Hot Themes:</strong> {hot_themes}</p>
            </div>
            
            <div class="summary">
                <h3>🐦 X (Twitter) Sentiment Analysis</h3>"""
        
        # Calculate X sentiment distribution
        bullish_count = len([s for s in buy_signals if s.get('x_sentiment') == 'Bullish'])
        bearish_count = len([s for s in buy_signals if s.get('x_sentiment') == 'Bearish'])
        neutral_count = len([s for s in buy_signals if s.get('x_sentiment') == 'Neutral'])
        
        email_body += f"""
                <p><strong>📈 Bullish X Sentiment:</strong> {bullish_count} stocks</p>
                <p><strong>📉 Bearish X Sentiment:</strong> {bearish_count} stocks</p>
                <p><strong>😐 Neutral X Sentiment:</strong> {neutral_count} stocks</p>
                <p><strong>🎯 Social Media Mood:</strong> <span style="color: {'#059669' if bullish_count > bearish_count else '#dc2626' if bearish_count > bullish_count else '#6b7280'};">
                    {'BULLISH' if bullish_count > bearish_count else 'BEARISH' if bearish_count > bullish_count else 'NEUTRAL'} on X (Twitter)
                </span></p>
            </div>
            
            <h3>🔥 BUY SIGNALS ({len(buy_signals)})</h3>
            <table class="signals-table">
                <tr>
                    <th>Symbol</th><th>Price</th><th>Change %</th><th>RSI</th><th>🐦 X Sentiment</th><th>Recommendation</th><th>Special Flags</th>
                </tr>
        """
        
        for signal in buy_signals[:15]:  # Show top 15 signals
            special_flags = []
            if signal.get('earnings_soon'):
                special_flags.append('📅 Earnings')
            if signal.get('in_hot_theme'):
                special_flags.append('🔥 Hot Theme')
            
            special_text = ', '.join(special_flags) if special_flags else '-'
            
            # Style based on recommendation strength
            row_class = 'strong-buy' if signal['recommendation'] == 'STRONG BUY' else 'buy-signal'
            change_color = '#059669' if signal['change_percent'] > 0 else '#dc2626'
            
            # X sentiment styling
            x_sentiment = signal.get('x_sentiment', 'Unknown')
            if x_sentiment == 'Bullish':
                x_sentiment_display = '<span style="color: #059669; font-weight: bold;">🐦📈 Bullish</span>'
                row_class += ' bullish-sentiment'  # Extra highlighting for bullish sentiment
            elif x_sentiment == 'Bearish':
                x_sentiment_display = '<span style="color: #dc2626; font-weight: bold;">🐦📉 Bearish</span>'
            elif x_sentiment == 'Neutral':
                x_sentiment_display = '<span style="color: #6b7280;">🐦😐 Neutral</span>'
            else:
                x_sentiment_display = '<span style="color: #9ca3af;">🐦❓ Unknown</span>'
            
            email_body += f"""
                <tr class="{row_class}">
                    <td><strong>{signal['symbol']}</strong></td>
                    <td>${signal['price']:.2f}</td>
                    <td style="color: {change_color};">{signal['change_percent']:+.2f}%</td>
                    <td>{signal['rsi']:.1f}</td>
                    <td>{x_sentiment_display}</td>
                    <td><strong>{signal['recommendation']}</strong></td>
                    <td>{special_text}</td>
                </tr>
            """
        
        email_body += """
            </table>
        """
        
        # Add dividend stocks section
        try:
            import json
            import os
            if os.path.exists('top_50_dividend_stocks.json'):
                with open('top_50_dividend_stocks.json', 'r') as f:
                    dividend_data = json.load(f)
                
                top_dividends = dividend_data.get('top_50_dividend_stocks', [])[:5]
                
                if top_dividends:
                    email_body += """
            <div class="summary">
                <h3>💰 Top Dividend Stocks (Income + Growth)</h3>
                <table class="signals-table">
                    <tr>
                        <th>Symbol</th><th>Company</th><th>Price</th><th>Yield</th><th>1M Growth</th><th>Score</th><th>Category</th>
                    </tr>
                    """
                    
                    for stock in top_dividends:
                        growth_color = '#059669' if stock['change_1m'] > 0 else '#dc2626'
                        email_body += f"""
                    <tr>
                        <td><strong>{stock['symbol']}</strong></td>
                        <td>{stock.get('company_name', stock['symbol'])[:25]}</td>
                        <td>${stock['current_price']:.2f}</td>
                        <td><strong>{stock['dividend_yield']:.2f}%</strong></td>
                        <td style="color: {growth_color};">{stock['change_1m']:+.2f}%</td>
                        <td>{stock['dividend_score']:.0f}/100</td>
                        <td>{stock.get('category', 'Dividend')}</td>
                    </tr>
                        """
                    
                    email_body += f"""
                </table>
                <p><em>📊 Total dividend stocks analyzed: {dividend_data.get('total_dividend_stocks', 0)} | 
                Last updated: {dividend_data.get('generated_at', 'N/A')[:10]}</em></p>
            </div>
                    """
        except Exception as e:
            print(f"⚠️ Could not load dividend data: {e}")
        
        email_body += """
            
            <div class="footer">
                <p><strong>🤖 Generated by your Agentic Stock Alert System</strong></p>
                <p>📊 <a href="http://localhost:5001">View Live Dashboard</a> | 
                   🔧 <a href="http://localhost:5678">Manage Workflows</a></p>
                <p><em>This is an automated alert based on comprehensive market analysis including earnings calendar, investment themes, technical indicators, and dividend analysis.</em></p>
            </div>
        </body>
        </html>
        """
        
        # Actually send the email using Gmail SMTP (also sends to Telegram)
        email_sent = send_gmail_email(email_to, subject, email_body)
        
        print(f"📧 Email alert prepared: {subject}")
        print(f"📊 Buy signals: {len(buy_signals)}")
        print(f"📬 Email sent: {'✅ Success' if email_sent else '❌ Failed'}")
        print(f"📱 Telegram: {'✅ Also sent' if email_sent else '❌ Failed'}")
        
        return jsonify({
            'success': True, 
            'message': f'Dual alert (Email + Telegram) sent for {len(buy_signals)} buy signals',
            'subject': subject,
            'email_to': email_to,
            'telegram_chat_id': TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else 'Not configured',
            'signals_count': len(buy_signals),
            'market_sentiment': sentiment,
            'html_preview': email_body[:200] + "..." if len(email_body) > 200 else email_body
        })
        
    except Exception as e:
        print(f"❌ Email alert error: {e}")
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/webhook/market-update', methods=['POST'])
def market_update_webhook():
    """Webhook for n8n to send market updates"""
    try:
        data = request.get_json()
        
        # Process market update from n8n
        print(f"Received market update from n8n: {data}")
        
        # You can add logic here to process the update
        # For example, trigger additional analysis or alerts
        
        return jsonify({'success': True, 'message': 'Market update processed'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/telegram-config', methods=['GET'])
def telegram_config():
    """Check Telegram configuration for n8n workflows"""
    try:
        bot_configured = bool(TELEGRAM_BOT_TOKEN)
        chat_configured = bool(TELEGRAM_CHAT_ID)
        
        # Test Telegram connection if configured
        telegram_status = 'not_configured'
        if bot_configured and chat_configured:
            try:
                # Test with a simple API call
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    telegram_status = 'connected'
                else:
                    telegram_status = 'error'
            except:
                telegram_status = 'connection_failed'
        
        return jsonify({
            'success': True,
            'telegram_configured': bot_configured and chat_configured,
            'bot_token_set': bot_configured,
            'chat_id_set': chat_configured,
            'chat_id': TELEGRAM_CHAT_ID if chat_configured else None,
            'status': telegram_status,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/api/test-telegram', methods=['POST'])
def test_telegram():
    """Test Telegram notification for n8n workflows"""
    try:
        data = request.get_json() or {}
        test_message = data.get('message', '🧪 *Test Alert from n8n Workflow*\n\nThis is a test notification to verify Telegram integration is working correctly.\n\n🤖 Sent via n8n API')
        
        success = send_telegram_message(test_message)
        
        return jsonify({
            'success': success,
            'message': 'Test message sent to Telegram' if success else 'Failed to send test message',
            'chat_id': TELEGRAM_CHAT_ID if TELEGRAM_CHAT_ID else 'Not configured'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': sanitize_error(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for n8n monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'stock_analysis': True,
            'market_data': True,
            'alerts': True,
            'telegram': bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
        }
    })

if __name__ == '__main__':
    print("🚀 Starting n8n Stock Agent Integration Server with Telegram Support")
    print("📊 Available endpoints:")
    print("   POST /api/comprehensive-analysis - Full sophisticated analysis")
    print("   POST /api/stock-analysis - Basic stock analysis")
    print("   POST /api/send-email-alert - Enhanced email alerts (+ Telegram)")
    print("   POST /api/send-telegram-alert - Direct Telegram notifications")
    print("   GET  /api/telegram-config - Check Telegram configuration")
    print("   POST /api/test-telegram - Test Telegram notifications")
    print("   GET  /api/market-data - Get market data")
    print("   POST /api/alerts - Create alerts")
    print("   GET  /api/portfolio - Get portfolio status")
    print("   POST /webhook/market-update - Market update webhook")
    print("   GET  /health - Health check")
    print()
    
    # Check Telegram configuration on startup
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        print("📱 Telegram Integration: ✅ CONFIGURED")
        print(f"   Chat ID: {TELEGRAM_CHAT_ID}")
        print("   All email alerts will also be sent to Telegram")
    else:
        print("📱 Telegram Integration: ❌ NOT CONFIGURED")
        print("   Only email alerts will be sent")
    
    print()
    print("🔗 n8n Integration Server running on http://localhost:5002")
    
    # Use debug=False in production for security
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5002, debug=debug_mode)