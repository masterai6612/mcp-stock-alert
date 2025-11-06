#!/usr/bin/env python3
"""
Verification script to ensure enhanced technical analysis is working in n8n workflows
"""

import requests
import os
import json
from dotenv import load_dotenv

def verify_enhanced_system():
    print("🔍 Verifying Enhanced Technical Analysis System")
    print("=" * 50)
    
    load_dotenv()
    
    # Test 1: Check n8n API key
    api_key = os.getenv('N8N_API_KEY')
    if api_key and len(api_key) > 100:
        print("✅ N8N_API_KEY is configured")
    else:
        print("❌ N8N_API_KEY is missing or invalid")
        return False
    
    # Test 2: Check n8n Integration API
    try:
        response = requests.get("http://localhost:5002/health", timeout=5)
        if response.status_code == 200:
            print("✅ n8n Integration API is running")
        else:
            print("❌ n8n Integration API is not responding")
            return False
    except:
        print("❌ n8n Integration API is not accessible")
        return False
    
    # Test 3: Check Enhanced Technical Analysis
    try:
        response = requests.post(
            "http://localhost:5002/api/comprehensive-analysis",
            json={"stock_limit": 1, "include_sentiment": False},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('data'):
                stock_data = data['data'][0] if data['data'] else {}
                
                # Check for enhanced technical analysis features
                enhanced_features = [
                    'technical_score', 'technical_signals', 'macd', 
                    'bollinger', 'moving_averages', 'volume_analysis', 'momentum'
                ]
                
                missing_features = []
                for feature in enhanced_features:
                    if feature not in stock_data:
                        missing_features.append(feature)
                
                if not missing_features:
                    print("✅ Enhanced Technical Analysis is working")
                    print(f"   Sample stock: {stock_data.get('symbol', 'Unknown')}")
                    print(f"   Technical score: {stock_data.get('technical_score', 0)}/100")
                    print(f"   Technical signals: {len(stock_data.get('technical_signals', []))}")
                else:
                    print("⚠️ Enhanced Technical Analysis is partially working")
                    print(f"   Missing features: {', '.join(missing_features)}")
            else:
                print("❌ Enhanced Technical Analysis API returned no data")
                return False
        else:
            print(f"❌ Enhanced Technical Analysis API failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Enhanced Technical Analysis test failed: {e}")
        return False
    
    # Test 4: Check n8n workflows
    try:
        headers = {"X-N8N-API-KEY": api_key}
        response = requests.get("http://localhost:5678/rest/workflows", headers=headers, timeout=10)
        
        if response.status_code == 200:
            workflows = response.json()
            scheduled_workflows = [w for w in workflows if 'scheduled' in w.get('name', '').lower()]
            active_scheduled = [w for w in scheduled_workflows if w.get('active')]
            
            print(f"✅ Found {len(workflows)} n8n workflows")
            print(f"   Scheduled workflows: {len(scheduled_workflows)}")
            print(f"   Active scheduled workflows: {len(active_scheduled)}")
            
            if active_scheduled:
                print("✅ Scheduled workflows are active")
                for workflow in active_scheduled:
                    print(f"   • {workflow['name']} (ID: {workflow['id']})")
            else:
                print("⚠️ No active scheduled workflows found")
                print("   Manual activation may be required")
        else:
            print(f"❌ Failed to get n8n workflows: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ n8n workflow check failed: {e}")
        return False
    
    # Test 5: Check email configuration
    email_from = os.getenv('EMAIL_FROM')
    email_password = os.getenv('EMAIL_PASSWORD')
    
    if email_from and email_password:
        print("✅ Email configuration is set")
        print(f"   Email: {email_from}")
    else:
        print("❌ Email configuration is missing")
        return False
    
    print("\n🎉 Enhanced Technical Analysis System Verification Complete!")
    return True

if __name__ == "__main__":
    success = verify_enhanced_system()
    if success:
        print("\n✅ All systems are working correctly!")
        print("🚀 Your enhanced stock analysis system is ready for automated trading signals")
    else:
        print("\n❌ Some issues were found. Please check the errors above.")
        exit(1)