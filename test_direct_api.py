#!/usr/bin/env python3
"""
Test the API directly to make sure it works, then create a simple working workflow
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_api_directly():
    """Test our API directly"""
    print("🧪 Testing API directly...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5002/health")
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # Test comprehensive analysis
    try:
        data = {
            "analysis_type": "full_universe",
            "include_earnings": True,
            "include_themes": True,
            "stock_limit": 3
        }
        
        response = requests.post(
            "http://localhost:5002/api/comprehensive-analysis",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Comprehensive analysis passed")
            print(f"📊 Analyzed {result.get('total_analyzed', 0)} stocks")
            print(f"🎯 Market sentiment: {result.get('market_context', {}).get('sentiment', 'Unknown')}")
            return True
        else:
            print(f"❌ Comprehensive analysis failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Comprehensive analysis error: {e}")
        return False

def create_simple_working_workflow():
    """Create a very simple workflow that definitely works"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "Simple Working Test",
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
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"stock_limit\": 5\n}"
                },
                "name": "Test Analysis",
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
                            "node": "Test Analysis",
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
            print(f"✅ Simple working workflow created: {workflow_id}")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing and fixing workflow issues...")
    
    # First test API directly
    if test_api_directly():
        print("\n✅ API is working correctly")
        
        # Create a simple working workflow
        workflow_id = create_simple_working_workflow()
        if workflow_id:
            print(f"\n🎉 Success! Try the 'Simple Working Test' workflow in n8n")
            print("This workflow should work without any method errors")
        else:
            print("\n❌ Failed to create working workflow")
    else:
        print("\n❌ API has issues - need to fix server first")