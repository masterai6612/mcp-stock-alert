#!/bin/bash
echo "🛑 Stopping Agentic Stock Alert System..."

# Load process IDs
if [ -f ".system_pids" ]; then
    source .system_pids
    
    # Kill Python processes
    if [ ! -z "$N8N_API_PID" ]; then
        kill $N8N_API_PID 2>/dev/null
        echo "✅ Stopped n8n API Server"
    fi
    
    # Also stop Gunicorn n8n API if running
    if [ -f "n8n_api.pid" ]; then
        GUNICORN_N8N_PID=$(cat n8n_api.pid)
        kill $GUNICORN_N8N_PID 2>/dev/null
        rm -f n8n_api.pid
        echo "✅ Stopped Gunicorn n8n API Server"
    fi
    
    if [ ! -z "$DASHBOARD_PID" ]; then
        kill $DASHBOARD_PID 2>/dev/null
        echo "✅ Stopped Web Dashboard"
    fi
    
    # Also stop Gunicorn dashboard if running
    if [ -f "dashboard.pid" ]; then
        GUNICORN_PID=$(cat dashboard.pid)
        kill $GUNICORN_PID 2>/dev/null
        rm -f dashboard.pid
        echo "✅ Stopped Gunicorn Dashboard"
    fi
    
    if [ ! -z "$MCP_SERVER_PID" ]; then
        kill $MCP_SERVER_PID 2>/dev/null
        echo "✅ Stopped MCP Server"
    fi
    
    rm .system_pids
fi

# Stop Docker services
docker-compose -f config/docker-compose.yml down
echo "✅ Stopped Docker services"

echo "🛑 System stopped successfully"
