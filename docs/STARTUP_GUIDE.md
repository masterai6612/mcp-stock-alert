# 🚀 Agentic Stock Alert System - Startup Guide

## 📋 Quick Start After Laptop Restart

### 1️⃣ **One-Command Startup**
```bash
./start_complete_system.sh
```

This single script will:
- ✅ Start all Docker services (n8n, PostgreSQL, Redis)
- ✅ Launch n8n Integration API Server
- ✅ Start Web Dashboard
- ✅ Verify all components are working
- ✅ Test email configuration
- ✅ Ensure both options are operational

### 2️⃣ **Verify Everything is Working**
```bash
python test_both_options.py
```

This will test:
- 🧪 Script-based option
- 🔄 n8n workflow option
- 📧 Email alert system
- 🌐 n8n UI accessibility

## 📊 Your Two Options

### **Option 1: Script-Based (Manual)**
```bash
# Run comprehensive analysis manually
python main_enhanced.py

# Features:
# • Immediate analysis of 269+ stocks
# • X (Twitter) sentiment analysis
# • Earnings calendar integration
# • Investment themes analysis
# • Email alerts for buy signals
```

### **Option 2: n8n Workflow (Automated)**
```bash
# Access n8n UI
open http://localhost:5678
# Login: admin / stockagent123

# Key Workflows:
# • FULL UNIVERSE - All 269 Stocks Analysis (runs every 30 min)
# • Real Email Alert - masterai6612@gmail.com (manual test)
# • X (Twitter) Sentiment Analysis - Enhanced (demo)
```

## 🔧 System Management

### **Monitor System Status**
```bash
./monitor_system.sh
```

### **Stop All Services**
```bash
./stop_system.sh
```

### **Restart Individual Components**
```bash
# Restart Docker services
docker-compose restart

# Restart n8n only
docker-compose restart n8n

# Check logs
docker-compose logs n8n
tail -f *.log
```

## 📧 Email Alerts

Your system sends professional HTML email alerts to:
**📬 masterai6612@gmail.com**

### Email Features:
- 🐦 **X (Twitter) sentiment** (🐦📈 Bullish, 🐦📉 Bearish, 🐦😐 Neutral)
- 📅 **Earnings calendar** integration
- 🔥 **Investment themes** analysis
- 📊 **Technical indicators** (RSI, volume, price action)
- 🎨 **Professional HTML** formatting with color coding
- 🎯 **Smart subject lines** based on market conditions

### Sample Email Subjects:
- `🐦🚀 X BULLISH: 3 Stocks + 5 BUY Signals!`
- `📈 MAJOR ALERT: 8 Buy Signals from Full Universe Analysis`
- `💡 3 Buy Opportunities from 269 Stock Scan (BULLISH)`

## 🌐 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **n8n UI** | http://localhost:5678 | Workflow management |
| **API Server** | http://localhost:5002 | n8n integration |
| **Dashboard** | http://localhost:5001 | System monitoring |

### n8n Login:
- **Username**: admin
- **Password**: stockagent123

## 🔍 Troubleshooting

### **If Email Alerts Don't Work:**
1. Check `.env` file has correct email settings
2. Verify Gmail app password is correct
3. Test email: `python test_both_options.py`

### **If n8n Workflows Don't Start:**
1. Check Docker is running: `docker ps`
2. Restart services: `docker-compose restart`
3. Check n8n logs: `docker-compose logs n8n`

### **If API Server Fails:**
1. Check port 5002 is free: `lsof -i :5002`
2. Check logs: `tail -f *.log`
3. Restart: Kill process and run `./start_complete_system.sh`

## 📊 System Features

### **Stock Universe (269+ stocks)**
- 🏢 **S&P 500 Large Caps**: AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA
- 🤖 **AI & Technology**: CRM, ORCL, INTC, MU, MRVL, SNPS, CDNS
- 💊 **Healthcare & Biotech**: UNH, JNJ, PFE, ABBV, MRK, TMO, ABT
- 🏦 **Financial Services**: JPM, BAC, WFC, GS, MS, C, AXP, SCHW
- ⚡ **Energy & Materials**: XOM, CVX, COP, EOG, SLB, MPC, VLO
- 🇨🇦 **Canadian Large Caps**: SHOP, RY, TD, CNR, CP, ENB

### **Analysis Features**
- 📈 **Technical Analysis**: RSI, volume, price movements
- 📅 **Earnings Calendar**: Upcoming earnings events
- 🔥 **Investment Themes**: Hot market sectors and trends
- 🐦 **X Sentiment**: Real-time Twitter/X sentiment analysis
- 🎯 **Smart Recommendations**: Multi-factor scoring system

## 🎯 Success Indicators

After running `./start_complete_system.sh`, you should see:
- ✅ All Docker services running
- ✅ n8n UI accessible at http://localhost:5678
- ✅ API server responding at http://localhost:5002
- ✅ Email configuration verified
- ✅ Test email sent to masterai6612@gmail.com

## 💡 Pro Tips

1. **Run the startup script after every laptop restart**
2. **Check your email regularly** for buy signals
3. **Use the dashboard** to monitor system health
4. **Test both options** to ensure redundancy
5. **Monitor logs** if you notice issues

---

**🚀 Your agentic stock alert system is now ready to help you identify trading opportunities with institutional-level analysis!** 📈✨