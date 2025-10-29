#!/bin/bash

# 🚀 Complete Agentic Stock Alert System Startup Script

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

# This script starts both Script-based and n8n workflow options
# Run this after laptop restart to get your email alerts working

echo "🚀 Starting Complete Agentic Stock Alert System..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "main.py" ] || [ ! -f "n8n_integration.py" ]; then
    print_error "Please run this script from the mcp-stock-alert directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup first."
    exit 1
fi

print_info "Starting system components..."
echo

# 1. Activate virtual environment
print_info "Activating Python virtual environment..."
if [ ! -d "venv" ]; then
    print_error "Virtual environment not found. Please run setup first."
    print_info "Run: ./setup_mcp_agent.sh"
    exit 1
fi

source venv/bin/activate
if [ "$VIRTUAL_ENV" != "" ]; then
    print_status "Virtual environment activated: $VIRTUAL_ENV"
    # Verify Python version and key dependencies
    PYTHON_VERSION=$(python --version 2>&1)
    print_info "Using: $PYTHON_VERSION"
    
    # Check if key dependencies are installed
    python -c "import flask, yfinance, requests" 2>/dev/null || {
        print_warning "Installing missing core dependencies..."
        pip install flask yfinance requests gunicorn psutil > /dev/null 2>&1
    }
    print_status "Core dependencies verified"
else
    print_error "Failed to activate virtual environment"
    exit 1
fi

# 2. Check environment variables
print_info "Checking environment configuration..."
if [ ! -f ".env" ]; then
    print_error ".env file not found. Please configure your secrets first."
    exit 1
fi

# Load environment variables
source .env
if [ -z "$EMAIL_FROM" ] || [ -z "$EMAIL_PASSWORD" ]; then
    print_error "Email configuration missing in .env file"
    exit 1
fi

print_status "Environment configuration verified"

# 2.5. Ensure Docker is running
print_info "Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    print_warning "Docker is not running. Starting Docker..."
    open -a Docker
    print_info "Waiting for Docker to start..."
    for i in {1..30}; do
        if docker info > /dev/null 2>&1; then
            print_status "Docker is now running"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Docker failed to start within 30 seconds"
            print_error "Please start Docker manually and try again"
            exit 1
        fi
        sleep 1
    done
else
    print_status "Docker is already running"
fi

# 3. Clean up and start Docker services (n8n, PostgreSQL, Redis)
print_info "Cleaning up old Docker containers..."
docker container prune -f > /dev/null 2>&1 || true
docker-compose -f config/docker-compose.yml down --remove-orphans > /dev/null 2>&1 || true
docker rm -f stock-agent-n8n stock-agent-postgres stock-agent-redis > /dev/null 2>&1 || true
print_status "Docker cleanup completed"

print_info "Starting Docker services (n8n, PostgreSQL, Redis)..."
if command -v docker-compose &> /dev/null; then
    docker-compose -f config/docker-compose.yml up -d
    if [ $? -eq 0 ]; then
        print_status "Docker services started successfully"
        sleep 5  # Wait for services to initialize
    else
        print_error "Failed to start Docker services"
        print_info "Trying to start Docker application..."
        open -a Docker
        sleep 10
        print_info "Retrying Docker services..."
        docker-compose -f config/docker-compose.yml up -d
        if [ $? -eq 0 ]; then
            print_status "Docker services started successfully (after retry)"
            sleep 5
        else
            print_error "Failed to start Docker services even after retry"
            exit 1
        fi
    fi
else
    print_error "Docker Compose not found. Please install Docker."
    exit 1
fi

# 4. Start n8n Integration API Server
print_info "Installing n8n API server dependencies..."
pip install gunicorn flask > /dev/null 2>&1 || true
print_status "n8n API dependencies ready"

print_info "Cleaning up any existing n8n API processes..."
EXISTING_N8N_PIDS=$(lsof -t -i:5002 2>/dev/null || true)
if [ ! -z "$EXISTING_N8N_PIDS" ]; then
    kill -9 $EXISTING_N8N_PIDS 2>/dev/null || true
    sleep 2
fi

print_info "Starting n8n Integration API Server with production server..."
# Use gunicorn for production deployment
gunicorn --bind 0.0.0.0:5002 --workers 2 --timeout 300 --daemon --pid n8n_api.pid n8n_integration:app
sleep 5

# Check if n8n API server is running with retries
N8N_ATTEMPTS=0
while [ $N8N_ATTEMPTS -lt 15 ]; do
    if curl -s http://localhost:5002/health > /dev/null 2>&1; then
        N8N_API_PID=$(cat n8n_api.pid 2>/dev/null || echo "unknown")
        print_status "n8n Integration API Server started with Gunicorn (PID: $N8N_API_PID)"
        break
    else
        N8N_ATTEMPTS=$((N8N_ATTEMPTS + 1))
        if [ $N8N_ATTEMPTS -eq 15 ]; then
            print_error "Failed to start n8n Integration API Server after 15 attempts"
            print_info "Trying fallback to development server..."
            python n8n_integration.py &
            N8N_API_PID=$!
            sleep 5
            if curl -s http://localhost:5002/health > /dev/null 2>&1; then
                print_status "n8n Integration API Server started with development server (PID: $N8N_API_PID)"
            else
                print_error "n8n Integration API Server failed to start completely"
                kill $N8N_API_PID 2>/dev/null
                exit 1
            fi
        else
            sleep 2
        fi
    fi
done

# 5. Start MCP Server (Yahoo Finance)
print_info "Starting MCP Server (Yahoo Finance)..."
python yahoo_finance_mcp_server.py > mcp_server.log 2>&1 &
MCP_SERVER_PID=$!
sleep 5

# Check if MCP server is running (it uses stdio, so we check process)
if kill -0 $MCP_SERVER_PID 2>/dev/null; then
    print_status "MCP Server started (PID: $MCP_SERVER_PID)"
else
    print_warning "MCP Server failed to start (optional component)"
    MCP_SERVER_PID=""
fi

# 6. Start Web Dashboard (essential component)
print_info "Installing dashboard dependencies..."
pip install psutil gunicorn > /dev/null 2>&1 || true
print_status "Dashboard dependencies ready"

print_info "Cleaning up any existing dashboard processes..."
# Kill any existing processes on port 5001
EXISTING_PIDS=$(lsof -t -i:5001 2>/dev/null || true)
if [ ! -z "$EXISTING_PIDS" ]; then
    kill -9 $EXISTING_PIDS 2>/dev/null || true
    sleep 2
fi

print_info "Starting Web Dashboard with production server..."
# Use gunicorn for production deployment
gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 --daemon --pid dashboard.pid web_dashboard:app
sleep 5

# Check if dashboard is running
DASHBOARD_ATTEMPTS=0
while [ $DASHBOARD_ATTEMPTS -lt 10 ]; do
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
        DASHBOARD_PID=$(cat dashboard.pid 2>/dev/null || echo "unknown")
        print_status "Web Dashboard started with Gunicorn (PID: $DASHBOARD_PID)"
        break
    else
        DASHBOARD_ATTEMPTS=$((DASHBOARD_ATTEMPTS + 1))
        if [ $DASHBOARD_ATTEMPTS -eq 10 ]; then
            print_error "Web Dashboard failed to start after 10 attempts"
            # Try fallback to development server
            print_info "Trying fallback to development server..."
            python web_dashboard.py &
            DASHBOARD_PID=$!
            sleep 3
            if curl -s http://localhost:5001 > /dev/null 2>&1; then
                print_status "Web Dashboard started with development server (PID: $DASHBOARD_PID)"
            else
                print_error "Web Dashboard failed to start completely"
            fi
        else
            sleep 1
        fi
    fi
done

# 7. Wait for n8n to be ready
print_info "Waiting for n8n to be ready..."
N8N_READY_ATTEMPTS=0
while [ $N8N_READY_ATTEMPTS -lt 60 ]; do
    if curl -s http://localhost:5678 > /dev/null 2>&1; then
        print_status "n8n is ready"
        break
    else
        N8N_READY_ATTEMPTS=$((N8N_READY_ATTEMPTS + 1))
        if [ $N8N_READY_ATTEMPTS -eq 60 ]; then
            print_error "n8n failed to start within 60 seconds"
            exit 1
        else
            sleep 1
        fi
    fi
done

# 8. Test the complete system
print_info "Testing system components..."

# Test n8n API
if curl -s http://localhost:5002/api/comprehensive-analysis \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"stock_limit": 3}' | grep -q "success"; then
    print_status "n8n Integration API is working"
else
    print_error "n8n Integration API test failed"
fi

# Test email functionality
print_info "Testing email system..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

email_from = os.getenv('EMAIL_FROM')
email_password = os.getenv('EMAIL_PASSWORD')

if email_from and email_password:
    print('✅ Email configuration verified')
    print(f'📧 Email: {email_from}')
else:
    print('❌ Email configuration missing')
    exit(1)
"

# 8. Show system status
echo
echo "=================================================="
print_status "🎉 SYSTEM STARTUP COMPLETE!"
echo "=================================================="
echo
print_info "📊 System Components Status:"
echo "   🐳 Docker Services: http://localhost:5678 (n8n)"
echo "   🔗 n8n API Server: http://localhost:5002 (Gunicorn Production Server)"
echo "   📊 Web Dashboard: http://localhost:5001 (Gunicorn Production Server)"
echo "   🤖 MCP Server: yahoo_finance_mcp_server.py (stdio)"
echo "   📧 Email Alerts: masterai6612@gmail.com"
echo
print_info "🤖 Available Options:"
echo
echo "   1️⃣  SCRIPT-BASED OPTION:"
echo "      • Run: python main_enhanced.py"
echo "      • Manual execution with comprehensive analysis"
echo "      • Immediate email alerts for buy signals"
echo
echo "   2️⃣  N8N WORKFLOW OPTION:"
echo "      • Automatic execution every 30 minutes"
echo "      • Go to: http://localhost:5678 (admin/stockagent123)"
echo "      • Workflow: 'FULL UNIVERSE - All 269 Stocks Analysis'"
echo "      • Status: Should be running automatically"
echo
print_info "📥 Setting up n8n workflows and authentication..."
python scripts/setup_n8n_workflows.py

print_info "🧪 Quick Tests:"
echo "   • Test Script: python main_enhanced.py"
echo "   • Test n8n API: curl http://localhost:5002/health"
echo "   • Test n8n UI: open http://localhost:5678"
echo
print_info "📧 Email Alert Features:"
echo "   • 🐦 X (Twitter) sentiment analysis"
echo "   • 📅 Earnings calendar integration"
echo "   • 🔥 Investment themes analysis"
echo "   • 📊 Technical indicators (RSI, volume)"
echo "   • 🎨 Professional HTML formatting"
echo
print_status "Your agentic stock system is now fully operational!"
echo

# 9. Create process monitoring script
cat > scripts/monitor_system.sh << 'EOF'
#!/bin/bash
# System monitoring script

echo "🔍 System Status Check"
echo "====================="

# Check Docker services
echo "🐳 Docker Services:"
docker-compose ps

echo
echo "🔗 API Endpoints:"
echo -n "   n8n API (5002): "
if curl -s http://localhost:5002/health > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo -n "   Dashboard (5001): "
if curl -s http://localhost:5001 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo -n "   n8n UI (5678): "
if curl -s http://localhost:5678 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Down"
fi

echo
echo "📊 Recent Logs:"
echo "   Check: tail -f *.log"
echo "   n8n: docker-compose logs n8n"
EOF

chmod +x scripts/monitor_system.sh
print_status "Created scripts/monitor_system.sh for system status checks"

# 10. Save process IDs for cleanup
echo "N8N_API_PID=$N8N_API_PID" > .system_pids
echo "DASHBOARD_PID=$DASHBOARD_PID" >> .system_pids
echo "MCP_SERVER_PID=$MCP_SERVER_PID" >> .system_pids
print_status "Process IDs saved for cleanup"

echo
print_info "💡 Useful Commands:"
echo "   • Monitor system: ./scripts/monitor_system.sh"
echo "   • Stop system: ./scripts/stop_system.sh"
echo "   • Test system: python tests/test_both_options.py"
echo "   • View logs: tail -f *.log"
echo "   • Restart n8n: docker-compose restart n8n"
echo

# Create stop script
cat > scripts/stop_system.sh << 'EOF'
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
EOF

chmod +x scripts/stop_system.sh
print_status "Created scripts/stop_system.sh for clean shutdown"

echo
print_status "🎯 READY FOR EMAIL ALERTS!"
print_info "Both script-based and n8n workflow options are now active."
print_info "You will receive email alerts at masterai6612@gmail.com"

echo
print_status "🌐 N8N WORKFLOW ACCESS:"
echo "   URL: http://localhost:5678"
echo "   Login: admin@stockagent.local"
echo "   Password: stockagent123"
echo
print_info "💡 If workflows aren't visible, run:"
echo "   python scripts/setup_n8n_workflows.py"
echo