#!/usr/bin/env python3
"""
Organize project files into clean folder structure
"""

import os
import shutil
from pathlib import Path

def create_folder_structure():
    """Create organized folder structure"""
    
    folders = {
        'scripts': 'Utility and management scripts',
        'tests': 'Testing and validation scripts', 
        'workflows': 'n8n workflow management',
        'docs': 'Documentation and guides',
        'config': 'Configuration and setup files',
        'utils': 'Helper utilities and tools'
    }
    
    print("📁 Creating folder structure...")
    for folder, description in folders.items():
        os.makedirs(folder, exist_ok=True)
        print(f"   ✅ {folder}/ - {description}")
    
    return folders

def organize_files():
    """Organize files into appropriate folders"""
    
    # File organization mapping
    file_moves = {
        # Scripts folder - System management and utility scripts
        'scripts': [
            'activate_all_workflows.py',
            'activate_email_workflows.py', 
            'cleanup_workflows.py',
            'final_cleanup.py',
            'monitor_system.sh',
            'stop_system.sh',
            'start_dashboard.sh',
            'start_agentic_system.sh',
            'setup_yahoo_finance.sh',
            'start_market_alerts.sh'
        ],
        
        # Tests folder - All testing scripts
        'tests': [
            'test_both_options.py',
            'test_x_sentiment_integration.py',
            'test_direct_api.py',
            'test_dashboard_api.py',
            'test_email_alerts.py',
            'test_mcp_server.py',
            'test_n8n_workflow.py',
            'check_email_alerts.py',
            'check_agentic_system.py',
            'check_alert_status.py'
        ],
        
        # Workflows folder - n8n workflow creation and management
        'workflows': [
            'create_workflow_via_api.py',
            'create_email_workflow.py',
            'create_real_email_workflow.py',
            'create_x_sentiment_workflow.py',
            'create_debug_workflow.py',
            'create_simple_email_workflow.py',
            'create_secure_workflows.py',
            'import_workflows.py',
            'list_workflows.py',
            'update_scheduled_workflow.py',
            'update_to_full_universe.py',
            'add_x_sentiment_to_workflows.py',
            'add_email_to_scheduled_workflow.py',
            'fix_workflow_method.py'
        ],
        
        # Docs folder - Documentation and guides
        'docs': [
            'AGENTIC_N8N_SETUP_GUIDE.md',
            'AGENTIC_SYSTEM_DESIGN.md',
            'STARTUP_GUIDE.md',
            'SECURITY_GUIDE.md',
            'WEB_DASHBOARD_GUIDE.md',
            'MARKET_ALERT_SYSTEM.md',
            'YAHOO_FINANCE_SOLUTION.md',
            'CLEAN_YAHOO_SOLUTION.md',
            'MCP_DEBUG_SOLUTION.md',
            'PRODUCTION_DEPLOYMENT.md',
            'MOOMOO_INTEGRATION_RESEARCH.md',
            'FINAL_SYSTEM_SUMMARY.md',
            'COMPREHENSIVE_SYSTEM_SUMMARY.md',
            'n8n_troubleshooting_guide.md',
            'COMMIT_MESSAGE.md'
        ],
        
        # Config folder - Configuration files
        'config': [
            'docker-compose.yml',
            'gunicorn.conf.py',
            'stock-dashboard.service'
        ],
        
        # Utils folder - Helper utilities
        'utils': [
            'dashboard_features.py',
            'filter_large_caps.py',
            'manage_watchlist.py',
            'stock_change_tracker.py'
        ]
    }
    
    print("\n📦 Moving files to organized folders...")
    
    for folder, files in file_moves.items():
        moved_count = 0
        for file in files:
            if os.path.exists(file):
                try:
                    shutil.move(file, f"{folder}/{file}")
                    moved_count += 1
                except Exception as e:
                    print(f"   ⚠️ Could not move {file}: {e}")
        
        print(f"   ✅ {folder}/: {moved_count} files moved")
    
    # Move n8n-workflows folder to workflows/
    if os.path.exists('n8n-workflows'):
        try:
            if os.path.exists('workflows/n8n-workflows'):
                shutil.rmtree('workflows/n8n-workflows')
            shutil.move('n8n-workflows', 'workflows/n8n-workflows')
            print(f"   ✅ workflows/n8n-workflows/: folder moved")
        except Exception as e:
            print(f"   ⚠️ Could not move n8n-workflows: {e}")
    
    # Move dashboard folder to its own location
    if os.path.exists('dashboard'):
        print(f"   ✅ dashboard/: kept in root (web assets)")

def create_folder_readmes():
    """Create README files for each folder"""
    
    folder_descriptions = {
        'scripts': {
            'title': '🔧 System Management Scripts',
            'description': 'Scripts for starting, stopping, and managing the agentic stock system',
            'key_files': [
                '• monitor_system.sh - Check system status',
                '• stop_system.sh - Clean shutdown',
                '• activate_email_workflows.py - Activate email alerts',
                '• cleanup_workflows.py - Clean up old workflows'
            ]
        },
        'tests': {
            'title': '🧪 Testing & Validation',
            'description': 'Scripts to test system components and validate functionality',
            'key_files': [
                '• test_both_options.py - Test script and n8n options',
                '• test_x_sentiment_integration.py - Test X sentiment',
                '• check_email_alerts.py - Verify email configuration',
                '• test_direct_api.py - Test API endpoints'
            ]
        },
        'workflows': {
            'title': '🔄 n8n Workflow Management',
            'description': 'Scripts for creating, updating, and managing n8n workflows',
            'key_files': [
                '• create_workflow_via_api.py - Create workflows programmatically',
                '• n8n-workflows/ - Workflow JSON definitions',
                '• update_to_full_universe.py - Update to analyze all stocks',
                '• create_x_sentiment_workflow.py - X sentiment workflows'
            ]
        },
        'docs': {
            'title': '📚 Documentation & Guides',
            'description': 'Complete documentation for setup, usage, and system design',
            'key_files': [
                '• STARTUP_GUIDE.md - Quick start after restart',
                '• AGENTIC_SYSTEM_DESIGN.md - System architecture',
                '• SECURITY_GUIDE.md - Security best practices',
                '• WEB_DASHBOARD_GUIDE.md - Dashboard usage'
            ]
        },
        'config': {
            'title': '⚙️ Configuration Files',
            'description': 'System configuration and deployment files',
            'key_files': [
                '• docker-compose.yml - Docker services configuration',
                '• gunicorn.conf.py - Production server configuration',
                '• stock-dashboard.service - Systemd service file'
            ]
        },
        'utils': {
            'title': '🛠️ Utility Functions',
            'description': 'Helper utilities and support functions',
            'key_files': [
                '• dashboard_features.py - Dashboard utilities',
                '• filter_large_caps.py - Stock filtering',
                '• manage_watchlist.py - Watchlist management'
            ]
        }
    }
    
    print("\n📝 Creating folder documentation...")
    
    for folder, info in folder_descriptions.items():
        readme_content = f"""# {info['title']}

{info['description']}

## Key Files

{chr(10).join(info['key_files'])}

## Usage

Run scripts from the project root directory:
```bash
# Example
python {folder}/script_name.py
```

## Note

These files have been organized for better project structure. 
All scripts should still be run from the main project directory.
"""
        
        with open(f"{folder}/README.md", 'w') as f:
            f.write(readme_content)
        
        print(f"   ✅ {folder}/README.md created")

def update_startup_script():
    """Update the startup script to reference new file locations"""
    
    print("\n🔄 Updating startup script references...")
    
    # The startup script should still work since we're running from root
    # But let's create a note about the new structure
    
    note = """
# 📁 PROJECT ORGANIZATION NOTE
# 
# Files have been organized into folders:
# • scripts/ - System management scripts  
# • tests/ - Testing and validation
# • workflows/ - n8n workflow management
# • docs/ - Documentation and guides
# • config/ - Configuration files
# • utils/ - Helper utilities
#
# All scripts should still be run from the project root directory.
"""
    
    # Add note to startup script
    with open('start_complete_system.sh', 'r') as f:
        content = f.read()
    
    if '# PROJECT ORGANIZATION NOTE' not in content:
        # Insert note after the initial comment
        lines = content.split('\n')
        insert_pos = 3  # After the initial comments
        lines.insert(insert_pos, note)
        
        with open('start_complete_system.sh', 'w') as f:
            f.write('\n'.join(lines))
        
        print("   ✅ Added organization note to startup script")

def create_root_readme():
    """Create a clean root README"""
    
    readme_content = """# 🚀 Agentic Stock Alert System

## Quick Start

```bash
# Start the complete system after laptop restart
./start_complete_system.sh

# Test both options are working
python tests/test_both_options.py
```

## Project Structure

```
📁 Project Root
├── 🚀 start_complete_system.sh    # Main startup script
├── 📊 Core System Files
│   ├── main.py                    # Core analysis engine
│   ├── main_enhanced.py           # Enhanced analysis
│   ├── n8n_integration.py         # n8n API server
│   ├── stock_universe.py          # 269+ stock universe
│   └── enhanced_yahoo_client.py   # Yahoo Finance client
├── 📁 scripts/                    # System management
├── 📁 tests/                      # Testing & validation  
├── 📁 workflows/                  # n8n workflow management
├── 📁 docs/                       # Documentation & guides
├── 📁 config/                     # Configuration files
├── 📁 utils/                      # Helper utilities
└── 📁 dashboard/                  # Web dashboard assets
```

## Your Two Options

### 1️⃣ Script-Based (Manual)
```bash
python main_enhanced.py
```

### 2️⃣ n8n Workflow (Automated)
- Access: http://localhost:5678 (admin/stockagent123)
- Runs every 30 minutes automatically

## Email Alerts

Professional HTML emails sent to: **masterai6612@gmail.com**

Features:
- 🐦 X (Twitter) sentiment analysis
- 📅 Earnings calendar integration  
- 🔥 Investment themes analysis
- 📊 Technical indicators (RSI, volume)
- 🎨 Color-coded buy signals

## System Management

```bash
./scripts/monitor_system.sh    # Check status
./scripts/stop_system.sh       # Clean shutdown
python tests/test_both_options.py  # Validate system
```

## Documentation

- 📋 **Quick Start**: [docs/STARTUP_GUIDE.md](docs/STARTUP_GUIDE.md)
- 🏗️ **System Design**: [docs/AGENTIC_SYSTEM_DESIGN.md](docs/AGENTIC_SYSTEM_DESIGN.md)
- 🔒 **Security**: [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)
- 🌐 **Dashboard**: [docs/WEB_DASHBOARD_GUIDE.md](docs/WEB_DASHBOARD_GUIDE.md)

---

**🤖 Your institutional-level agentic trading system analyzing 269+ stocks with X sentiment integration!** 📈✨
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    
    print("   ✅ Created clean root README.md")

if __name__ == "__main__":
    print("🗂️ Organizing Agentic Stock Alert System...")
    print("=" * 60)
    
    # Create folder structure
    create_folder_structure()
    
    # Move files to appropriate folders
    organize_files()
    
    # Create documentation for each folder
    create_folder_readmes()
    
    # Update startup script
    update_startup_script()
    
    # Create clean root README
    create_root_readme()
    
    print("\n" + "=" * 60)
    print("✅ PROJECT ORGANIZATION COMPLETE!")
    print("=" * 60)
    
    print("\n📁 Clean Project Structure:")
    print("   🚀 start_complete_system.sh - Main startup script")
    print("   📊 Core system files (main.py, n8n_integration.py, etc.)")
    print("   📁 scripts/ - System management")
    print("   📁 tests/ - Testing & validation")
    print("   📁 workflows/ - n8n workflow management")
    print("   📁 docs/ - Documentation & guides")
    print("   📁 config/ - Configuration files")
    print("   📁 utils/ - Helper utilities")
    
    print("\n🎯 Usage:")
    print("   • Start system: ./start_complete_system.sh")
    print("   • Test system: python tests/test_both_options.py")
    print("   • Monitor: ./scripts/monitor_system.sh")
    print("   • Stop: ./scripts/stop_system.sh")
    
    print("\n✨ Your project is now clean and professionally organized!")