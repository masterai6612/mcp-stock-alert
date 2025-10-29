# 🔧 n8n Workflow Troubleshooting Guide

## 🚨 Common Issues and Solutions

### **Issue 1: HTTP Request Node Errors**
**Problem**: "Problem running workflow" with HTTP request nodes

**Solutions**:
1. **Update URLs**: Make sure HTTP Request nodes use the correct URL:
   - Change `http://localhost:5002` to `http://host.docker.internal:5002`
   - This allows n8n (running in Docker) to access your local API

2. **Check Timeout Settings**: 
   - Set timeout to 30000ms (30 seconds) in HTTP Request node options
   - Go to node → Parameters → Options → Timeout

### **Issue 2: Missing Credentials**
**Problem**: Nodes requiring authentication fail

**Solutions**:
1. **Email Send Node**: If using email alerts, configure SMTP credentials
2. **HTTP Request with Auth**: Set up basic auth if needed

### **Issue 3: JSON/Code Node Errors**
**Problem**: JavaScript code in Code nodes fails

**Solutions**:
1. **Simplify Code**: Use basic JavaScript without complex operations
2. **Check Syntax**: Ensure proper JSON.stringify() usage
3. **Add Error Handling**: Wrap code in try-catch blocks

## 🛠️ Step-by-Step Fix Process

### **Step 1: Delete Problematic Workflows**
1. In n8n, go to your workflows list
2. Delete any workflows showing errors
3. Start fresh with simplified versions

### **Step 2: Import Simple Workflows**
I've created simplified versions for you:
- `simple-stock-alert-workflow.json`
- `simple-market-monitor-workflow.json`

### **Step 3: Configure HTTP Request Nodes**
For each HTTP Request node:

1. **Click on the HTTP Request node**
2. **Set URL**: `http://host.docker.internal:5002/api/stock-analysis`
3. **Set Method**: POST (for stock analysis) or GET (for market data)
4. **Set Headers**: Content-Type: application/json
5. **Set Body** (for POST): 
   ```json
   {
     "symbols": ["AAPL", "NVDA", "MSFT"]
   }
   ```
6. **Set Timeout**: 30000 (in Options section)

### **Step 4: Test Individual Nodes**
1. **Click "Execute Node"** on each node individually
2. **Check output** to ensure it's working
3. **Fix any errors** before connecting nodes

### **Step 5: Test Full Workflow**
1. **Save the workflow**
2. **Click "Execute Workflow"** 
3. **Check execution log** for any errors

## 🎯 Quick Fix: Manual Node Setup

If imports keep failing, create workflows manually:

### **Simple Stock Alert Workflow**:
1. **Add Webhook Trigger**:
   - Path: `stock-alert`
   - Method: POST

2. **Add HTTP Request**:
   - URL: `http://host.docker.internal:5002/api/stock-analysis`
   - Method: POST
   - Body: `{{ JSON.stringify($json) }}`

3. **Add Respond to Webhook**:
   - Response: `{{ JSON.stringify({success: true, data: $json}) }}`

4. **Connect**: Webhook → HTTP Request → Response

### **Simple Market Monitor Workflow**:
1. **Add Schedule Trigger**:
   - Interval: Every 30 minutes

2. **Add HTTP Request**:
   - URL: `http://host.docker.internal:5002/api/market-data`
   - Method: GET

3. **Add Code Node**:
   ```javascript
   console.log('Market check completed');
   return [{json: {timestamp: new Date().toISOString(), completed: true}}];
   ```

4. **Connect**: Schedule → HTTP Request → Code

## 🧪 Test Your API First

Before setting up workflows, test your API directly:

```bash
# Test from your terminal (outside Docker)
curl http://localhost:5002/health

# Test stock analysis
curl -X POST http://localhost:5002/api/stock-analysis \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL"]}'
```

## 🔍 Debug Tips

1. **Check n8n Logs**: Look at execution logs in n8n interface
2. **Check API Logs**: Monitor your n8n_integration.py output
3. **Test URLs**: Use `host.docker.internal` instead of `localhost` in n8n
4. **Start Simple**: Begin with basic workflows, add complexity later

## 🚀 Once Working

After you get basic workflows running:
1. **Activate them** (toggle switch in workflow list)
2. **Monitor executions** in n8n interface
3. **Check logs** for successful API calls
4. **Add more complexity** gradually

Your agentic system will be fully operational once these workflows are running! 🤖✨