#!/usr/bin/env python3
"""
Fix the HTTP method in the comprehensive workflow
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

N8N_URL = "http://localhost:5678"
API_KEY = os.getenv('N8N_API_KEY')

def get_workflows():
    """Get all workflows to find the comprehensive one"""
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
    if response.status_code == 200:
        workflows = response.json()['data']
        for workflow in workflows:
            if 'Comprehensive' in workflow['name']:
                print(f"Found workflow: {workflow['name']} (ID: {workflow['id']})")
                return workflow['id']
    return None

def fix_workflow_method(workflow_id):
    """Fix the HTTP method in the workflow"""
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Get the current workflow
    response = requests.get(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get workflow: {response.text}")
        return False
    
    workflow_data = response.json()
    
    # Find and fix the HTTP request node
    for node in workflow_data['nodes']:
        if node['type'] == 'n8n-nodes-base.httpRequest':
            print(f"Found HTTP node: {node['name']}")
            print(f"Current method: {node['parameters'].get('requestMethod', 'GET (default)')}")
            
            # Ensure POST method is set
            node['parameters']['requestMethod'] = 'POST'
            print("✅ Fixed method to POST")
    
    # Update the workflow
    response = requests.put(
        f"{N8N_URL}/api/v1/workflows/{workflow_id}",
        json=workflow_data,
        headers=headers
    )
    
    if response.status_code == 200:
        print("✅ Workflow updated successfully!")
        return True
    else:
        print(f"❌ Failed to update workflow: {response.text}")
        return False

if __name__ == "__main__":
    print("🔧 Fixing workflow HTTP method...")
    
    workflow_id = get_workflows()
    if workflow_id:
        if fix_workflow_method(workflow_id):
            print("✅ Workflow fixed! Try running it again.")
        else:
            print("❌ Failed to fix workflow")
    else:
        print("❌ Comprehensive workflow not found")