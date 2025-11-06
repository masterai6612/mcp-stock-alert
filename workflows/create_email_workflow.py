#!/usr/bin/env python3
"""
Create a workflow with enhanced email alerts including custom subject
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_email_alert_workflow():
    """Create a workflow that sends enhanced email alerts"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "Enhanced Email Alert System",
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
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"include_earnings\": true,\n  \"include_themes\": true,\n  \"include_sentiment\": true,\n  \"stock_limit\": 100\n}",
                    "options": {
                        "timeout": 120000
                    }
                },
                "name": "Get Stock Analysis",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  const marketContext = data.market_context || {};\n  const sentiment = marketContext.sentiment || 'NEUTRAL';\n  const earningsToday = marketContext.earnings_today || 0;\n  const hotThemes = marketContext.hot_themes || 0;\n  \n  // Create custom subject based on market conditions\n  let subject = '';\n  if (buySignals.length >= 10) {\n    subject = `🚀 MAJOR OPPORTUNITY: ${buySignals.length} Strong Buy Signals!`;\n  } else if (buySignals.length >= 5) {\n    subject = `📈 ${sentiment} Market: ${buySignals.length} Buy Opportunities`;\n  } else if (buySignals.length > 0) {\n    subject = `💡 ${buySignals.length} Stock Alert${buySignals.length > 1 ? 's' : ''} - ${sentiment} Market`;\n  } else {\n    subject = `📊 Market Update: No Strong Signals (${sentiment})`;\n  }\n  \n  // Add special flags to subject\n  if (earningsToday > 5) {\n    subject += ` | ${earningsToday} Earnings Today`;\n  }\n  if (hotThemes > 3) {\n    subject += ` | ${hotThemes} Hot Themes`;\n  }\n  \n  console.log(`📧 Email subject: ${subject}`);\n  console.log(`📊 Buy signals: ${buySignals.length}`);\n  console.log(`🎯 Market sentiment: ${sentiment}`);\n  \n  return [{\n    json: {\n      subject: subject,\n      email_to: 'your-email@example.com', // Change this to your email\n      buy_signals: buySignals,\n      market_context: marketContext,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString()\n      }\n    }\n  }];\n} else {\n  console.log('❌ Analysis failed');\n  return [{\n    json: {\n      subject: '❌ Stock Analysis Failed',\n      email_to: 'your-email@example.com',\n      buy_signals: [],\n      error: data.error\n    }\n  }];\n}"
                },
                "name": "Process & Create Email",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": "http://host.docker.internal:5002/api/send-email-alert",
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonBody": "={{ JSON.stringify($json) }}",
                    "options": {
                        "timeout": 15000
                    }
                },
                "name": "Send Enhanced Email",
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
                            "node": "Get Stock Analysis",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Stock Analysis": {
                "main": [
                    [
                        {
                            "node": "Process & Create Email",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Process & Create Email": {
                "main": [
                    [
                        {
                            "node": "Send Enhanced Email",
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
            print(f"✅ Enhanced Email Alert workflow created!")
            print(f"🔗 Link: http://localhost:5678/workflow/{workflow_id}")
            print()
            print("📧 Features:")
            print("   • Custom subject based on market conditions")
            print("   • Professional HTML email formatting")
            print("   • Market sentiment in subject line")
            print("   • Special flags for earnings and themes")
            print("   • Color-coded buy signals")
            print("   • Up to 15 top recommendations")
            print()
            print("🎯 Subject examples:")
            print("   • '🚀 MAJOR OPPORTUNITY: 12 Strong Buy Signals!'")
            print("   • '📈 BULLISH Market: 7 Buy Opportunities | 8 Earnings Today'")
            print("   • '💡 3 Stock Alerts - NEUTRAL Market | 5 Hot Themes'")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("📧 Creating Enhanced Email Alert Workflow...")
    create_email_alert_workflow()