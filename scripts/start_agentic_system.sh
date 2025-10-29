#!/bin/bash

echo "🚀 Starting Agentic Stock Alert System with n8n"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p n8n-workflows n8n-credentials logs

# Start Docker containers
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for containers to be ready
echo "⏳ Waiting for containers to start..."
sleep 10

# Check container status
echo "📊 Container Status:"
docker-compose ps

# Start n8n integration server
echo "🔗 Starting n8n Integration Server..."
source venv/bin/activate
python n8n_integration.py &
N8N_INTEGRATION_PID=$!

# Start existing dashboard (if not already running)
echo "📊 Starting Stock Dashboard..."
python web_dashboard.py &
DASHBOARD_PID=$!

echo ""
echo "✅ Agentic Stock Alert System Started!"
echo "======================================"
echo "🌐 n8n Workflow Editor: http://localhost:5678"
echo "   Username: admin"
echo "   Password: stockagent123"
echo ""
echo "🔗 n8n Integration API: http://localhost:5000"
echo "📊 Stock Dashboard: http://localhost:5001"
echo "🗄️  PostgreSQL: localhost:5432 (n8n/n8n_password)"
echo "🔴 Redis: localhost:6379"
echo ""
echo "📋 Available API Endpoints:"
echo "   POST http://localhost:5000/api/stock-analysis"
echo "   GET  http://localhost:5000/api/market-data"
echo "   POST http://localhost:5000/api/alerts"
echo "   GET  http://localhost:5000/api/portfolio"
echo "   GET  http://localhost:5000/health"
echo ""
echo "🎯 n8n Webhook URLs:"
echo "   http://localhost:5678/webhook/stock-alert"
echo "   http://localhost:5678/webhook/market-update"
echo ""
echo "💡 Next Steps:"
echo "1. Open n8n at http://localhost:5678"
echo "2. Import the pre-built workflows from n8n-workflows/"
echo "3. Configure credentials and test workflows"
echo "4. Monitor logs in the logs/ directory"
echo ""
echo "🛑 To stop: docker-compose down && kill $N8N_INTEGRATION_PID $DASHBOARD_PID"

# Save PIDs for cleanup
echo $N8N_INTEGRATION_PID > logs/n8n_integration.pid
echo $DASHBOARD_PID > logs/dashboard.pid

# Keep script running
wait