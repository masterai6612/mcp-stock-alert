#!/usr/bin/env python3
"""
Script to help import n8n workflows
"""

import requests
import json
import os

def import_workflow_to_n8n(workflow_file, n8n_url="http://localhost:5678"):
    """Import a workflow JSON file to n8n"""
    
    if not os.path.exists(workflow_file):
        print(f"❌ Workflow file not found: {workflow_file}")
        return False
    
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        print(f"📁 Importing workflow: {workflow_data.get('name', 'Unknown')}")
        
        # n8n API endpoint for importing workflows
        import_url = f"{n8n_url}/rest/workflows/import"
        
        response = requests.post(
            import_url,
            json=workflow_data,
            auth=("admin", "stockagent123"),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Successfully imported: {workflow_data.get('name')}")
            return True
        else:
            print(f"❌ Import failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing workflow: {e}")
        return False

def main():
    print("🔄 n8n Workflow Import Helper")
    print("=" * 40)
    
    workflows_dir = "n8n-workflows"
    
    if not os.path.exists(workflows_dir):
        print(f"❌ Workflows directory not found: {workflows_dir}")
        return
    
    workflow_files = [f for f in os.listdir(workflows_dir) if f.endswith('.json')]
    
    if not workflow_files:
        print(f"❌ No workflow files found in {workflows_dir}")
        return
    
    print(f"📂 Found {len(workflow_files)} workflow files:")
    for wf in workflow_files:
        print(f"   - {wf}")
    
    print()
    print("🌐 Manual Import Instructions:")
    print("=" * 30)
    print("1. Open n8n at http://localhost:5678")
    print("2. Login with admin/stockagent123")
    print("3. Click 'Import from File' or use the '+' button")
    print("4. Upload the JSON files from n8n-workflows/ directory")
    print("5. Activate the workflows after import")
    print()
    
    print("📋 Available Workflows:")
    for workflow_file in workflow_files:
        filepath = os.path.join(workflows_dir, workflow_file)
        try:
            with open(filepath, 'r') as f:
                workflow_data = json.load(f)
            print(f"   📊 {workflow_data.get('name', workflow_file)}")
            print(f"      File: {workflow_file}")
            print(f"      Nodes: {len(workflow_data.get('nodes', []))}")
            print()
        except Exception as e:
            print(f"   ❌ Error reading {workflow_file}: {e}")
    
    print("🎯 After importing workflows, test them by:")
    print("1. Triggering the Stock Alert workflow manually")
    print("2. Checking the Market Monitor workflow runs every 15 minutes")
    print("3. Monitoring execution logs in n8n interface")

if __name__ == "__main__":
    main()