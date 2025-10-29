#!/usr/bin/env python3
"""
Standalone n8n authentication setup script
"""

import requests
import json
import time

def setup_n8n_authentication():
    print("🔑 N8N AUTHENTICATION SETUP")
    print("=" * 30)
    
    base_url = "http://localhost:5678"
    
    # Check if n8n is running
    try:
        response = requests.get(f"{base_url}/healthz", timeout=5)
        print("✅ n8n is running")
    except:
        print("❌ n8n is not running. Please start the system first:")
        print("   ./start_complete_system.sh")
        return False
    
    # Wait for n8n to be ready
    print("⏳ Waiting for n8n to be ready...")
    time.sleep(5)
    
    try:
        # Check current status
        response = requests.get(f"{base_url}/rest/login", timeout=10)
        
        if response.status_code == 200:
            print("✅ n8n is already configured")
            print("🌐 Access: http://localhost:5678")
            print("🔑 Try login: admin@stockagent.local / stockagent123")
            return True
        
        # Check if this is first-time setup
        setup_response = requests.get(f"{base_url}/rest/owner/setup", timeout=10)
        
        if setup_response.status_code == 200:
            print("🆕 Setting up n8n owner account...")
            
            owner_data = {
                "email": "admin@stockagent.local",
                "firstName": "Stock",
                "lastName": "Agent",
                "password": "stockagent123"
            }
            
            create_response = requests.post(
                f"{base_url}/rest/owner/setup",
                json=owner_data,
                timeout=15
            )
            
            if create_response.status_code in [200, 201]:
                print("✅ Owner account created successfully!")
                print("📧 Email: admin@stockagent.local")
                print("🔑 Password: stockagent123")
                print("🌐 Access: http://localhost:5678")
                return True
            else:
                print(f"⚠️ Failed to create account: {create_response.status_code}")
                return False
        else:
            print("🔑 n8n requires manual setup")
            print("💡 Go to: http://localhost:5678")
            print("   Set up your account manually")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Manual setup required:")
        print("   1. Go to: http://localhost:5678")
        print("   2. Follow the setup wizard")
        print("   3. Recommended credentials:")
        print("      Email: admin@stockagent.local")
        print("      Password: stockagent123")
        return False

if __name__ == "__main__":
    setup_n8n_authentication()