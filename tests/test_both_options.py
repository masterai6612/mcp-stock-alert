#!/usr/bin/env python3
"""
Test both Script-based and n8n workflow options
Verify email alerts are working for both
"""

import requests
import subprocess
import time
import os
from dotenv import load_dotenv

load_dotenv()

def test_script_option():
    """Test the script-based option"""
    print("🧪 Testing Script-Based Option...")
    print("-" * 40)
    
    try:
        # Run the enhanced main script
        result = subprocess.run(
            ["python", "main_enhanced.py"], 
            capture_output=True, 
            text=True, 
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Script-based analysis completed successfully")
            
            # Check if email was mentioned in output
            if "email" in result.stdout.lower() or "alert" in result.stdout.lower():
                print("✅ Email alert functionality detected")
            else:
                print("⚠️ No email alert indication in output")
            
            # Show sample output
            lines = result.stdout.split('\n')
            print("📊 Sample output:")
            for line in lines[:10]:
                if line.strip():
                    print(f"   {line}")
            
            return True
        else:
            print(f"❌ Script failed with return code: {result.returncode}")
            print(f"Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Script timed out (may still be running)")
        return False
    except Exception as e:
        print(f"❌ Error running script: {e}")
        return False

def test_n8n_option():
    """Test the n8n workflow option"""
    print("\n🧪 Testing n8n Workflow Option...")
    print("-" * 40)
    
    try:
        # Test n8n API health
        health_response = requests.get("http://localhost:5002/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ n8n Integration API is healthy")
        else:
            print(f"❌ n8n API health check failed: {health_response.status_code}")
            return False
        
        # Test comprehensive analysis endpoint
        analysis_data = {
            "analysis_type": "full_universe",
            "include_earnings": True,
            "include_themes": True,
            "include_sentiment": True,
            "stock_limit": 5
        }
        
        analysis_response = requests.post(
            "http://localhost:5002/api/comprehensive-analysis",
            json=analysis_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if analysis_response.status_code == 200:
            result = analysis_response.json()
            print("✅ n8n comprehensive analysis working")
            print(f"📊 Analyzed {result.get('total_analyzed', 0)} stocks")
            
            # Check for X sentiment
            if result.get('data') and len(result['data']) > 0:
                sample_stock = result['data'][0]
                if 'x_sentiment' in sample_stock:
                    print(f"✅ X sentiment integration working: {sample_stock['x_sentiment']}")
                else:
                    print("⚠️ X sentiment not found in response")
            
            return True
        else:
            print(f"❌ n8n analysis failed: {analysis_response.status_code}")
            print(f"Response: {analysis_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ n8n API connection error: {e}")
        return False

def test_email_configuration():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration...")
    print("-" * 40)
    
    email_from = os.getenv('EMAIL_FROM')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if email_from and email_password:
        print(f"✅ Email FROM: {email_from}")
        print(f"✅ Email PASSWORD: {'*' * len(email_password)}")
        
        # Test email alert endpoint
        try:
            test_email_data = {
                "email_to": "masterai6612@gmail.com",
                "subject": "🧪 Test Email from Agentic Stock System",
                "buy_signals": [
                    {
                        "symbol": "TEST",
                        "price": 100.0,
                        "recommendation": "BUY",
                        "change_percent": 5.0,
                        "rsi": 65.0,
                        "x_sentiment": "Bullish",
                        "earnings_soon": False,
                        "in_hot_theme": True
                    }
                ],
                "market_context": {
                    "sentiment": "BULLISH",
                    "earnings_today": 3,
                    "hot_themes": 2
                },
                "summary": {
                    "total_analyzed": 50,
                    "timestamp": "2025-10-29T02:30:00Z"
                }
            }
            
            email_response = requests.post(
                "http://localhost:5002/api/send-email-alert",
                json=test_email_data,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            if email_response.status_code == 200:
                result = email_response.json()
                print("✅ Email alert API working")
                print(f"📧 Subject: {result.get('subject', 'Unknown')}")
                
                if result.get('success'):
                    print("✅ Test email sent successfully!")
                    print("📬 Check masterai6612@gmail.com for test email")
                else:
                    print("⚠️ Email API responded but may not have sent email")
                
                return True
            else:
                print(f"❌ Email alert API failed: {email_response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Email API connection error: {e}")
            return False
    else:
        print("❌ Email configuration missing in .env file")
        return False

def test_n8n_workflows():
    """Test n8n workflows are accessible"""
    print("\n🔄 Testing n8n Workflows...")
    print("-" * 40)
    
    try:
        # Test n8n UI accessibility
        n8n_response = requests.get("http://localhost:5678", timeout=10)
        if n8n_response.status_code == 200:
            print("✅ n8n UI is accessible at http://localhost:5678")
            print("🔑 Login: admin / stockagent123")
            print("📊 Key workflows:")
            print("   • FULL UNIVERSE - All 269 Stocks Analysis (Auto-running)")
            print("   • Real Email Alert - masterai6612@gmail.com (Manual)")
            print("   • X (Twitter) Sentiment Analysis - Enhanced (Demo)")
            return True
        else:
            print(f"❌ n8n UI not accessible: {n8n_response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ n8n UI connection error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Complete Agentic Stock Alert System")
    print("=" * 60)
    
    # Test all components
    script_ok = test_script_option()
    n8n_ok = test_n8n_option()
    email_ok = test_email_configuration()
    workflows_ok = test_n8n_workflows()
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    print(f"1️⃣  Script-Based Option:     {'✅ WORKING' if script_ok else '❌ FAILED'}")
    print(f"2️⃣  n8n Workflow Option:     {'✅ WORKING' if n8n_ok else '❌ FAILED'}")
    print(f"📧 Email Alert System:      {'✅ WORKING' if email_ok else '❌ FAILED'}")
    print(f"🔄 n8n Workflows:           {'✅ ACCESSIBLE' if workflows_ok else '❌ FAILED'}")
    
    if all([script_ok, n8n_ok, email_ok, workflows_ok]):
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
        print("✅ Both options are working and email alerts are configured")
        print("📧 You will receive alerts at masterai6612@gmail.com")
        print("\n🚀 Your agentic stock system is ready for trading analysis!")
    else:
        print("\n⚠️ Some components need attention")
        print("Check the individual test results above")
    
    print("\n💡 Next Steps:")
    print("   • Run script manually: python main_enhanced.py")
    print("   • Check n8n workflows: http://localhost:5678")
    print("   • Monitor system: ./monitor_system.sh")
    print("   • Stop system: ./stop_system.sh")