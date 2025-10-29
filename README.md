# 🚀 Agentic Stock Alert System

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
