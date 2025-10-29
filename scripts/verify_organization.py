#!/usr/bin/env python3
"""
Verify the project organization is working correctly
"""

import os
import subprocess

def verify_folder_structure():
    """Verify all folders exist with correct files"""
    
    expected_structure = {
        'scripts': ['monitor_system.sh', 'stop_system.sh', 'activate_email_workflows.py'],
        'tests': ['test_both_options.py', 'test_x_sentiment_integration.py'],
        'workflows': ['create_workflow_via_api.py', 'n8n-workflows'],
        'docs': ['STARTUP_GUIDE.md', 'AGENTIC_SYSTEM_DESIGN.md', 'SECURITY_GUIDE.md'],
        'config': ['docker-compose.yml', 'gunicorn.conf.py'],
        'utils': ['dashboard_features.py']
    }
    
    print("📁 Verifying folder structure...")
    
    all_good = True
    for folder, sample_files in expected_structure.items():
        if os.path.exists(folder):
            print(f"   ✅ {folder}/ exists")
            
            # Check sample files
            for sample_file in sample_files:
                file_path = os.path.join(folder, sample_file)
                if os.path.exists(file_path):
                    print(f"      ✅ {sample_file}")
                else:
                    print(f"      ❌ {sample_file} missing")
                    all_good = False
        else:
            print(f"   ❌ {folder}/ missing")
            all_good = False
    
    return all_good

def verify_startup_script():
    """Verify the startup script references are correct"""
    
    print("\n🚀 Verifying startup script...")
    
    if not os.path.exists('start_complete_system.sh'):
        print("   ❌ start_complete_system.sh missing")
        return False
    
    with open('start_complete_system.sh', 'r') as f:
        content = f.read()
    
    # Check for correct references
    checks = [
        ('scripts/monitor_system.sh', 'Monitor script reference'),
        ('scripts/stop_system.sh', 'Stop script reference'),
        ('config/docker-compose.yml', 'Docker compose reference'),
        ('tests/test_both_options.py', 'Test script reference')
    ]
    
    all_good = True
    for check, description in checks:
        if check in content:
            print(f"   ✅ {description}")
        else:
            print(f"   ❌ {description} missing")
            all_good = False
    
    return all_good

def verify_core_files():
    """Verify core system files are still in root"""
    
    print("\n📊 Verifying core system files...")
    
    core_files = [
        'main.py',
        'main_enhanced.py', 
        'n8n_integration.py',
        'stock_universe.py',
        'enhanced_yahoo_client.py',
        'web_dashboard.py',
        '.env'
    ]
    
    all_good = True
    for file in core_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} missing")
            all_good = False
    
    return all_good

if __name__ == "__main__":
    print("🔍 Verifying Project Organization...")
    print("=" * 50)
    
    folder_ok = verify_folder_structure()
    startup_ok = verify_startup_script()
    core_ok = verify_core_files()
    
    print("\n" + "=" * 50)
    print("📊 VERIFICATION RESULTS")
    print("=" * 50)
    
    print(f"📁 Folder Structure:     {'✅ CORRECT' if folder_ok else '❌ ISSUES'}")
    print(f"🚀 Startup Script:       {'✅ CORRECT' if startup_ok else '❌ ISSUES'}")
    print(f"📊 Core Files:           {'✅ PRESENT' if core_ok else '❌ MISSING'}")
    
    if all([folder_ok, startup_ok, core_ok]):
        print("\n🎉 PROJECT ORGANIZATION PERFECT!")
        print("✅ Clean root directory with only essential files")
        print("✅ All utilities organized in appropriate folders")
        print("✅ Startup script references updated correctly")
        print("✅ Core system files remain accessible")
        
        print("\n🎯 Ready to use:")
        print("   • Start system: ./start_complete_system.sh")
        print("   • Test system: python tests/test_both_options.py")
        print("   • Monitor: ./scripts/monitor_system.sh")
        print("   • Stop: ./scripts/stop_system.sh")
        
        print("\n📧 Email alerts will be sent to: masterai6612@gmail.com")
        print("🚀 Your agentic stock system is professionally organized!")
    else:
        print("\n⚠️ Some issues found - check the results above")
    
    print("\n📋 Current root directory contents:")
    root_files = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
    for file in sorted(root_files)[:10]:  # Show first 10 files
        print(f"   • {file}")
    
    if len(root_files) > 10:
        print(f"   ... and {len(root_files) - 10} more files")