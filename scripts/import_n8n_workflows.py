#!/usr/bin/env python3
"""
Import n8n workflows automatically
"""
import requests
import json
import time
import os
import glob
from pathlib import Path

def wait_for_n8n(max_attempts=30):
    """Wait for n8n to be ready"""
    print("⏳ Waiting for n8n to be ready...")
    for attempt in range(max_attempts):
        try:
            response = requests.get('http://localhost:5678/healthz', timeout=5)
            if response.status_code == 200:
                print("✅ n8n is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"   Attempt {attempt + 1}/{max_attempts}...")
        time.sleep(2)
    
    print("❌ n8n failed to become ready")
    return False

def setup_n8n_owner():
    """Setup n8n owner account"""
    print("🔧 Setting up n8n owner account...")
    
    # Check if owner exists
    try:
        response = requests.get('http://localhost:5678/rest/owner/setup', timeout=10)
        if response.status_code == 200:
            setup_data = response.json()
            if not setup_data.get('data', {}).get('hasOwner', False):
                # Setup owner
                owner_data = {
                    "email": "masterai6612@gmail.com",
                    "firstName": "Stock",
                    "lastName": "Agent",
                    "password": "stockagent123"
                }
                
                setup_response = requests.post(
                    'http://localhost:5678/rest/owner/setup',
                    json=owner_data,
                    timeout=10
                )
                
                if setup_response.status_code == 200:
                    print("✅ n8n owner account created successfully")
                    return True
                else:
                    print(f"❌ Failed to create owner: {setup_response.status_code}")
                    return False
            else:
                print("✅ n8n owner already exists")
                return True
    except Exception as e:
        print(f"❌ Error setting up owner: {e}")
        return False

def get_auth_cookie():
    """Get authentication cookie"""
    print("🔑 Getting authentication...")
    
    try:
        # Login
        login_data = {
            "email": "masterai6612@gmail.com",
            "password": "stockagent123"
        }
        
        response = requests.post(
            'http://localhost:5678/rest/login',
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Authentication successful")
            return response.cookies
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Authentication error: {e}")
        return None

def import_workflow(workflow_file, cookies):
    """Import a single workflow"""
    print(f"📥 Importing workflow: {workflow_file}")
    
    try:
        with open(workflow_file, 'r') as f:
            workflow_data = json.load(f)
        
        # Import workflow
        response = requests.post(
            'http://localhost:5678/rest/workflows/import',
            json=workflow_data,
            cookies=cookies,
            timeout=30
        )
        
        if response.status_code in [200, 201]:
            print(f"✅ Successfully imported: {os.path.basename(workflow_file)}")
            return True
        else:
            print(f"❌ Failed to import {workflow_file}: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error importing {workflow_file}: {e}")
        return False

def main():
    print("🚀 N8N WORKFLOW IMPORT TOOL")
    print("=" * 50)
    
    # Wait for n8n
    if not wait_for_n8n():
        return False
    
    # Setup owner
    if not setup_n8n_owner():
        return False
    
    # Get authentication
    cookies = get_auth_cookie()
    if not cookies:
        return False
    
    # Find workflow files
    workflow_dir = Path("workflows/n8n-workflows")
    if not workflow_dir.exists():
        print(f"❌ Workflow directory not found: {workflow_dir}")
        return False
    
    workflow_files = list(workflow_dir.glob("*.json"))
    if not workflow_files:
        print(f"❌ No workflow files found in {workflow_dir}")
        return False
    
    print(f"📁 Found {len(workflow_files)} workflow files")
    
    # Import workflows
    success_count = 0
    for workflow_file in workflow_files:
        if import_workflow(workflow_file, cookies):
            success_count += 1
        time.sleep(1)  # Small delay between imports
    
    print("=" * 50)
    print(f"✅ Import complete: {success_count}/{len(workflow_files)} workflows imported")
    
    if success_count > 0:
        print("\n🌐 Access your workflows at:")
        print("   URL: http://localhost:5678")
        print("   Email: masterai6612@gmail.com")
        print("   Password: stockagent123")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)