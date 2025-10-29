#!/usr/bin/env python3
"""
Create a simple working email workflow that definitely works
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def create_simple_email_workflow():
    """Create a simple email workflow that works with GET requests"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    workflow_data = {
        "name": "Working Email Alert Test",
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
                    "url": "http://host.docker.internal:5002/api/send-email-alert"
                },
                "name": "Send Test Email",
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
                            "node": "Send Test Email",
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
            print(f"✅ Simple email test workflow created!")
            print(f"🔗 Link: http://localhost:5678/workflow/{workflow_id}")
            print()
            print("📧 This workflow will:")
            print("   • Send a test email with sample data")
            print("   • Use the enhanced HTML formatting")
            print("   • Show intelligent subject line")
            print("   • Work with GET requests (no method errors)")
            return workflow_id
        else:
            print(f"❌ Failed to create workflow: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating workflow: {e}")
        return None

if __name__ == "__main__":
    print("📧 Creating simple working email test workflow...")
    create_simple_email_workflow()