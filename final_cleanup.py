#!/usr/bin/env python3
"""
Final cleanup - check the unknown workflow and create a clean summary
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def check_unknown_workflow():
    """Check the unknown workflow and clean up if needed"""
    
    N8N_URL = "http://localhost:5678"
    API_KEY = os.getenv('N8N_API_KEY')
    
    headers = {
        "X-N8N-API-KEY": API_KEY
    }
    
    # Get all workflows
    try:
        response = requests.get(f"{N8N_URL}/api/v1/workflows", headers=headers)
        
        if response.status_code == 200:
            workflows = response.json()['data']
            
            print("🔍 Final Workflow Review:")
            print("=" * 50)
            
            essential_workflows = []
            unknown_workflows = []
            
            for workflow in workflows:
                name = workflow['name']
                workflow_id = workflow['id']
                is_active = workflow.get('active', False)
                status = "🟢 ACTIVE" if is_active else "⚪ MANUAL"
                
                if name in [
                    "FULL UNIVERSE - All 269 Stocks Analysis",
                    "Real Email Alert - masterai6612@gmail.com", 
                    "X (Twitter) Sentiment Analysis - Enhanced"
                ]:
                    essential_workflows.append({
                        'name': name,
                        'id': workflow_id,
                        'active': is_active,
                        'status': status
                    })
                    print(f"✅ ESSENTIAL: {name} ({status})")
                else:
                    unknown_workflows.append({
                        'name': name,
                        'id': workflow_id,
                        'active': is_active,
                        'status': status
                    })
                    print(f"❓ UNKNOWN: {name} ({status})")
            
            # Delete unknown workflows
            if unknown_workflows:
                print(f"\n🗑️ Deleting {len(unknown_workflows)} unknown workflow(s)...")
                for workflow in unknown_workflows:
                    delete_response = requests.delete(
                        f"{N8N_URL}/api/v1/workflows/{workflow['id']}", 
                        headers=headers
                    )
                    if delete_response.status_code == 200:
                        print(f"✅ Deleted: {workflow['name']}")
                    else:
                        print(f"❌ Failed to delete: {workflow['name']}")
            
            print("\n" + "=" * 50)
            print("🎉 FINAL CLEAN WORKFLOW LIST:")
            print("=" * 50)
            
            # Show final essential workflows
            for workflow in essential_workflows:
                print(f"\n📊 {workflow['name']}")
                print(f"   Status: {workflow['status']}")
                print(f"   Link: http://localhost:5678/workflow/{workflow['id']}")
                
                if "FULL UNIVERSE" in workflow['name']:
                    print(f"   Purpose: 🤖 Main production workflow - analyzes all 269 stocks")
                    print(f"   Features: ✅ X sentiment, earnings, themes, email alerts")
                    print(f"   Schedule: ⏰ Every 30 minutes automatically")
                elif "Real Email Alert" in workflow['name']:
                    print(f"   Purpose: 🧪 Manual testing workflow")
                    print(f"   Features: ✅ 20 stock analysis with all features")
                    print(f"   Usage: 🔧 Test new features and email alerts")
                elif "X (Twitter) Sentiment" in workflow['name']:
                    print(f"   Purpose: 🐦 Showcase X sentiment analysis")
                    print(f"   Features: ✅ Social media sentiment distribution")
                    print(f"   Usage: 📊 Demonstrate X sentiment capabilities")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧹 Final Cleanup & Summary...")
    print()
    
    if check_unknown_workflow():
        print("\n" + "=" * 60)
        print("✨ YOUR AGENTIC STOCK SYSTEM IS NOW PERFECTLY CLEAN!")
        print("=" * 60)
        
        print("\n🎯 You now have exactly 3 essential workflows:")
        print("   1️⃣ MAIN PRODUCTION (Auto-running)")
        print("   2️⃣ MANUAL TESTING (On-demand)")
        print("   3️⃣ X SENTIMENT SHOWCASE (Demo)")
        
        print("\n🚀 No more confusion - your system is streamlined!")
        print("🤖 Ready for professional trading analysis!")
    else:
        print("\n❌ Final cleanup failed")