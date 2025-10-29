#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🛑 Stopping Complete Agentic Stock Alert System..."
echo "=================================================="

# 0. Show what's currently running
print_info "Scanning for running processes..."
CURRENT_PROCESSES=$(ps aux | grep -E "(gunicorn|python.*main_enhanced|python.*web_dashboard|python.*n8n_integration|python.*mcp_server|python.*start_mcp|docker.*n8n)" | grep -v grep | wc -l)
if [ "$CURRENT_PROCESSES" -gt 0 ]; then
    print_info "Found $CURRENT_PROCESSES related processes running:"
    ps aux | grep -E "(gunicorn|python.*main_enhanced|python.*web_dashboard|python.*n8n_integration|python.*mcp_server|python.*start_mcp|docker.*n8n)" | grep -v grep | awk '{print "   • " $11 " (PID: " $2 ")"}'
    echo
else
    print_info "No related processes currently running"
fi

# 1. Stop Gunicorn processes using PID files
print_info "Stopping Gunicorn servers..."

if [ -f "dashboard.pid" ]; then
    DASHBOARD_PID=$(cat dashboard.pid)
    if kill -0 $DASHBOARD_PID 2>/dev/null; then
        kill $DASHBOARD_PID
        print_status "Dashboard server stopped (PID: $DASHBOARD_PID)"
    else
        print_warning "Dashboard PID file exists but process not running"
    fi
    rm -f dashboard.pid
else
    print_info "No dashboard PID file found"
fi

if [ -f "n8n_api.pid" ]; then
    N8N_API_PID=$(cat n8n_api.pid)
    if kill -0 $N8N_API_PID 2>/dev/null; then
        kill $N8N_API_PID
        print_status "n8n API server stopped (PID: $N8N_API_PID)"
    else
        print_warning "n8n API PID file exists but process not running"
    fi
    rm -f n8n_api.pid
else
    print_info "No n8n API PID file found"
fi

# 2. Kill any remaining Gunicorn processes
print_info "Cleaning up any remaining Gunicorn processes..."
GUNICORN_PIDS=$(ps aux | grep gunicorn | grep -v grep | awk '{print $2}')
if [ ! -z "$GUNICORN_PIDS" ]; then
    echo "$GUNICORN_PIDS" | xargs kill -9 2>/dev/null || true
    print_status "Remaining Gunicorn processes terminated"
else
    print_info "No remaining Gunicorn processes found"
fi

# 3. Kill processes on specific ports
print_info "Freeing up ports 5001, 5002, 5678..."

# Port 5001 (Dashboard)
PORT_5001_PIDS=$(lsof -t -i:5001 2>/dev/null || true)
if [ ! -z "$PORT_5001_PIDS" ]; then
    echo "$PORT_5001_PIDS" | xargs kill -9 2>/dev/null || true
    print_status "Port 5001 freed"
fi

# Port 5002 (n8n API)
PORT_5002_PIDS=$(lsof -t -i:5002 2>/dev/null || true)
if [ ! -z "$PORT_5002_PIDS" ]; then
    echo "$PORT_5002_PIDS" | xargs kill -9 2>/dev/null || true
    print_status "Port 5002 freed"
fi

# Port 5678 (n8n UI) - handled by Docker, but just in case
PORT_5678_PIDS=$(lsof -t -i:5678 2>/dev/null || true)
if [ ! -z "$PORT_5678_PIDS" ]; then
    echo "$PORT_5678_PIDS" | xargs kill -9 2>/dev/null || true
    print_status "Port 5678 freed"
fi

# 4. Stop background jobs and scheduled tasks
print_info "Stopping background jobs and scheduled tasks..."

# Kill any background jobs in current shell
jobs -p | xargs kill -9 2>/dev/null || true

# Stop any cron jobs related to our system (if any)
CRON_JOBS=$(crontab -l 2>/dev/null | grep -E "(main_enhanced|scheduled_market_alerts|stock.*alert)" | wc -l)
if [ "$CRON_JOBS" -gt 0 ]; then
    print_warning "Found $CRON_JOBS cron jobs related to stock alerts"
    print_info "You may want to check: crontab -l"
fi

print_status "Background jobs cleanup completed"

# 5. Stop ALL Python processes related to our system
print_info "Stopping all related Python processes..."

# List of all possible Python scripts that could be running
PYTHON_SCRIPTS=(
    "main_enhanced.py"
    "main.py"
    "web_dashboard.py"
    "n8n_integration.py"
    "start_mcp_server.py"
    "yahoo_finance_mcp_server.py"
    "scheduled_market_alerts.py"
    "check_agentic_system.py"
    "check_alert_status.py"
    "check_email_alerts.py"
    "dashboard_features.py"
    "enhanced_yahoo_client.py"
    "test_dashboard_api.py"
    "test_direct_api.py"
    "test_n8n_workflow.py"
    "test_x_sentiment_integration.py"
    "scripts/import_n8n_workflows.py"
    "scripts/setup_n8n_workflows.py"
    "scripts/setup_n8n_auth.py"
    "scripts/activate_all_workflows.py"
    "scripts/activate_email_workflows.py"
    "scripts/cleanup_workflows.py"
    "scripts/monitor_system.py"
    "import_workflows.py"
    "activate_all_workflows.py"
    "activate_email_workflows.py"
    "cleanup_workflows.py"
    "create_workflow_via_api.py"
    "update_scheduled_workflow.py"
)

KILLED_COUNT=0
for script in "${PYTHON_SCRIPTS[@]}"; do
    SCRIPT_PIDS=$(ps aux | grep python | grep "$script" | grep -v grep | awk '{print $2}')
    if [ ! -z "$SCRIPT_PIDS" ]; then
        echo "$SCRIPT_PIDS" | xargs kill -9 2>/dev/null || true
        KILLED_COUNT=$((KILLED_COUNT + 1))
        print_status "Stopped: $script"
    fi
done

# Also kill any Python process in our directory
CURRENT_DIR=$(pwd)
DIR_PYTHON_PIDS=$(ps aux | grep python | grep "$CURRENT_DIR" | grep -v grep | grep -v "jedi-language-server" | awk '{print $2}')
if [ ! -z "$DIR_PYTHON_PIDS" ]; then
    echo "$DIR_PYTHON_PIDS" | xargs kill -9 2>/dev/null || true
    KILLED_COUNT=$((KILLED_COUNT + 1))
    print_status "Stopped Python processes in project directory"
fi

if [ $KILLED_COUNT -gt 0 ]; then
    print_status "Stopped $KILLED_COUNT Python process groups"
else
    print_info "No related Python processes found"
fi

# 6. Stop Docker services
print_info "Stopping Docker services..."
if command -v docker-compose >/dev/null 2>&1; then
    if [ -f "config/docker-compose.yml" ]; then
        docker-compose -f config/docker-compose.yml down --remove-orphans
        print_status "Docker services stopped"
    else
        print_warning "Docker compose file not found"
    fi
else
    print_warning "Docker compose not available"
fi

# 7. Stop individual Docker containers (fallback)
print_info "Ensuring Docker containers are stopped..."
CONTAINERS=("stock-agent-n8n" "stock-agent-postgres" "stock-agent-redis")
for container in "${CONTAINERS[@]}"; do
    if docker ps -q -f name=$container | grep -q .; then
        docker stop $container >/dev/null 2>&1
        docker rm $container >/dev/null 2>&1
        print_status "Container $container stopped and removed"
    fi
done

# 8. Stop any systemd services (if running on Linux)
if command -v systemctl >/dev/null 2>&1; then
    print_info "Checking for systemd services..."
    if systemctl is-active --quiet stock-dashboard 2>/dev/null; then
        sudo systemctl stop stock-dashboard
        print_status "Systemd service 'stock-dashboard' stopped"
    fi
fi

# 9. Clean up log files and temporary files
print_info "Cleaning up temporary files..."
rm -f *.pid *.log 2>/dev/null || true

# Clean up any temporary Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

print_status "Temporary files and cache cleaned"

# 10. Check for any remaining processes
print_info "Final cleanup check..."
REMAINING_PROCESSES=$(ps aux | grep -E "(gunicorn|n8n|stock-agent|main_enhanced|web_dashboard|mcp_server)" | grep -v grep | wc -l)
if [ "$REMAINING_PROCESSES" -gt 0 ]; then
    print_warning "Some processes may still be running:"
    ps aux | grep -E "(gunicorn|n8n|stock-agent|main_enhanced|web_dashboard|mcp_server)" | grep -v grep
    print_info "You may need to manually kill these processes"
else
    print_status "All processes successfully stopped"
fi

# 11. Verify ports are free
print_info "Verifying ports are free..."
PORTS_IN_USE=0

if lsof -i:5001 >/dev/null 2>&1; then
    print_warning "Port 5001 still in use"
    PORTS_IN_USE=$((PORTS_IN_USE + 1))
fi

if lsof -i:5002 >/dev/null 2>&1; then
    print_warning "Port 5002 still in use"
    PORTS_IN_USE=$((PORTS_IN_USE + 1))
fi

if lsof -i:5678 >/dev/null 2>&1; then
    print_warning "Port 5678 still in use"
    PORTS_IN_USE=$((PORTS_IN_USE + 1))
fi

if [ "$PORTS_IN_USE" -eq 0 ]; then
    print_status "All ports are now free"
else
    print_warning "$PORTS_IN_USE ports still in use"
fi

echo
echo "=================================================="
print_status "🎯 SYSTEM SHUTDOWN COMPLETE!"
echo "=================================================="
echo
print_info "📊 Shutdown Summary:"
echo "   🔴 Gunicorn servers: Stopped"
echo "   🔴 Docker services: Stopped"
echo "   🔴 MCP Server: Stopped"
echo "   🔴 Background processes: Terminated"
echo "   🧹 Temporary files: Cleaned"
echo "   🚪 Ports: Freed (5001, 5002, 5678)"
echo
print_info "💡 To restart the system, run:"
echo "   ./start_complete_system.sh"
echo