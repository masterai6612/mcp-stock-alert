#!/usr/bin/env python3
"""
Setup Telegram integration in n8n workflows
"""

import requests
import json
import os
import time
from datetime import datetime

# n8n Configuration
N8N_BASE_URL = "http://localhost:5678"
N8N_API_URL = f"{N8N_BASE_URL}/api/v1"
N8N_AUTH = ("admin", "stockagent123")

def check_n8n_connection():
    """Check if n8n is running and accessible"""
    try:
        response = requests.get(f"{N8N_BASE_URL}/healthz", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_telegram_config():
    """Check Telegram configuration via our API"""
    try:
        response = requests.get("http://localhost:5002/api/telegram-config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('telegram_configured', False), data
        return False, {}
    except:
        return False, {}

def test_telegram_integration():
    """Test Telegram integration"""
    try:
        test_data = {
            "message": "🧪 *Telegram Integration Test*\n\nThis is a test message from the n8n setup script.\n\n✅ If you receive this, Telegram integration is working correctly!\n\n🤖 n8n workflows are now ready to send notifications."
        }
        
        response = requests.post(
            "http://localhost:5002/api/test-telegram",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('success', False), result.get('message', '')
        return False, f"HTTP {response.status_code}"
        
    except Exception as e:
        return False, str(e)

def import_telegram_workflow():
    """Import the Telegram stock alert workflow"""
    try:
        # Load the workflow JSON
        workflow_file = "n8n-workflows/telegram-stock-alert.json"
        
        if not os.path.exists(workflow_file):
            print(f"❌ Workflow file not found: {workflow_file}")
            return False
        
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Import workflow via n8n API
        response = requests.post(
            f"{N8N_API_URL}/workflows",
            json=workflow_data,
            auth=N8N_AUTH,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Telegram workflow imported successfully")
            return True
        else:
            print(f"❌ Failed to import workflow: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing workflow: {e}")
        return False

def activate_telegram_workflow():
    """Activate the Telegram workflow"""
    try:
        # Get list of workflows
        response = requests.get(f"{N8N_API_URL}/workflows", auth=N8N_AUTH, timeout=10)
        
        if response.status_code != 200:
            print(f"❌ Failed to get workflows: {response.status_code}")
            return False
        
        workflows = response.json()
        telegram_workflow = None
        
        # Find the Telegram workflow
        for workflow in workflows.get('data', []):
            if 'telegram' in workflow.get('name', '').lower():
                telegram_workflow = workflow
                break
        
        if not telegram_workflow:
            print("❌ Telegram workflow not found")
            return False
        
        workflow_id = telegram_workflow['id']
        
        # Activate the workflow
        response = requests.patch(
            f"{N8N_API_URL}/workflows/{workflow_id}",
            json={"active": True},
            auth=N8N_AUTH,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Telegram workflow activated")
            return True
        else:
            print(f"❌ Failed to activate workflow: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error activating workflow: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Telegram Integration for n8n")
    print("=" * 50)
    
    # Check n8n connection
    print("🔍 Checking n8n connection...")
    if not check_n8n_connection():
        print("❌ n8n is not running or not accessible")
        print("   Please start n8n first: docker-compose up -d")
        return False
    
    print("✅ n8n is running")
    
    # Check our API server
    print("🔍 Checking API server...")
    try:
        response = requests.get("http://localhost:5002/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server not responding correctly")
            return False
    except:
        print("❌ API server is not running")
        print("   Please start the API server: python n8n_integration.py")
        return False
    
    # Check Telegram configuration
    print("🔍 Checking Telegram configuration...")
    telegram_configured, config_data = check_telegram_config()
    
    if telegram_configured:
        print("✅ Telegram is configured")
        print(f"   Chat ID: {config_data.get('chat_id', 'Unknown')}")
        print(f"   Status: {config_data.get('status', 'Unknown')}")
    else:
        print("❌ Telegram is not configured")
        print("   Please check your .env file for TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        return False
    
    # Test Telegram integration
    print("🧪 Testing Telegram integration...")
    test_success, test_message = test_telegram_integration()
    
    if test_success:
        print("✅ Telegram test successful")
        print("📱 Check your Telegram for the test message")
    else:
        print(f"❌ Telegram test failed: {test_message}")
        return False
    
    # Import workflow
    print("📥 Importing Telegram workflow...")
    if import_telegram_workflow():
        print("✅ Workflow imported")
    else:
        print("❌ Failed to import workflow")
        return False
    
    # Wait a moment for n8n to process
    time.sleep(2)
    
    # Activate workflow
    print("🔄 Activating Telegram workflow...")
    if activate_telegram_workflow():
        print("✅ Workflow activated")
    else:
        print("❌ Failed to activate workflow")
        return False
    
    print("\n🎉 Telegram Integration Setup Complete!")
    print("=" * 50)
    print("✅ n8n workflows will now send notifications to both:")
    print("   📧 Email: masterai6612@gmail.com")
    print(f"   📱 Telegram: Chat ID {config_data.get('chat_id', 'Unknown')}")
    print()
    print("🔗 Access points:")
    print("   📊 n8n Dashboard: http://localhost:5678")
    print("   🔧 API Server: http://localhost:5002")
    print("   📈 Stock Dashboard: http://localhost:5001")
    print()
    print("🤖 The Telegram Stock Alert Workflow is now:")
    print("   ⏰ Running every hour")
    print("   📊 Analyzing 150 stocks")
    print("   📧 Sending email alerts for BUY signals")
    print("   📱 Sending Telegram notifications")
    print("   🎯 Including X (Twitter) sentiment analysis")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Setup completed successfully!")
        else:
            print("\n❌ Setup failed. Please check the errors above.")
    except KeyboardInterrupt:
        print("\n👋 Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")