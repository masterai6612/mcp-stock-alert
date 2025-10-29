#!/usr/bin/env python3
"""
Create a workflow that showcases X (Twitter) sentiment analysis
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_x_sentiment_workflow():
    """Create a workflow that highlights X sentiment analysis"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "X (Twitter) Sentiment Analysis - Enhanced",
        "nodes": [
            {
                "parameters": {},
                "name": "Manual Trigger",
                "type": "n8n-nodes-base.manualTrigger",
                "typeVersion": 1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": "http://host.docker.internal:5002/api/comprehensive-analysis",
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"include_earnings\": true,\n  \"include_themes\": true,\n  \"include_sentiment\": true,\n  \"stock_limit\": 30\n}",
                    "options": {
                        "timeout": 60000
                    }
                },
                "name": "Get Stocks with X Sentiment",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const stocks = data.data || [];\n  \n  // Analyze X sentiment distribution\n  const bullishStocks = stocks.filter(s => s.x_sentiment === 'Bullish');\n  const bearishStocks = stocks.filter(s => s.x_sentiment === 'Bearish');\n  const neutralStocks = stocks.filter(s => s.x_sentiment === 'Neutral');\n  const unknownStocks = stocks.filter(s => s.x_sentiment === 'Unknown');\n  \n  // Find stocks with strong X sentiment + buy signals\n  const bullishBuySignals = stocks.filter(s => \n    s.x_sentiment === 'Bullish' && \n    (s.recommendation === 'BUY' || s.recommendation === 'STRONG BUY')\n  );\n  \n  // Create X sentiment summary\n  const xSentimentSummary = {\n    total_analyzed: stocks.length,\n    bullish_count: bullishStocks.length,\n    bearish_count: bearishStocks.length,\n    neutral_count: neutralStocks.length,\n    unknown_count: unknownStocks.length,\n    bullish_with_buy_signals: bullishBuySignals.length\n  };\n  \n  // Create email subject highlighting X sentiment\n  let subject = '';\n  if (bullishBuySignals.length >= 3) {\n    subject = `🐦🚀 TWITTER BULLISH: ${bullishBuySignals.length} Stocks with Bullish X Sentiment + Buy Signals!`;\n  } else if (bullishStocks.length >= 10) {\n    subject = `🐦📈 Strong Social Sentiment: ${bullishStocks.length} Bullish vs ${bearishStocks.length} Bearish on X`;\n  } else if (bullishStocks.length > bearishStocks.length) {\n    subject = `🐦💡 X Sentiment Positive: ${bullishStocks.length} Bullish, ${bearishStocks.length} Bearish`;\n  } else {\n    subject = `🐦📊 X Sentiment Analysis: ${bullishStocks.length}B/${bearishStocks.length}B/${neutralStocks.length}N`;\n  }\n  \n  console.log('🐦 X (Twitter) Sentiment Analysis Results:');\n  console.log(`📊 Total stocks analyzed: ${stocks.length}`);\n  console.log(`📈 Bullish sentiment: ${bullishStocks.length}`);\n  console.log(`📉 Bearish sentiment: ${bearishStocks.length}`);\n  console.log(`😐 Neutral sentiment: ${neutralStocks.length}`);\n  console.log(`❓ Unknown sentiment: ${unknownStocks.length}`);\n  console.log(`🎯 Bullish + Buy signals: ${bullishBuySignals.length}`);\n  \n  // Show top bullish stocks\n  if (bullishStocks.length > 0) {\n    console.log('🐦📈 Top Bullish X Sentiment Stocks:');\n    bullishStocks.slice(0, 5).forEach(stock => {\n      console.log(`  ${stock.symbol}: ${stock.recommendation} (${stock.change_percent.toFixed(2)}%)`);\n    });\n  }\n  \n  // Show bullish buy signals\n  if (bullishBuySignals.length > 0) {\n    console.log('🐦🚀 Bullish X Sentiment + Buy Signals:');\n    bullishBuySignals.forEach(stock => {\n      console.log(`  ${stock.symbol}: ${stock.recommendation} at $${stock.price} (${stock.change_percent.toFixed(2)}%)`);\n    });\n  }\n  \n  return [{\n    json: {\n      subject: subject,\n      email_to: 'masterai6612@gmail.com',\n      buy_signals: bullishBuySignals,\n      x_sentiment_summary: xSentimentSummary,\n      bullish_stocks: bullishStocks.slice(0, 10),\n      bearish_stocks: bearishStocks.slice(0, 5),\n      market_context: data.market_context,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString(),\n        x_sentiment_enabled: true\n      }\n    }\n  }];\n} else {\n  console.log('❌ X sentiment analysis failed');\n  return [{\n    json: {\n      subject: '❌ X Sentiment Analysis Failed',\n      email_to: 'masterai6612@gmail.com',\n      error: data.error\n    }\n  }];\n}"
                },
                "name": "Analyze X Sentiment Results",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "url": "http://host.docker.internal:5002/api/send-email-alert",
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonBody": "={{ JSON.stringify($json) }}",
                    "options": {
                        "timeout": 15000
                    }
                },
                "name": "Send X Sentiment Email",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [900, 300]
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [
                    [
                        {
                            "node": "Get Stocks with X Sentiment",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Stocks with X Sentiment": {
                "main": [
                    [
                        {
                            "node": "Analyze X Sentiment Results",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Analyze X Sentiment Results": {
                "main": [
                    [
                        {
                            "node": "Send X Sentiment Email",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "settings": {
            "executionOrder": "v1"
        }
    }
    
    try:
        headers = {
            "Content-Type": "application/json",
            "X-N8N-API-KEY": API_KEY
        }
        
        response = requests.post(
            f"{N8N_URL}/api/v1/workflows",
            json=workflow_data,
            headers=headers
        )
        
        if response.status_code == 200:
            workflow_id = response.json().get('id')
            print(f"✅ X Sentiment Analysis workflow created!")
            print(f"🔗 Link: http://localhost:5678/workflow/{workflow_id}")
            print()
            print("🐦 This workflow showcases:")
            print("   • X (Twitter) sentiment analysis for 30 stocks")
            print("   • Bullish vs Bearish sentiment distribution")
            print("   • Stocks with Bullish X sentiment + Buy signals")
            print("   • Enhanced email with X sentiment insights")
            print("   • Real-time social media sentiment integration")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("🐦 Creating X (Twitter) Sentiment Analysis Workflow...")
    create_x_sentiment_workflow()