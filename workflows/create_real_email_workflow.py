#!/usr/bin/env python3
"""
Create a workflow that sends real emails to masterai6612@gmail.com
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_real_email_workflow():
    """Create a workflow that sends actual emails"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "Real Email Alert - masterai6612@gmail.com",
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
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  const marketContext = data.market_context || {};\n  const sentiment = marketContext.sentiment || 'NEUTRAL';\n  const earningsToday = marketContext.earnings_today || 0;\n  const hotThemes = marketContext.hot_themes || 0;\n  \n  // Create personalized subject for masterai6612@gmail.com\n  let subject = '';\n  if (buySignals.length >= 8) {\n    subject = `🚀 MAJOR ALERT: ${buySignals.length} Strong Buy Signals Detected!`;\n  } else if (buySignals.length >= 3) {\n    subject = `📈 Trading Alert: ${buySignals.length} Buy Opportunities (${sentiment} Market)`;\n  } else if (buySignals.length > 0) {\n    subject = `💡 Stock Alert: ${buySignals.length} Signal${buySignals.length > 1 ? 's' : ''} Found`;\n  } else {\n    subject = `📊 Market Scan Complete: No Strong Signals (${sentiment})`;\n  }\n  \n  // Add market context\n  if (earningsToday > 3) {\n    subject += ` | ${earningsToday} Earnings Today`;\n  }\n  if (hotThemes > 2) {\n    subject += ` | ${hotThemes} Hot Themes`;\n  }\n  \n  console.log(`📧 Preparing email for masterai6612@gmail.com`);\n  console.log(`📊 Subject: ${subject}`);\n  console.log(`📈 Buy signals: ${buySignals.length}`);\n  console.log(`🎯 Market sentiment: ${sentiment}`);\n  \n  return [{\n    json: {\n      subject: subject,\n      email_to: 'masterai6612@gmail.com',\n      buy_signals: buySignals,\n      market_context: marketContext,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString()\n      }\n    }\n  }];\n} else {\n  console.log('❌ Analysis failed');\n  return [{\n    json: {\n      subject: '❌ Stock Analysis System Error',\n      email_to: 'masterai6612@gmail.com',\n      buy_signals: [],\n      error: data.error,\n      summary: {\n        total_analyzed: 0,\n        timestamp: new Date().toISOString()\n      }\n    }\n  }];\n}"
                },
                "name": "Prepare Email for masterai6612",
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
                "name": "Send Real Email",
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
                            "node": "Prepare Email for masterai6612",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Prepare Email for masterai6612": {
                "main": [
                    [
                        {
                            "node": "Send Real Email",
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
            print(f"✅ Real email workflow created!")
            print(f"🔗 Link: http://localhost:5678/workflow/{workflow_id}")
            print()
            print("📧 This workflow will:")
            print("   • Analyze 20 stocks from your 269+ universe")
            print("   • Send REAL emails to masterai6612@gmail.com")
            print("   • Use professional HTML formatting")
            print("   • Include intelligent subject lines")
            print("   • Show buy signals with market context")
            print()
            print("⚠️ Make sure EMAIL_PASSWORD is set in .env file!")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("📧 Creating real email workflow for masterai6612@gmail.com...")
    create_real_email_workflow()