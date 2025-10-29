#!/usr/bin/env python3
"""
Clean up unwanted workflows to avoid confusion
Keep only the essential, working workflows
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_all_workflows():
    """Get all workflows from n8n"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        
        if response.status_code == 200:
            workflows = response.json()['data']
            return workflows
        else:
            print(f"❌ Failed to get workflows: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error getting workflows: {e}")
        return []

def delete_workflow(workflow_id, workflow_name):
    """Delete a workflow"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    try:
        response = requests.delete(f"{N8N_URL}/api/v1/workflows/{workflow_id}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Deleted: {workflow_name}")
            return True
        else:
            print(f"❌ Failed to delete {workflow_name}: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting {workflow_name}: {e}")
        return False

def cleanup_workflows():
    """Clean up unwanted workflows"""
    
    print("🧹 Cleaning up workflows...")
    print("=" * 60)
    
    workflows = get_all_workflows()
    
    if not workflows:
        print("❌ No workflows found")
        return
    
    # Define essential workflows to KEEP
    essential_workflows = [
        "FULL UNIVERSE - All 269 Stocks Analysis",  # Main production workflow
        "Real Email Alert - masterai6612@gmail.com",  # Manual email test
        "X (Twitter) Sentiment Analysis - Enhanced",  # X sentiment showcase
    ]
    
    # Define workflows to DELETE (old/redundant/test workflows)
    workflows_to_delete = [
        "My workflow",
        "My workflow 2", 
        "Simple Working Test",
        "Debug HTTP Methods",
        "Stock Alert Agent Workflow",
        "Simple Stock Alert Workflow",
        "Scheduled Stock Agent - Every 30 Minutes",  # Old version, replaced by FULL UNIVERSE
        "Comprehensive Stock Analysis - Manual Test",  # Redundant
        "Enhanced Email Alert System",  # Redundant
        "Working Email Alert Test",  # Test workflow
        "API Test - Health Check",  # Basic test
        "API Created Test Workflow",  # Old test
        "Simple Comprehensive Test",  # Old test
        "Minimal Comprehensive Agent",  # Old version
    ]
    
    print("📋 Current workflows:")
    for i, workflow in enumerate(workflows, 1):
        name = workflow['name']
        is_active = workflow.get('active', False)
        status = "🟢 ACTIVE" if is_active else "⚪ INACTIVE"
        
        if name in essential_workflows:
            print(f"{i:2d}. ✅ KEEP: {name} ({status})")
        elif name in workflows_to_delete:
            print(f"{i:2d}. 🗑️  DELETE: {name} ({status})")
        else:
            print(f"{i:2d}. ❓ REVIEW: {name} ({status})")
    
    print("\n" + "=" * 60)
    print("🗑️  Deleting unwanted workflows...")
    print("-" * 30)
    
    deleted_count = 0
    for workflow in workflows:
        if workflow['name'] in workflows_to_delete:
            if delete_workflow(workflow['id'], workflow['name']):
                deleted_count += 1
    
    print("-" * 30)
    print(f"🧹 Deleted {deleted_count} unwanted workflows")
    
    # Show remaining workflows
    print("\n✅ Essential workflows remaining:")
    remaining_workflows = get_all_workflows()
    
    for workflow in remaining_workflows:
        name = workflow['name']
        workflow_id = workflow['id']
        is_active = workflow.get('active', False)
        status = "🟢 ACTIVE" if is_active else "⚪ MANUAL"
        
        print(f"   • {name} ({status})")
        print(f"     http://localhost:5678/workflow/{workflow_id}")
        print()
    
    return deleted_count

if __name__ == "__main__":
    print("🧹 Cleaning Up n8n Workflows...")
    print("Removing old, redundant, and test workflows")
    print()
    
    deleted_count = cleanup_workflows()
    
    print("=" * 60)
    print("🎉 CLEANUP COMPLETE!")
    print("=" * 60)
    
    if deleted_count > 0:
        print(f"\n✅ Removed {deleted_count} unwanted workflows")
        print("\n🎯 Your clean, essential workflows:")
        print("   1. FULL UNIVERSE - All 269 Stocks Analysis (MAIN)")
        print("      • Analyzes all 269 stocks every 30 minutes")
        print("      • Includes X sentiment, earnings, themes")
        print("      • Sends email alerts to masterai6612@gmail.com")
        print()
        print("   2. Real Email Alert - masterai6612@gmail.com (MANUAL TEST)")
        print("      • Manual trigger for testing email alerts")
        print("      • Analyzes 20 stocks with full features")
        print("      • Perfect for testing new features")
        print()
        print("   3. X (Twitter) Sentiment Analysis - Enhanced (SHOWCASE)")
        print("      • Demonstrates X sentiment analysis")
        print("      • Shows social media sentiment distribution")
        print("      • Highlights bullish/bearish trends")
        
        print("\n🚀 Your agentic system is now clean and focused!")
        print("No more confusion - just the essential workflows!")
    else:
        print("\n⚠️ No workflows were deleted")
        print("Your workflows may already be clean")