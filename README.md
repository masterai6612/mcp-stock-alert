# 🚀 MCP Stock Alert Agent

A production-ready automated stock monitoring and alert system with MCP (Model Context Protocol) integration, designed for swing trading and real-time market analytics.

## 🎯 Quick Start

### Local Development
```bash
# Setup and start the complete system
./setup_mcp_agent.sh
./start_complete_system.sh
```

### Production Deployment
```bash
# Deploy to Hostinger VPS
./scripts/hostinger_deploy.sh

# Or use generic production deployment
./scripts/deploy_production.sh
```

## 🏗️ Architecture

### Core Components
- **Stock Analysis Engine** (`main_enhanced.py`) - Advanced technical analysis with 269+ stock universe
- **MCP Server** (`yahoo_finance_mcp_server.py`) - WebSocket server for agentic communication  
- **Web Dashboard** (`web_dashboard.py`) - Real-time monitoring interface
- **Alert System** (`scheduled_market_alerts.py`) - Automated email notifications
- **Yahoo Finance Client** (`enhanced_yahoo_client.py`) - Extended market data integration

### Project Structure
```
📁 mcp-stock-alert/
├── 🚀 Core System
│   ├── main_enhanced.py           # Enhanced analysis engine
│   ├── yahoo_finance_mcp_server.py # MCP WebSocket server
│   ├── web_dashboard.py           # Flask dashboard
│   ├── scheduled_market_alerts.py # Alert scheduler
│   └── enhanced_yahoo_client.py   # Yahoo Finance client
├── 📁 scripts/                    # Deployment & management
│   ├── hostinger_deploy.sh        # Hostinger VPS deployment
│   ├── deploy_production.sh       # Generic production deployment
│   └── health_monitor.sh          # System health monitoring
├── 📁 config/                     # Production configuration
│   └── nginx.conf                 # Nginx reverse proxy config
├── 📁 docs/                       # Documentation
└── 📁 tests/                      # Testing suite
```

## 🎛️ Features

### Market Analysis
- **269+ Stock Universe** across multiple sectors (Tech, Healthcare, Finance, Energy, etc.)
- **Technical Indicators**: RSI, volume analysis, price momentum
- **Earnings Calendar** integration with Yahoo Finance
- **Investment Themes** tracking (AI, Clean Energy, Biotech, etc.)
- **News Sentiment** analysis from multiple sources

### Alert System
- **Smart Recommendations**: BUY/WATCH/NO SIGNAL based on multiple factors
- **Email Notifications**: Professional HTML emails with color-coded signals
- **Configurable Thresholds**: Customizable criteria for buy signals
- **Market Context**: Earnings dates and theme-based insights

### Production Features
- **MCP Integration**: WebSocket server for agentic communication
- **Health Monitoring**: Automated system health checks
- **Nginx Reverse Proxy**: Production-grade web server configuration
- **Process Management**: Systemd service integration
- **Cost Optimization**: Efficient resource usage for VPS deployment

## 🚀 Deployment Options

### 1. Hostinger VPS (Recommended)
```bash
./scripts/hostinger_deploy.sh
```
- **Cost**: ~$3.99/month
- **Specs**: 1 vCPU, 1GB RAM, 20GB SSD
- **Features**: Full root access, systemd services, nginx

### 2. Local Development
```bash
./start_complete_system.sh
```
- **Dashboard**: http://localhost:5001
- **MCP Server**: ws://localhost:8000

## 📊 System Management

```bash
# Health monitoring
./scripts/health_monitor.sh

# Stop all services
./stop_complete_system.sh

# Check system status
systemctl status stock-dashboard  # Production only
```

## 📧 Email Configuration

Configure email settings in your environment:
```bash
export EMAIL_TO="your-email@gmail.com"
export EMAIL_FROM="sender@gmail.com" 
export EMAIL_PASSWORD="your-app-password"
```

## 📚 Documentation

- 🚀 **Production Deployment**: [HOSTINGER_DEPLOYMENT_GUIDE.md](HOSTINGER_DEPLOYMENT_GUIDE.md)
- ✅ **Production Checklist**: [PRODUCTION_CHECKLIST.md](PRODUCTION_CHECKLIST.md)
- 📋 **Readiness Plan**: [PRODUCTION_READINESS_PLAN.md](PRODUCTION_READINESS_PLAN.md)
- 💰 **Cost Analysis**: [COST_COMPARISON.md](COST_COMPARISON.md)
- 🏗️ **System Design**: [docs/AGENTIC_SYSTEM_DESIGN.md](docs/AGENTIC_SYSTEM_DESIGN.md)
- 🔒 **Security Guide**: [docs/SECURITY_GUIDE.md](docs/SECURITY_GUIDE.md)
- 🌐 **Dashboard Guide**: [docs/WEB_DASHBOARD_GUIDE.md](docs/WEB_DASHBOARD_GUIDE.md)

## 🛠️ Technology Stack

- **Python 3.8+**: Core language
- **FastAPI**: MCP WebSocket server
- **Flask**: Web dashboard backend
- **yfinance**: Yahoo Finance API client
- **pandas**: Data analysis
- **nginx**: Production web server
- **systemd**: Process management

---

**🤖 Production-ready MCP stock alert system with institutional-level analysis of 269+ stocks!** 📈✨
