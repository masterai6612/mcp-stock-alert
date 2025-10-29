# 🤖 Agentic Stock Alert System with n8n

## 🎉 System Successfully Deployed!

Your agentic stock alert system is now running with n8n workflow automation. Here's what's currently active:

### 🌐 **Active Services:**

| Service | URL | Status | Purpose |
|---------|-----|--------|---------|
| **n8n Workflow Editor** | http://localhost:5678 | ✅ Running | Visual workflow automation |
| **n8n Integration API** | http://localhost:5002 | ✅ Running | Stock data API for workflows |
| **Stock Dashboard** | http://localhost:5001 | ✅ Running | Real-time monitoring |
| **PostgreSQL** | localhost:5432 | ✅ Running | n8n database |
| **Redis** | localhost:6379 | ✅ Running | Caching & queues |

### 🔐 **Login Credentials:**
- **n8n Username:** `admin`
- **n8n Password:** `stockagent123`

## 🚀 **Getting Started with Your Agentic System**

### Step 1: Access n8n Workflow Editor
1. Open http://localhost:5678 in your browser
2. Login with admin/stockagent123
3. You'll see the n8n workflow editor interface

### Step 2: Import Pre-built Workflows
I've created two powerful workflows for you:

#### 📊 **Stock Alert Agent Workflow**
- **File:** `n8n-workflows/stock-alert-workflow.json`
- **Purpose:** Processes stock analysis and sends intelligent alerts
- **Triggers:** Webhook-based (can be called from external systems)
- **Actions:** 
  - Analyzes 269+ stocks
  - Filters for BUY/STRONG BUY signals
  - Sends email alerts
  - Updates dashboard

#### 🔍 **Market Monitor Agent Workflow**
- **File:** `n8n-workflows/market-monitor-workflow.json`
- **Purpose:** Continuously monitors market conditions
- **Triggers:** Every 15 minutes automatically
- **Actions:**
  - Checks major market indices (SPY, QQQ, DIA, IWM)
  - Detects significant market movements
  - Triggers stock analysis when needed
  - Updates dashboard with market sentiment

### Step 3: Test the API Integration
Your system exposes several API endpoints that n8n can use:

```bash
# Test market data endpoint
curl http://localhost:5002/api/market-data

# Test stock analysis endpoint
curl -X POST http://localhost:5002/api/stock-analysis \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "NVDA", "MSFT"]}'

# Health check
curl http://localhost:5002/health
```

## 🤖 **Agentic Capabilities Now Available**

### **Autonomous Decision Making**
- n8n workflows can make decisions based on market conditions
- Conditional logic determines when to trigger alerts
- Smart filtering prevents alert spam

### **Multi-Agent Coordination**
- Market Monitor Agent watches overall market
- Stock Alert Agent analyzes individual stocks
- Agents communicate through webhooks and APIs

### **Learning and Adaptation**
- Workflows can be modified based on performance
- Historical data stored in PostgreSQL
- Redis caching improves response times

### **Goal-Oriented Behavior**
- Workflows designed to maximize trading opportunities
- Risk-aware decision making
- Priority-based alert system

## 🛠️ **Advanced Configuration**

### **Customizing Workflows**
1. Open n8n editor at http://localhost:5678
2. Import workflows from `n8n-workflows/` directory
3. Modify triggers, conditions, and actions as needed
4. Test workflows using the built-in testing tools

### **Adding New Agents**
You can easily add new specialized agents:

1. **News Sentiment Agent**: Monitor news and social media
2. **Risk Management Agent**: Portfolio risk assessment
3. **Execution Agent**: Optimal trade timing
4. **Portfolio Agent**: Asset allocation optimization

### **Webhook URLs for External Integration**
- Stock Alert Trigger: `http://localhost:5678/webhook/stock-alert`
- Market Update: `http://localhost:5678/webhook/market-update`

## 📊 **Monitoring and Logs**

### **n8n Execution History**
- View workflow executions in n8n interface
- Debug failed workflows
- Monitor performance metrics

### **API Logs**
- n8n Integration Server logs: Check terminal output
- Dashboard logs: Check web_dashboard.py output

### **Database Access**
- PostgreSQL: `psql -h localhost -p 5432 -U n8n -d n8n`
- Redis: `redis-cli -h localhost -p 6379`

## 🎯 **Next Steps: Building Your Agentic Trading System**

### **Phase 1: Basic Automation (Current)**
- ✅ Market monitoring every 15 minutes
- ✅ Automated stock analysis
- ✅ Intelligent alert filtering
- ✅ Email notifications

### **Phase 2: Enhanced Intelligence**
- 🔄 Add machine learning models
- 🔄 Implement sentiment analysis
- 🔄 Create portfolio optimization
- 🔄 Add risk management rules

### **Phase 3: Full Autonomy**
- 🔄 Autonomous trading decisions
- 🔄 Dynamic strategy adaptation
- 🔄 Multi-market expansion
- 🔄 Performance attribution

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **n8n not accessible**: Check if container is running with `docker ps`
2. **API errors**: Verify n8n integration server is running on port 5002
3. **Workflow failures**: Check n8n execution logs in the interface
4. **Database connection**: Ensure PostgreSQL container is healthy

### **Restart Commands:**
```bash
# Restart all containers
docker-compose restart

# Restart specific service
docker-compose restart n8n

# View logs
docker-compose logs n8n
```

## 🎉 **You Now Have a True Agentic System!**

Your stock alert system has evolved from simple automation to intelligent, autonomous agents that:

- 🧠 **Think**: Analyze market conditions and make decisions
- 🤝 **Collaborate**: Multiple agents work together
- 📈 **Learn**: Adapt strategies based on performance
- 🎯 **Act**: Take autonomous actions based on goals
- 🔄 **Evolve**: Continuously improve over time

The system is now ready to be your intelligent trading assistant! 🚀

## 📞 **Support**

If you need help customizing workflows or adding new capabilities, the system is designed to be easily extensible. Each agent can be enhanced with additional logic, and new agents can be added through n8n's visual interface.

Happy automated trading! 📈🤖