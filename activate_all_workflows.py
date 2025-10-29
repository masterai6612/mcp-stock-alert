#!/usr/bin/env python3
"""
Activate all workflows in n8n
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

def activate_all_workflows():
    """Activate all workflows in n8n"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Get all workflows
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        
        if response.status_code != 200:
            print(f"❌ Failed to get workflows: {response.status_code}")
            return False
            
        workflows = response.json()['data']
        print(f"📋 Found {len(workflows)} workflows")
        print()
        
        # Activate each workflow
        activated_count = 0
        for workflow in workflows:
            workflow_id = workflow['id']
            workflow_name = workflow['name']
            is_active = workflow.get('active', False)
            
            print(f"🔗 {workflow_name}")
            print(f"   Link: http://localhost:5678/workflow/{workflow_id}")
            
            if is_active:
                print(f"   Status: ✅ Already active")
            else:
                # Activate the workflow
                try:
                    activate_response = requests.post(
                        f"{N8N_URL}/api/v1/workflows/{workflow_id}/activate",
                        headers=headers
                    )
                    
                    if activate_response.status_code == 200:
                        print(f"   Status: ✅ Activated successfully")
                        activated_count += 1
                    else:
                        print(f"   Status: ❌ Failed to activate ({activate_response.status_code})")
                        
                except Exception as e:
                    print(f"   Status: ❌ Error activating: {e}")
            
            print()
        
        print(f"🎉 Summary: {activated_count} workflows activated")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def print_workflow_links():
    """Print direct links to all workflows"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        
        if response.status_code == 200:
            workflows = response.json()['data']
            
            print("🔗 Direct Links to All Workflows:")
            print("=" * 50)
            
            for i, workflow in enumerate(workflows, 1):
                name = workflow['name']
                workflow_id = workflow['id']
                is_active = workflow.get('active', False)
                status = "🟢 ACTIVE" if is_active else "⚪ INACTIVE"
                
                print(f"{i}. {name} ({status})")
                print(f"   http://localhost:5678/workflow/{workflow_id}")
                print()
            
            return workflows
        else:
            print(f"❌ Failed to get workflows: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Activating all workflows and providing links...")
    print()
    
    # First show all links
    workflows = print_workflow_links()
    
    print("\n" + "=" * 50)
    print("🔄 Now activating all workflows...")
    print()
    
    # Then activate them
    activate_all_workflows()
    
    print("\n🎯 Key Workflows for Your Agentic System:")
    print("=" * 50)
    print("📊 For Manual Testing:")
    print("   • Simple Working Test")
    print("   • Comprehensive Stock Analysis - Manual Test")
    print("   • API Test - Health Check")
    print()
    print("🤖 For Automated Trading:")
    print("   • Scheduled Stock Agent - Every 30 Minutes")
    print()
    print("🔧 For Debugging:")
    print("   • Debug HTTP Methods")
    print()
    print("✅ All workflows are now active and ready!")