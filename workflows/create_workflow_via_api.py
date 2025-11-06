#!/usr/bin/env python3
"""
Create n8n workflow via API instead of importing JSON
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# n8n configuration
N8N_URL = "http://localhost:5678"
API_KEY = os.getenv('N8N_API_KEY')

if not API_KEY:
    print("❌ Error: N8N_API_KEY not found in environment variables")
    print("Please set your API key in .env file or environment")
    exit(1)

def create_simple_workflow():
    """Create a simple test workflow via API"""
    
    workflow_data = {
        "name": "API Test - Health Check",
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
                    "requestMethod": "GET",
                    "url": "http://host.docker.internal:5002/health"
                },
                "name": "Health Check",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [
                    [
                        {
                            "node": "Health Check",
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
            print("✅ Simple workflow created successfully!")
            workflow_id = response.json().get('id')
            print(f"Workflow ID: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Simple workflow creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating simple workflow: {e}")
        return None

def create_comprehensive_workflow():
    """Create the comprehensive analysis workflow via API"""
    
    workflow_data = {
        "name": "Comprehensive Stock Analysis - Manual Test",
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
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"include_earnings\": true,\n  \"include_themes\": true,\n  \"stock_limit\": 10\n}",
                    "options": {
                        "timeout": 30000
                    }
                },
                "name": "Comprehensive Analysis",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  console.log(`✅ Analysis complete: ${data.total_analyzed} stocks analyzed`);\n  console.log(`📈 Buy signals found: ${buySignals.length}`);\n  console.log(`📅 Earnings today: ${data.market_context?.earnings_today || 0}`);\n  console.log(`🔥 Hot themes: ${data.market_context?.hot_themes || 0}`);\n  \n  if (buySignals.length > 0) {\n    console.log('🎯 Top Buy Signals:');\n    buySignals.slice(0, 5).forEach(stock => {\n      console.log(`  ${stock.symbol}: ${stock.recommendation} at $${stock.price} (${stock.change_percent}%)`);\n    });\n  }\n  \n  return [{\n    json: {\n      success: true,\n      buy_signals: buySignals,\n      total_analyzed: data.total_analyzed,\n      market_context: data.market_context\n    }\n  }];\n} else {\n  console.log('❌ Analysis failed:', data.error);\n  return [{ json: { success: false, error: data.error } }];\n}"
                },
                "name": "Process Results",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            }
        ],
        "connections": {
            "Manual Trigger": {
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
                            "node": "Process Results",
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
            print("✅ Comprehensive workflow created successfully!")
            workflow_id = response.json().get('id')
            print(f"Workflow ID: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Comprehensive workflow creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating comprehensive workflow: {e}")
        return None

def create_scheduled_workflow():
    """Create a scheduled comprehensive analysis workflow"""
    
    workflow_data = {
        "name": "Scheduled Stock Agent - Every 30 Minutes",
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
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"include_earnings\": true,\n  \"include_themes\": true,\n  \"stock_limit\": 100\n}",
                    "options": {
                        "timeout": 120000
                    }
                },
                "name": "Comprehensive Analysis",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 300]
            },
            {
                "parameters": {
                    "mode": "runOnceForAllItems",
                    "jsCode": "const data = $input.all()[0].json;\n\nif (data.success) {\n  const buySignals = data.data.filter(stock => \n    stock.recommendation === 'BUY' || stock.recommendation === 'STRONG BUY'\n  );\n  \n  console.log(`🤖 Automated Analysis: ${data.total_analyzed} stocks`);\n  console.log(`📈 Buy signals: ${buySignals.length}`);\n  \n  return [{\n    json: {\n      buy_signals: buySignals,\n      market_context: data.market_context,\n      summary: {\n        total_analyzed: data.total_analyzed,\n        timestamp: new Date().toISOString()\n      }\n    }\n  }];\n} else {\n  console.log('❌ Automated analysis failed');\n  return [{ json: { success: false } }];\n}"
                },
                "name": "Process Signals",
                "type": "n8n-nodes-base.code",
                "typeVersion": 2,
                "position": [680, 300]
            }
        ],
        "connections": {
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
                            "node": "Process Signals",
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
            print("✅ Scheduled workflow created successfully!")
            workflow_id = response.json().get('id')
            print(f"Workflow ID: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Scheduled workflow creation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating scheduled workflow: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Creating workflows via n8n API...")
    
    # Create simple test workflow first
    simple_id = create_simple_workflow()
    if simple_id:
        print(f"✅ Simple workflow created: {simple_id}")
        
        # Create comprehensive manual test workflow
        comp_id = create_comprehensive_workflow()
        if comp_id:
            print(f"✅ Comprehensive workflow created: {comp_id}")
            
            # Create scheduled workflow
            sched_id = create_scheduled_workflow()
            if sched_id:
                print(f"✅ Scheduled workflow created: {sched_id}")
                print("\n🎉 All workflows created successfully!")
                print("\n📋 Next steps:")
                print("1. Go to n8n: http://localhost:5678")
                print("2. Test the 'API Test - Health Check' workflow first")
                print("3. Test the 'Comprehensive Stock Analysis - Manual Test' workflow")
                print("4. Activate the 'Scheduled Stock Agent' for automated analysis")
            else:
                print("⚠️ Manual workflows created, but scheduled failed")
        else:
            print("⚠️ Simple workflow created, but comprehensive failed")
    else:
        print("❌ Failed to create workflows")