#!/usr/bin/env python3
"""
Update workflows to analyze ALL 269 stocks instead of just 100
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def update_workflow_to_full_universe(workflow_id, workflow_name):
    """Update a workflow to analyze all 269 stocks"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        # Get the current workflow
        response = requests.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get workflow {workflow_name}: {response.status_code}")
            return False
            
        workflow_data = response.json()
        print(f"📊 Updating: {workflow_name}")
        
        # Find and update HTTP request nodes that call comprehensive-analysis
        updated_nodes = 0
        for node in workflow_data.get('nodes', []):
            if (node.get('type') == 'n8n-nodes-base.httpRequest' and 
                'comprehensive-analysis' in node.get('parameters', {}).get('url', '')):
                
                # Parse the current JSON body
                json_body = node['parameters'].get('jsonBody', '{}')
                try:
                    # Parse the JSON to update stock_limit
                    if isinstance(json_body, str):
                        # Handle string JSON
                        import re
                        # Extract stock_limit value and replace it
                        if 'stock_limit' in json_body:
                            # Replace any existing stock_limit with 269
                            new_json_body = re.sub(
                                r'"stock_limit":\s*\d+',
                                '"stock_limit": 269',
                                json_body
                            )
                        else:
                            # Add stock_limit if it doesn't exist
                            new_json_body = json_body.replace(
                                '}',
                                ',\n  "stock_limit": 269\n}'
                            )
                        
                        node['parameters']['jsonBody'] = new_json_body
                        updated_nodes += 1
                        print(f"   ✅ Updated node: {node.get('name', 'Unknown')}")
                        
                except Exception as e:
                    print(f"   ⚠️ Could not parse JSON in node {node.get('name', 'Unknown')}: {e}")
        
        if updated_nodes > 0:
            # Update the workflow
            response = requests.put(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}",
                json=workflow_data,
                headers=headers
            )
            
            if response.status_code == 200:
                print(f"   ✅ Workflow updated successfully! Now analyzes ALL 269 stocks")
                return True
            else:
                print(f"   ❌ Failed to update workflow: {response.status_code}")
                return False
        else:
            print(f"   ⚠️ No nodes found to update")
            return False
            
    except Exception as e:
        print(f"   ❌ Error updating workflow: {e}")
        return False

def create_full_universe_workflow():
    """Create a new workflow that definitely analyzes all 269 stocks"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "FULL UNIVERSE - All 269 Stocks Analysis",
        "nodes": [
            {
                "parameters": {
                    "rule": {
                        "interval": [
                            {
                                "field": "minutes",
                                "minutesInterval": 30
                            }
                        ]
                    }
                },
                "name": "Every 30 Minutes",
                "type": "n8n-nodes-base.scheduleTrigger",
                "typeVersion": 1.1,
                "position": [240, 300]
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": "http://host.docker.internal:5002/api/comprehensive-analysis",
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"include_earnings\": true,\n  \"include_themes\": true,\n  \"include_sentiment\": true,\n  \"stock_limit\": 269\n}",
                    "options": {
                        "timeout": 120000
                    }
                },
                "name": "Analyze ALL 269 Stocks",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  const marketContext = data.market_context || {};\n  const sentiment = marketContext.sentiment || 'NEUTRAL';\n  const earningsToday = marketContext.earnings_today || 0;\n  const hotThemes = marketContext.hot_themes || 0;\n  \n  // Create intelligent subject for full universe analysis\n  let subject = '';\n  if (buySignals.length >= 15) {\n    subject = `🚀 MASSIVE OPPORTUNITY: ${buySignals.length} Strong Buy Signals from 269 Stocks!`;\n  } else if (buySignals.length >= 8) {\n    subject = `📈 MAJOR ALERT: ${buySignals.length} Buy Signals from Full Universe Analysis`;\n  } else if (buySignals.length >= 3) {\n    subject = `💡 ${buySignals.length} Buy Opportunities from 269 Stock Scan (${sentiment})`;\n  } else if (buySignals.length > 0) {\n    subject = `📊 ${buySignals.length} Signal${buySignals.length > 1 ? 's' : ''} from Complete Market Scan`;\n  } else {\n    subject = `📊 Full Universe Scan Complete: No Strong Signals (${sentiment} Market)`;\n  }\n  \n  // Add market context\n  if (earningsToday > 5) {\n    subject += ` | ${earningsToday} Earnings Today`;\n  }\n  if (hotThemes > 3) {\n    subject += ` | ${hotThemes} Hot Themes`;\n  }\n  \n  console.log(`🤖 FULL UNIVERSE ANALYSIS: ${data.total_analyzed} stocks analyzed`);\n  console.log(`📈 Buy signals found: ${buySignals.length}`);\n  console.log(`📧 Email subject: ${subject}`);\n  console.log(`🎯 Market sentiment: ${sentiment}`);\n  \n  return [{\n    json: {\n      subject: subject,\n      email_to: 'masterai6612@gmail.com',\n      buy_signals: buySignals,\n      market_context: marketContext,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString(),\n        full_universe: true\n      }\n    }\n  }];\n} else {\n  console.log('❌ Full universe analysis failed');\n  return [{\n    json: {\n      subject: '❌ Full Universe Analysis Failed',\n      email_to: 'masterai6612@gmail.com',\n      buy_signals: [],\n      error: data.error\n    }\n  }];\n}"
                },
                "name": "Process Full Universe Results",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            },
            {
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
                "name": "Send Full Universe Email",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [1120, 300]
            }
        ],
        "connections": {
            "Every 30 Minutes": {
                "main": [
                    [
                        {
                            "node": "Analyze ALL 269 Stocks",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Analyze ALL 269 Stocks": {
                "main": [
                    [
                        {
                            "node": "Process Full Universe Results",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Process Full Universe Results": {
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
                            "node": "Send Full Universe Email",
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
            print(f"✅ Full Universe workflow created!")
            print(f"🔗 Link: http://localhost:5678/workflow/{workflow_id}")
            
            # Activate it immediately
            activate_response = requests.post(
                f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate",
                headers=headers
            )
            
            if activate_response.status_code == 200:
                print(f"✅ Workflow activated - now analyzing ALL 269 stocks every 30 minutes!")
            
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Updating workflows to analyze ALL 269 stocks...")
    print("=" * 60)
    
    # Key workflows to update
    workflows_to_update = [
        ("leH1zCk4Bk9yd2rl", "Scheduled Stock Agent - Every 30 Minutes"),
        ("vT3dbsgFAblxcuvf", "Real Email Alert - masterai6612@gmail.com"),
        ("MnWtw1f6LgSkuNng", "Enhanced Email Alert System")
    ]
    
    updated_count = 0
    for workflow_id, workflow_name in workflows_to_update:
        if update_workflow_to_full_universe(workflow_id, workflow_name):
            updated_count += 1
        print()
    
    print("=" * 60)
    print(f"📊 Updated {updated_count} existing workflows")
    
    # Create a new full universe workflow as backup
    print("\n🚀 Creating dedicated FULL UNIVERSE workflow...")
    new_workflow_id = create_full_universe_workflow()
    
    if new_workflow_id:
        print("\n🎉 SUCCESS! Your agentic system now analyzes ALL 269 stocks!")
        print("\n📊 Full Universe Analysis includes:")
        print("   • All 269 stocks from your comprehensive universe")
        print("   • S&P 500 large caps, IPOs, trending stocks")
        print("   • Canadian large caps and international stocks")
        print("   • AI, biotech, energy, financial, and all sectors")
        print("\n🤖 Your system is now truly comprehensive!")
    else:
        print("\n⚠️ Some workflows updated, but failed to create new full universe workflow")