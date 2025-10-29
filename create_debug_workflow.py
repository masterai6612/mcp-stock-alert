#!/usr/bin/env python3
"""
Create a debug workflow to test HTTP methods
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_debug_workflow():
    """Create a workflow to debug HTTP method issues"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "Debug HTTP Methods",
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
                    "method": "POST",  # Try this instead of requestMethod
                    "url": "http://host.docker.internal:5002/api/comprehensive-analysis",
                    "sendBody": True,
                    "contentType": "json",
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"stock_limit\": 3\n}",
                    "options": {
                        "timeout": 30000
                    }
                },
                "name": "POST Test",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,  # Try older version
                "position": [460, 200]
            },
            {
                "parameters": {
                    "requestMethod": "POST",
                    "url": "http://host.docker.internal:5002/api/comprehensive-analysis",
                    "sendBody": True,
                    "bodyContentType": "json",
                    "jsonBody": "{\n  \"analysis_type\": \"full_universe\",\n  \"stock_limit\": 3\n}",
                    "options": {
                        "timeout": 30000
                    }
                },
                "name": "POST Test v4",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 4.1,
                "position": [460, 400]
            }
        ],
        "connections": {
            "Manual Trigger": {
                "main": [
                    [
                        {
                            "node": "POST Test",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "POST Test v4",
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
            print(f"✅ Debug workflow created: {workflow_id}")
            print("This workflow tests different HTTP request configurations")
            return workflow_id
        else:
            print(f"❌ Failed to create debug workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating debug workflow: {e}")
        return None

if __name__ == "__main__":
    print("🔧 Creating debug workflow to test HTTP methods...")
    create_debug_workflow()