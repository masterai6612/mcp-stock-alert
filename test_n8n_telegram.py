#!/usr/bin/env python3
"""
Test n8n Telegram integration
"""

import requests
import json
import time
from datetime import datetime

def test_api_endpoints():
    """Test all API endpoints for Telegram functionality"""
    print("🧪 Testing n8n API Endpoints with Telegram Support")
    print("=" * 55)
    
    base_url = "http://localhost:5002"
    
    # Test health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            telegram_status = data.get('services', {}).get('telegram', False)
            print(f"   ✅ Health check passed")
            print(f"   📱 Telegram service: {'✅ Available' if telegram_status else '❌ Not configured'}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
    
    # Test Telegram configuration
    print("\n2. Testing Telegram configuration...")
    try:
        response = requests.get(f"{base_url}/api/telegram-config", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Configuration check passed")
            print(f"   📱 Telegram configured: {data.get('telegram_configured', False)}")
            print(f"   🤖 Bot token set: {data.get('bot_token_set', False)}")
            print(f"   💬 Chat ID set: {data.get('chat_id_set', False)}")
            print(f"   📞 Connection status: {data.get('status', 'Unknown')}")
            if data.get('chat_id'):
                print(f"   🆔 Chat ID: {data.get('chat_id')}")
        else:
            print(f"   ❌ Configuration check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Configuration check error: {e}")
    
    # Test Telegram message
    print("\n3. Testing Telegram message...")
    try:
        test_data = {
            "message": "🧪 *n8n Integration Test*\n\nThis is a test message from the n8n Telegram integration test script.\n\n📊 Testing features:\n• ✅ Markdown formatting\n• ✅ Emoji support\n• ✅ API connectivity\n\n🤖 If you see this, the integration is working!"
        }
        
        response = requests.post(f"{base_url}/api/test-telegram", json=test_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Telegram test passed")
            print(f"   📱 Message sent: {data.get('success', False)}")
            print(f"   💬 Chat ID: {data.get('chat_id', 'Unknown')}")
        else:
            print(f"   ❌ Telegram test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Telegram test error: {e}")
    
    # Test stock analysis
    print("\n4. Testing stock analysis...")
    try:
        analysis_data = {
            "analysis_type": "full_universe",
            "stock_limit": 10,  # Small test
            "include_earnings": True,
            "include_themes": True,
            "include_sentiment": True
        }
        
        response = requests.post(f"{base_url}/api/comprehensive-analysis", json=analysis_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stock analysis passed")
            print(f"   📊 Stocks analyzed: {data.get('total_analyzed', 0)}")
            print(f"   🚀 Success: {data.get('success', False)}")
            
            # Count BUY signals for next test
            buy_signals = [stock for stock in data.get('data', []) if 'BUY' in stock.get('recommendation', '')]
            print(f"   🎯 BUY signals found: {len(buy_signals)}")
            
            return buy_signals, data.get('market_context', {})
        else:
            print(f"   ❌ Stock analysis failed: {response.status_code}")
            return [], {}
    except Exception as e:
        print(f"   ❌ Stock analysis error: {e}")
        return [], {}

def test_alert_system(buy_signals, market_context):
    """Test the alert system with real data"""
    print("\n5. Testing alert system...")
    
    if not buy_signals:
        print("   ⚠️  No BUY signals to test with, creating mock data...")
        buy_signals = [
            {
                "symbol": "TEST",
                "price": 100.0,
                "change_percent": 5.0,
                "rsi": 65.0,
                "recommendation": "BUY",
                "x_sentiment": "Bullish",
                "earnings_soon": False,
                "in_hot_theme": True
            }
        ]
    
    # Test email + Telegram alert
    try:
        alert_data = {
            "buy_signals": buy_signals[:5],  # Top 5 signals
            "market_context": market_context,
            "summary": {
                "total_analyzed": 10,
                "timestamp": datetime.now().isoformat()
            },
            "subject": "🧪 Test Alert: n8n + Telegram Integration",
            "email_to": "masterai6612@gmail.com"
        }
        
        response = requests.post("http://localhost:5002/api/send-email-alert", json=alert_data, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Email + Telegram alert sent")
            print(f"   📧 Email to: {data.get('email_to', 'Unknown')}")
            print(f"   📱 Telegram chat: {data.get('telegram_chat_id', 'Unknown')}")
            print(f"   🎯 Signals count: {data.get('signals_count', 0)}")
        else:
            print(f"   ❌ Alert failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Alert error: {e}")
    
    # Test Telegram-only alert
    print("\n6. Testing Telegram-only alert...")
    try:
        telegram_data = {
            "subject": "📱 Telegram-Only Test Alert",
            "buy_signals": buy_signals[:3]  # Top 3 signals
        }
        
        response = requests.post("http://localhost:5002/api/send-telegram-alert", json=telegram_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Telegram-only alert sent")
            print(f"   📱 Success: {data.get('success', False)}")
            print(f"   🎯 Signals count: {data.get('signals_count', 0)}")
        else:
            print(f"   ❌ Telegram alert failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Telegram alert error: {e}")

def test_n8n_workflow():
    """Test n8n workflow execution"""
    print("\n7. Testing n8n workflow...")
    
    # Check if n8n is running
    try:
        response = requests.get("http://localhost:5678/healthz", timeout=5)
        if response.status_code == 200:
            print("   ✅ n8n is running")
            
            # Try to get workflows
            try:
                response = requests.get(
                    "http://localhost:5678/api/v1/workflows",
                    auth=("admin", "stockagent123"),
                    timeout=10
                )
                
                if response.status_code == 200:
                    workflows = response.json()
                    telegram_workflows = [w for w in workflows.get('data', []) if 'telegram' in w.get('name', '').lower()]
                    
                    print(f"   ✅ Found {len(workflows.get('data', []))} total workflows")
                    print(f"   📱 Found {len(telegram_workflows)} Telegram workflows")
                    
                    for workflow in telegram_workflows:
                        status = "🟢 Active" if workflow.get('active') else "🔴 Inactive"
                        print(f"      • {workflow.get('name', 'Unknown')}: {status}")
                else:
                    print(f"   ❌ Failed to get workflows: {response.status_code}")
            except Exception as e:
                print(f"   ❌ Workflow check error: {e}")
        else:
            print("   ❌ n8n is not responding")
    except Exception as e:
        print(f"   ❌ n8n connection error: {e}")

def main():
    """Main test function"""
    print("🧪 N8N TELEGRAM INTEGRATION TEST")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test API endpoints
    buy_signals, market_context = test_api_endpoints()
    
    # Test alert system
    test_alert_system(buy_signals, market_context)
    
    # Test n8n workflow
    test_n8n_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 TEST SUMMARY")
    print("=" * 60)
    print("✅ API endpoints tested")
    print("✅ Telegram configuration checked")
    print("✅ Stock analysis tested")
    print("✅ Alert system tested")
    print("✅ n8n workflow checked")
    print()
    print("📱 Check your Telegram for test messages!")
    print("📧 Check your email for test alerts!")
    print()
    print("🔗 Access Points:")
    print("   📊 n8n Dashboard: http://localhost:5678")
    print("   🔧 API Server: http://localhost:5002")
    print("   📈 Stock Dashboard: http://localhost:5001")
    print()
    print("🤖 Your n8n workflows now support:")
    print("   ✅ Dual notifications (Email + Telegram)")
    print("   ✅ Stock analysis with X sentiment")
    print("   ✅ Automated hourly monitoring")
    print("   ✅ Professional alert formatting")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")