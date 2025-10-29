#!/usr/bin/env python3
"""
List all workflows in n8n to see what's available
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def list_all_workflows():
    """List all workflows in n8n"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        
        if response.status_code == 200:
            workflows = response.json()['data']
            print(f"📋 Found {len(workflows)} workflows in n8n:")
            print()
            
            for i, workflow in enumerate(workflows, 1):
                print(f"{i}. {workflow['name']}")
                print(f"   ID: {workflow['id']}")
                print(f"   Active: {workflow.get('active', False)}")
                print(f"   Created: {workflow.get('createdAt', 'Unknown')}")
                print()
            
            return workflows
        else:
            print(f"❌ Failed to get workflows: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return []

if __name__ == "__main__":
    print("🔍 Listing all workflows in n8n...")
    list_all_workflows()