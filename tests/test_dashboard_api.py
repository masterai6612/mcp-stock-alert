#!/usr/bin/env python3
"""
Test Dashboard API Endpoints
Quick test to verify all API endpoints are working
"""

import requests
import json
import time

def test_api_endpoint(endpoint, description):
    """Test a single API endpoint"""
    try:
        print(f"🧪 Testing {description}...")
        response = requests.get(f"http://localhost:5001{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}: OK ({len(str(data))} chars)")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {description}: Connection refused (dashboard not running?)")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {description}: Timeout")
        return False
    except Exception as e:
        print(f"❌ {description}: {e}")
        return False

def test_all_endpoints():
    """Test all dashboard API endpoints"""
    print("🔍 DASHBOARD API TEST")
    print("=" * 50)
    
    endpoints = [
        ("/api/status", "System Status"),
        ("/api/stocks", "Top Stocks"),
        ("/api/market", "Market Data"),
        ("/api/earnings", "Earnings Calendar"),
        ("/api/themes", "Investment Themes")
    ]
    
    results = []
    for endpoint, description in endpoints:
        result = test_api_endpoint(endpoint, description)
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
    print("\n📊 TEST SUMMARY:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All API endpoints are working!")
        print("🌐 Dashboard should be fully functional at http://localhost:5001")
    else:
        print("\n⚠️  Some endpoints failed. Check the dashboard logs.")
    
    return all(results)

def test_dashboard_health():
    """Quick health check of the dashboard"""
    try:
        response = requests.get("http://localhost:5001", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard web page is accessible")
            return True
        else:
            print(f"❌ Dashboard returned HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Dashboard health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Stock Alert Dashboard")
    print("=" * 50)
    
    # Test main page
    if test_dashboard_health():
        print()
        # Test API endpoints
        test_all_endpoints()
    else:
        print("\n💡 Make sure the dashboard is running:")
        print("   ./start_dashboard.sh")
        print("   Then try this test again.")