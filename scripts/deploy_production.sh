#!/bin/bash
# Production Deployment Script
# Automates the deployment process for production environments

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."
echo "=================================="

# Configuration
PROJECT_DIR="/opt/stock-alert"
SERVICE_USER="stockalert"
NGINX_AVAILABLE="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warn() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   log_error "This script should not be run as root for security reasons"
   exit 1
fi

# Check if sudo is available
if ! command -v sudo &> /dev/null; then
    log_error "sudo is required but not installed"
    exit 1
fi

echo "📋 Pre-deployment Checklist:"
echo "1. Do you have a domain name ready? (y/n)"
read -r domain_ready
echo "2. Do you have production email credentials? (y/n)"
read -r email_ready
echo "3. Have you updated the .env file with production values? (y/n)"
read -r env_ready

if [[ "$domain_ready" != "y" || "$email_ready" != "y" || "$env_ready" != "y" ]]; then
    log_warn "Please complete the checklist before proceeding"
    exit 1
fi

echo "🔧 Installing System Dependencies..."
sudo apt update
sudo apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    htop \
    curl \
    git

log_info "System dependencies installed"

echo "👤 Creating Service User..."
if ! id "$SERVICE_USER" &>/dev/null; then
    sudo useradd -r -s /bin/false -d "$PROJECT_DIR" "$SERVICE_USER"
    log_info "Service user '$SERVICE_USER' created"
else
    log_info "Service user '$SERVICE_USER' already exists"
fi

echo "📁 Setting up Project Directory..."
if [[ ! -d "$PROJECT_DIR" ]]; then
    sudo mkdir -p "$PROJECT_DIR"
    sudo chown "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"
    log_info "Project directory created at $PROJECT_DIR"
fi

echo "🔐 Configuring Firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 5001/tcp # Dashboard (can be removed after nginx setup)
log_info "Firewall configured"

echo "🐳 Starting Docker Services..."
if [[ -f "config/docker-compose.yml" ]]; then
    sudo docker-compose -f config/docker-compose.yml up -d
    log_info "Docker services started"
else
    log_warn "Docker compose file not found, skipping Docker setup"
fi

echo "🌐 Configuring Nginx..."
if [[ -f "config/nginx.conf" ]]; then
    sudo cp config/nginx.conf "$NGINX_AVAILABLE/stock-alert"
    
    # Enable site
    if [[ ! -L "$NGINX_ENABLED/stock-alert" ]]; then
        sudo ln -s "$NGINX_AVAILABLE/stock-alert" "$NGINX_ENABLED/stock-alert"
    fi
    
    # Test nginx configuration
    if sudo nginx -t; then
        sudo systemctl reload nginx
        log_info "Nginx configured and reloaded"
    else
        log_error "Nginx configuration test failed"
        exit 1
    fi
else
    log_warn "Nginx configuration file not found, skipping nginx setup"
fi

echo "🔒 Setting File Permissions..."
chmod 600 .env 2>/dev/null || log_warn ".env file not found"
chmod +x scripts/*.sh 2>/dev/null || log_warn "No scripts to make executable"
chmod +x *.sh 2>/dev/null || log_warn "No shell scripts to make executable"
log_info "File permissions set"

echo "🔍 Running Health Checks..."
sleep 5  # Give services time to start

# Check if dashboard is responding
if curl -s http://localhost:5001/api/status > /dev/null; then
    log_info "Dashboard is responding"
else
    log_warn "Dashboard not responding (may need manual start)"
fi

# Check if n8n is responding
if curl -s http://localhost:5678/healthz > /dev/null; then
    log_info "n8n is responding"
else
    log_warn "n8n not responding (may need manual start)"
fi

echo ""
echo "🎉 Production Deployment Complete!"
echo "=================================="
echo ""
echo "📊 Next Steps:"
echo "1. Configure your domain DNS to point to this server"
echo "2. Run SSL setup: sudo certbot --nginx -d your-domain.com"
echo "3. Test the system: curl http://your-server-ip:5001/api/status"
echo "4. Access n8n: http://your-server-ip:5678 (admin/stockagent123)"
echo "5. Change default passwords!"
echo ""
echo "📋 Important URLs:"
echo "• Dashboard: http://$(curl -s ifconfig.me):5001"
echo "• n8n: http://$(curl -s ifconfig.me):5678"
echo ""
echo "🔒 Security Reminders:"
echo "• Change n8n password from default"
echo "• Update .env with production email credentials"
echo "• Set up SSL certificates"
echo "• Configure monitoring and backups"
echo ""
log_info "Deployment script completed successfully!"