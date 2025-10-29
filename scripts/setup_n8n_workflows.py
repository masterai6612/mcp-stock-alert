#!/usr/bin/env python3
"""
Setup n8n workflows with authentication and automatic account creation
"""

import requests
import json
import os
import time
from pathlib import Path

def setup_n8n_workflows():
    print("🔧 SETTING UP N8N WORKFLOWS & AUTHENTICATION")
    print("=" * 50)
    
    base_url = "http://localhost:5678"
    
    # Check if n8n is running
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print("✅ n8n is running")
    except:
        print("❌ n8n is not running. Please start the system first:")
        print("   ./start_complete_system.sh")
        return False
    
    # Wait for n8n to be fully ready
    print("⏳ Waiting for n8n to be fully ready...")
    time.sleep(8)
    
    # Try to setup authentication first
    session = setup_authentication(base_url)
    
    if session:
        print("✅ Authentication successful")
        # Try to import workflows with authenticated session
        return import_workflows_with_auth(base_url, session)
    else:
        # Fallback to manual instructions
        return provide_manual_instructions()

def setup_authentication(base_url):
    """Try to setup n8n authentication"""
    print("🔑 Setting up n8n authentication...")
    
    try:
        # Check if n8n is already set up
        response = requests.get(f"{base_url}/rest/login", timeout=10)
        
        if response.status_code == 200:
            print("✅ n8n is already configured")
            return try_login(base_url)
        
        # Check if this is first-time setup
        setup_response = requests.get(f"{base_url}/rest/owner/setup", timeout=10)
        
        if setup_response.status_code == 200:
            print("🆕 Setting up n8n for first time...")
            return setup_owner_account(base_url)
        else:
            print("🔑 n8n requires login")
            return try_login(base_url)
            
    except Exception as e:
        print(f"⚠️ Authentication setup failed: {e}")
        return None

def setup_owner_account(base_url):
    """Setup the owner account for first-time n8n installation"""
    try:
        owner_data = {
            "email": "admin@stockagent.local",
            "firstName": "Stock",
            "lastName": "Agent",
            "password": "stockagent123"
        }
        
        response = requests.post(
            f"{base_url}/rest/owner/setup",
            json=owner_data,
            timeout=15
        )
        
        if response.status_code in [200, 201]:
            print("✅ Owner account created successfully")
            print("📧 Email: admin@stockagent.local")
            print("🔑 Password: stockagent123")
            
            # Login with the new account
            return login_with_credentials(base_url, "admin@stockagent.local", "stockagent123")
        else:
            print(f"⚠️ Failed to create owner account: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating owner account: {e}")
        return None

def try_login(base_url):
    """Try to login with default credentials"""
    credentials = [
        ("admin@stockagent.local", "stockagent123"),
        ("admin", "stockagent123"),
        ("admin@localhost", "admin"),
    ]
    
    for email, password in credentials:
        session = login_with_credentials(base_url, email, password)
        if session:
            return session
    
    print("⚠️ Could not login with default credentials")
    return None

def login_with_credentials(base_url, email, password):
    """Login with specific credentials"""
    try:
        login_data = {
            "email": email,
            "password": password
        }
        
        session = requests.Session()
        response = session.post(
            f"{base_url}/rest/login",
            json=login_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✅ Logged in successfully as: {email}")
            return session
        else:
            return None
            
    except Exception as e:
        return None

def import_workflows_with_auth(base_url, session):
    """Import workflows using authenticated session"""
    workflow_dir = Path("workflows/n8n-workflows")
    
    if not workflow_dir.exists():
        print("❌ Workflow directory not found")
        return False
    
    imported_count = 0
    failed_count = 0
    
    print("📥 Importing workflows with authentication...")
    
    for workflow_file in workflow_dir.glob("*.json"):
        try:
            print(f"   Importing: {workflow_file.name}")
            
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            
            # Try to import using authenticated session
            response = session.post(
                f"{base_url}/rest/workflows",
                json=workflow_data,
                timeout=15
            )
            
            if response.status_code in [200, 201]:
                print(f"   ✅ Successfully imported: {workflow_file.name}")
                imported_count += 1
            else:
                print(f"   ⚠️ Failed to import: {workflow_file.name} (Status: {response.status_code})")
                failed_count += 1
                
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error with {workflow_file.name}: {e}")
            failed_count += 1
    
    print()
    print("📊 IMPORT SUMMARY")
    print("=" * 20)
    print(f"✅ Successfully imported: {imported_count}")
    if failed_count > 0:
        print(f"⚠️ Failed to import: {failed_count}")
    
    if imported_count > 0:
        print()
        print("🎉 Workflows are now available in n8n!")
        print("🌐 Access them at: http://localhost:5678/workflows")
        print("🔑 Login: admin@stockagent.local / stockagent123")
    
    return imported_count > 0

def provide_manual_instructions():
    """Provide manual import instructions"""
    print("🔑 n8n requires manual setup")
    print("💡 Manual setup required:")
    print()
    print("1. Go to: http://localhost:5678")
    print("2. Set up your account (if first time)")
    print("   • Email: admin@stockagent.local")
    print("   • Password: stockagent123")
    print("3. Go to Workflows section")
    print("4. Click 'Import from File'")
    print("5. Import files from: workflows/n8n-workflows/")
    print()
    
    # List available workflows
    workflow_dir = Path("workflows/n8n-workflows")
    if workflow_dir.exists():
        print("📁 Available workflow files:")
        for workflow_file in workflow_dir.glob("*.json"):
            print(f"   • {workflow_file.name}")
        print()
        
        print("🎯 Recommended workflows to import:")
        print("   • comprehensive-stock-agent.json - Full 269+ stock analysis")
        print("   • minimal-comprehensive-agent.json - Lightweight version")
        print("   • manual-comprehensive-test.json - Manual testing")
        print()
    
    return True

def import_workflows_programmatically(base_url):
    """Try to import workflows programmatically"""
    workflow_dir = Path("workflows/n8n-workflows")
    
    if not workflow_dir.exists():
        print("❌ Workflow directory not found")
        return False
    
    imported_count = 0
    failed_count = 0
    
    print("📥 Importing workflows...")
    
    for workflow_file in workflow_dir.glob("*.json"):
        try:
            print(f"   Importing: {workflow_file.name}")
            
            with open(workflow_file, 'r') as f:
                workflow_data = json.load(f)
            
            # Try different import endpoints
            endpoints = [
                "/rest/workflows/import",
                "/rest/workflows",
                "/api/v1/workflows/import"
            ]
            
            success = False
            for endpoint in endpoints:
                try:
                    response = requests.post(
                        f"{base_url}{endpoint}",
                        json=workflow_data,
                        headers={"Content-Type": "application/json"},
                        timeout=10
                    )
                    
                    if response.status_code in [200, 201]:
                        print(f"   ✅ Successfully imported: {workflow_file.name}")
                        imported_count += 1
                        success = True
                        break
                        
                except Exception as e:
                    continue
            
            if not success:
                print(f"   ⚠️ Failed to import: {workflow_file.name}")
                failed_count += 1
                
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error with {workflow_file.name}: {e}")
            failed_count += 1
    
    print()
    print("📊 IMPORT SUMMARY")
    print("=" * 20)
    print(f"✅ Successfully imported: {imported_count}")
    if failed_count > 0:
        print(f"⚠️ Failed to import: {failed_count}")
    
    return imported_count > 0

if __name__ == "__main__":
    setup_n8n_workflows()