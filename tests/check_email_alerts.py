#!/usr/bin/env python3
"""
Check if email alerts are configured and working
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def check_workflow_email_config(workflow_id, workflow_name):
    """Check if a workflow has email alert configuration"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=headers)
        
        if response.status_code == 200:
            workflow_data = response.json()
            nodes = workflow_data.get('nodes', [])
            
            print(f"🔍 Checking: {workflow_name}")
            
            email_nodes = []
            http_alert_nodes = []
            
            for node in nodes:
                node_type = node.get('type', '')
                node_name = node.get('name', '')
                
                # Check for email nodes
                if 'email' in node_type.lower() or 'mail' in node_type.lower():
                    email_nodes.append(node_name)
                
                # Check for HTTP alert endpoints
                if node_type == 'n8n-nodes-base.httpRequest':
                    url = node.get('parameters', {}).get('url', '')
                    if 'email-alert' in url or 'alert' in url:
                        http_alert_nodes.append({
                            'name': node_name,
                            'url': url
                        })
            
            if email_nodes:
                print(f"   ✅ Email nodes found: {', '.join(email_nodes)}")
            elif http_alert_nodes:
                print(f"   📧 HTTP alert endpoints found:")
                for alert_node in http_alert_nodes:
                    print(f"      • {alert_node['name']}: {alert_node['url']}")
            else:
                print(f"   ❌ No email alerts configured")
            
            print()
            return len(email_nodes) > 0 or len(http_alert_nodes) > 0
            
        else:
            print(f"   ❌ Failed to get workflow details: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking workflow: {e}")
        return False

def check_email_api_endpoint():
    """Check if our email alert API endpoint is working"""
    
    print("🧪 Testing email alert API endpoint...")
    
    test_data = {
        "buy_signals": [
            {
                "symbol": "AAPL",
                "price": 150.25,
                "recommendation": "BUY",
                "change_percent": 2.5,
                "rsi": 65.2,
                "earnings_soon": True,
                "in_hot_theme": False
            }
        ],
        "market_context": {
            "sentiment": "BULLISH",
            "earnings_today": 5,
            "hot_themes": 3
        },
        "summary": {
            "total_analyzed": 100,
            "timestamp": "2025-10-29T01:00:00Z"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:5002/api/send-email-alert",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Email API endpoint working")
            print(f"   📧 Would send: {result.get('message', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Email API failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error testing email API: {e}")
        return False

def check_email_configuration():
    """Check if email configuration exists"""
    
    print("📧 Checking email configuration...")
    
    # Check environment variables
    email_from = os.getenv('EMAIL_FROM')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if email_from and email_password:
        print(f"   ✅ Email config found in .env")
        print(f"   📧 From: {email_from}")
        return True
    else:
        print(f"   ⚠️ Email config not found in .env file")
        print(f"   💡 Add these to .env:")
        print(f"      EMAIL_FROM=your-email@gmail.com")
        print(f"      EMAIL_PASSWORD=your-app-password")
        return False

if __name__ == "__main__":
    print("🔍 Checking Email Alert Configuration...")
    print("=" * 50)
    
    # Check email configuration
    email_configured = check_email_configuration()
    print()
    
    # Check email API endpoint
    api_working = check_email_api_endpoint()
    print()
    
    # Check key workflows for email alerts
    workflows_to_check = [
        ("leH1zCk4Bk9yd2rl", "Scheduled Stock Agent - Every 30 Minutes"),
        ("vOlaWel3Gpofm27k", "Comprehensive Stock Analysis - Manual Test"),
        ("IbNcXnDXeqZ929gW", "Stock Alert Agent Workflow")
    ]
    
    print("🔍 Checking workflows for email alert nodes...")
    print("-" * 50)
    
    workflows_with_alerts = 0
    for workflow_id, workflow_name in workflows_to_check:
        if check_workflow_email_config(workflow_id, workflow_name):
            workflows_with_alerts += 1
    
    print("=" * 50)
    print("📊 Email Alert Status Summary:")
    print(f"   Email Configuration: {'✅ Configured' if email_configured else '❌ Not configured'}")
    print(f"   Email API Endpoint: {'✅ Working' if api_working else '❌ Not working'}")
    print(f"   Workflows with Alerts: {workflows_with_alerts}/{len(workflows_to_check)}")
    
    if not email_configured:
        print("\n💡 To enable email alerts:")
        print("1. Add email config to .env file")
        print("2. Configure SMTP settings in your workflows")
        print("3. Test the email functionality")
    elif workflows_with_alerts == 0:
        print("\n💡 Email API is ready, but workflows need email nodes added")
    else:
        print("\n🎉 Email alerts appear to be configured!")