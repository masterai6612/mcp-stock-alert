#!/usr/bin/env python3
"""
Update the main scheduled workflow to include email alerts
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def update_scheduled_workflow_with_email():
    """Add email alerts to the main scheduled workflow"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    SCHEDULED_WORKFLOW_ID = "leH1zCk4Bk9yd2rl"  # From our earlier list
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Get the current scheduled workflow
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows/{SCHEDULED_WORKFLOW_ID}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get scheduled workflow: {response.status_code}")
            return False
            
        workflow_data = response.json()
        print(f"✅ Retrieved scheduled workflow: {workflow_data['name']}")
        
        # Add email alert node
        email_node = {
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
            "name": "Send Email Alerts",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 4.1,
            "position": [1120, 400]
        }
        
        # Add condition node to check if alerts should be sent
        condition_node = {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict"
                    },
                    "conditions": [
                        {
                            "id": "condition-1",
                            "leftValue": "={{ $json.buy_signals.length }}",
                            "rightValue": 0,
                            "operator": {
                                "type": "number",
                                "operation": "gt"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "name": "Has Buy Signals?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [900, 300]
        }
        
        # Enhanced processing node with email preparation
        enhanced_process_node = {
            "parameters": {
                "mode": "runOnceForAllItems",
                "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  const marketContext = data.market_context || {};\n  const sentiment = marketContext.sentiment || 'NEUTRAL';\n  const earningsToday = marketContext.earnings_today || 0;\n  const hotThemes = marketContext.hot_themes || 0;\n  \n  // Create intelligent subject\n  let subject = '';\n  if (buySignals.length >= 10) {\n    subject = `🚀 MAJOR OPPORTUNITY: ${buySignals.length} Strong Buy Signals!`;\n  } else if (buySignals.length >= 5) {\n    subject = `📈 ${sentiment} Market: ${buySignals.length} Buy Opportunities`;\n  } else if (buySignals.length > 0) {\n    subject = `💡 ${buySignals.length} Stock Alert${buySignals.length > 1 ? 's' : ''} - ${sentiment} Market`;\n  } else {\n    subject = `📊 Market Update: No Strong Signals (${sentiment})`;\n  }\n  \n  // Add context to subject\n  if (earningsToday > 5) {\n    subject += ` | ${earningsToday} Earnings Today`;\n  }\n  if (hotThemes > 3) {\n    subject += ` | ${hotThemes} Hot Themes`;\n  }\n  \n  console.log(`🤖 Automated Analysis: ${data.total_analyzed} stocks`);\n  console.log(`📈 Buy signals: ${buySignals.length}`);\n  console.log(`📧 Email subject: ${subject}`);\n  \n  return [{\n    json: {\n      subject: subject,\n      email_to: 'your-email@example.com', // Update this!\n      buy_signals: buySignals,\n      market_context: marketContext,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString()\n      }\n    }\n  }];\n} else {\n  console.log('❌ Automated analysis failed');\n  return [{\n    json: {\n      subject: '❌ Automated Stock Analysis Failed',\n      email_to: 'your-email@example.com',\n      buy_signals: [],\n      error: data.error\n    }\n  }];\n}"
            },
            "name": "Process Signals & Prepare Email",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [680, 300]
        }
        
        # Update the workflow nodes
        workflow_data['nodes'] = [
            # Keep the schedule trigger and analysis nodes
            workflow_data['nodes'][0],  # Schedule trigger
            workflow_data['nodes'][1],  # Comprehensive analysis
            enhanced_process_node,      # Enhanced processing
            condition_node,             # Condition check
            email_node                  # Email alert
        ]
        
        # Update connections
        workflow_data['connections'] = {
            "Every 30 Minutes": {
                "main": [
                    [
                        {
                            "node": "Comprehensive Analysis",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Comprehensive Analysis": {
                "main": [
                    [
                        {
                            "node": "Process Signals & Prepare Email",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Process Signals & Prepare Email": {
                "main": [
                    [
                        {
                            "node": "Has Buy Signals?",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Has Buy Signals?": {
                "main": [
                    [
                        {
                            "node": "Send Email Alerts",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        }
        
        # Update the workflow
        response = requests.put(
            f"{N8N_URL}/api/v1/workflows/{SCHEDULED_WORKFLOW_ID}",
            json=workflow_data,
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Scheduled workflow updated with email alerts!")
            print(f"🔗 Link: http://localhost:5678/workflow/{SCHEDULED_WORKFLOW_ID}")
            print()
            print("📧 Email alerts will now be sent when:")
            print("   • Buy signals are detected")
            print("   • Every 30 minutes (if there are signals)")
            print("   • With intelligent subject lines")
            print("   • Professional HTML formatting")
            return True
        else:
            print(f"❌ Failed to update workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating scheduled workflow: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Adding email alerts to main scheduled workflow...")
    
    if update_scheduled_workflow_with_email():
        print("\n🎉 Success! Your main automated workflow now includes:")
        print("   ✅ Every 30-minute analysis")
        print("   ✅ 100 stock comprehensive analysis")
        print("   ✅ Intelligent email alerts")
        print("   ✅ Professional HTML formatting")
        print("   ✅ Smart subject lines")
        print()
        print("🚀 Your agentic system is now fully automated with email alerts!")
    else:
        print("\n❌ Failed to update the workflow")