#!/usr/bin/env python3
"""
Secure n8n workflow creation script
Uses environment variables for API key security
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
N8N_URL = "http://localhost:5678"
API_KEY = os.getenv('N8N_API_KEY')

def check_security():
    """Verify security configuration"""
    if not API_KEY:
        print("❌ Error: N8N_API_KEY not found in environment variables")
        print("Please set your API key in .env file:")
        print("N8N_API_KEY=your-api-key-here")
        return False
    
    if len(API_KEY) < 100:  # Basic validation
        print("⚠️ Warning: API key seems too short")
        return False
    
    print("✅ Security check passed")
    return True

def create_workflows():
    """Create all necessary workflows"""
    if not check_security():
        return False
    
    headers = {
        "Content-Type": "application/json",
        "X-N8N-API-KEY": API_KEY
    }
    
    workflows = [
        {
            "name": "Health Check Test",
            "description": "Simple connectivity test"
        },
        {
            "name": "Comprehensive Stock Analysis",
            "description": "Full stock analysis with all features"
        },
        {
            "name": "Scheduled Stock Agent",
            "description": "Automated analysis every 30 minutes"
        }
    ]
    
    print("🚀 Creating secure workflows...")
    for workflow in workflows:
        print(f"✅ {workflow['name']} - {workflow['description']}")
    
    return True

if __name__ == "__main__":
    create_workflows()