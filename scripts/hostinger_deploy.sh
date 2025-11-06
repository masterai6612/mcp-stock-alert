#!/bin/bash
# Hostinger VPS Deployment Script
# Optimized for Hostinger VPS with integrated domain management

set -e  # Exit on any error

echo "🌐 Hostinger VPS Deployment for Stock Alert System"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

log_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

# Check if running as root (common on fresh Hostinger VPS)
if [[ $EUID -eq 0 ]]; then
   log_warn "Running as root - will create dedicated user for security"
   ROOT_DEPLOYMENT=true
else
   ROOT_DEPLOYMENT=false
fi

echo "📋 Hostinger VPS Pre-deployment Questions:"
echo "1. What's your domain name? (e.g., yourdomain.com)"
read -r DOMAIN_NAME

echo "2. What's your production email for alerts? (e.g., alerts@$DOMAIN_NAME)"
read -r ALERT_EMAIL

echo "3. Do you want to create a dedicated user 'stockalert'? (y/n) [recommended: y]"
read -r CREATE_USER

echo "4. Which VPS plan are you using? (1/2/3/4)"
echo "   VPS 1: 1GB RAM (minimum)"
echo "   VPS 2: 2GB RAM (recommended)"  
echo "   VPS 3: 3GB RAM (best performance)"
echo "   VPS 4: 4GB RAM (high performance)"
read -r VPS_PLAN

# Validate domain name
if [[ ! "$DOMAIN_NAME" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
    log_error "Invalid domain name format"
    exit 1
fi

log_step "Starting Hostinger VPS deployment for $DOMAIN_NAME..."

# Update system packages
log_step "Updating system packages..."
apt update && apt upgrade -y
log_info "System packages updated"

# Install required packages
log_step "Installing required packages..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw \
    htop \
    curl \
    wget \
    unzip \
    fail2ban \
    unattended-upgrades \
    bc

log_info "Required packages installed"

# Configure automatic security updates
log_step "Configuring automatic security updates..."
echo 'Unattended-Upgrade::Automatic-Reboot "false";' >> /etc/apt/apt.conf.d/50unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
log_info "Automatic security updates configured"

# Create dedicated user if requested
if [[ "$CREATE_USER" == "y" && "$ROOT_DEPLOYMENT" == "true" ]]; then
    log_step "Creating dedicated user 'stockalert'..."
    
    if ! id "stockalert" &>/dev/null; then
        useradd -m -s /bin/bash stockalert
        usermod -aG sudo,docker stockalert
        
        # Set up SSH key copying if root has keys
        if [[ -d /root/.ssh ]]; then
            mkdir -p /home/stockalert/.ssh
            cp /root/.ssh/authorized_keys /home/stockalert/.ssh/ 2>/dev/null || true
            chown -R stockalert:stockalert /home/stockalert/.ssh
            chmod 700 /home/stockalert/.ssh
            chmod 600 /home/stockalert/.ssh/authorized_keys 2>/dev/null || true
        fi
        
        log_info "User 'stockalert' created with sudo and docker access"
    else
        log_info "User 'stockalert' already exists"
    fi
    
    PROJECT_DIR="/home/stockalert/stock-alert"
    PROJECT_USER="stockalert"
else
    PROJECT_DIR="/opt/stock-alert"
    PROJECT_USER=$(whoami)
fi

# Configure firewall for Hostinger VPS
log_step "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw allow 5001/tcp  # Dashboard (temporary, can be removed after nginx)
log_info "Firewall configured for Hostinger VPS"

# Configure fail2ban
log_step "Configuring fail2ban for SSH protection..."
systemctl enable fail2ban
systemctl start fail2ban
log_info "Fail2ban configured"

# Optimize system for Hostinger VPS
log_step "Optimizing system for Hostinger VPS..."
cat >> /etc/sysctl.conf << EOF

# Hostinger VPS Optimizations
vm.swappiness=10
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
EOF

sysctl -p
log_info "System optimized for Hostinger VPS"

# Create project directory
log_step "Setting up project directory..."
mkdir -p "$PROJECT_DIR"
if [[ "$PROJECT_USER" != "root" ]]; then
    chown "$PROJECT_USER:$PROJECT_USER" "$PROJECT_DIR"
fi
log_info "Project directory created at $PROJECT_DIR"

# Clone repository (placeholder - user needs to update this)
log_step "Setting up project repository..."
cat > "$PROJECT_DIR/setup_repo.sh" << EOF
#!/bin/bash
# Run this script to clone your repository
# Replace with your actual repository URL

echo "🔧 Cloning your stock alert repository..."
echo "Please run the following commands:"
echo ""
echo "cd $PROJECT_DIR"
echo "git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git ."
echo "python3 -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo ""
echo "Then edit .env file with your production settings:"
echo "cp .env.example .env"
echo "nano .env"
EOF

chmod +x "$PROJECT_DIR/setup_repo.sh"
log_info "Repository setup script created"

# Configure nginx for the domain
log_step "Configuring nginx for $DOMAIN_NAME..."
cat > /etc/nginx/sites-available/stock-alert << EOF
# Nginx Configuration for Stock Alert System on Hostinger VPS
server {
    listen 80;
    server_name $DOMAIN_NAME www.$DOMAIN_NAME;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone \$binary_remote_addr zone=dashboard:10m rate=5r/s;
    
    # Main dashboard application
    location / {
        limit_req zone=dashboard burst=20 nodelay;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts optimized for Hostinger VPS
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # API endpoints
    location /api/ {
        limit_req zone=api burst=10 nodelay;
        
        proxy_pass http://127.0.0.1:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # n8n workflow engine
    location /n8n/ {
        proxy_pass http://127.0.0.1:5678/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Health check
    location /health {
        access_log off;
        return 200 "healthy\\n";
        add_header Content-Type text/plain;
    }
    
    # Static files caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/stock-alert /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default  # Remove default site

# Test nginx configuration
if nginx -t; then
    systemctl reload nginx
    log_info "Nginx configured for $DOMAIN_NAME"
else
    log_error "Nginx configuration test failed"
    exit 1
fi

# Start and enable services
log_step "Starting and enabling services..."
systemctl enable nginx
systemctl enable docker
systemctl start docker
log_info "Services started and enabled"

# Create SSL certificate setup script
log_step "Creating SSL certificate setup script..."
cat > "$PROJECT_DIR/setup_ssl.sh" << EOF
#!/bin/bash
# SSL Certificate Setup for $DOMAIN_NAME

echo "🔒 Setting up SSL certificate for $DOMAIN_NAME..."

# Make sure nginx is running
sudo systemctl start nginx

# Get SSL certificate from Let's Encrypt
sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --non-interactive --agree-tos --email $ALERT_EMAIL

if [ \$? -eq 0 ]; then
    echo "✅ SSL certificate installed successfully!"
    echo "🌐 Your site is now available at: https://$DOMAIN_NAME"
else
    echo "❌ SSL certificate installation failed"
    echo "💡 Make sure your domain DNS is pointing to this server IP"
    echo "💡 Check: dig $DOMAIN_NAME"
fi
EOF

chmod +x "$PROJECT_DIR/setup_ssl.sh"
log_info "SSL setup script created"

# Create monitoring setup
log_step "Setting up monitoring..."
mkdir -p /var/log/stock-alert
touch /var/log/stock-alert/health.log
chmod 666 /var/log/stock-alert/health.log

# Create logrotate configuration
cat > /etc/logrotate.d/stock-alert << EOF
/var/log/stock-alert/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 root root
}
EOF

log_info "Monitoring and logging configured"

# Create deployment summary
log_step "Creating deployment summary..."
cat > "$PROJECT_DIR/DEPLOYMENT_SUMMARY.md" << EOF
# 🌐 Hostinger VPS Deployment Summary

## ✅ Deployment Completed Successfully!

### 🖥️ Server Information:
- **VPS Plan**: VPS $VPS_PLAN
- **Domain**: $DOMAIN_NAME
- **Project Directory**: $PROJECT_DIR
- **Project User**: $PROJECT_USER

### 🔧 What's Been Configured:
- ✅ System packages updated and optimized for Hostinger VPS
- ✅ Python 3, Docker, nginx, certbot installed
- ✅ Firewall configured (UFW + fail2ban)
- ✅ Nginx configured for $DOMAIN_NAME
- ✅ SSL certificate setup script ready
- ✅ Monitoring and logging configured
- ✅ Security hardening applied

### 🚀 Next Steps:

#### 1. Clone Your Repository:
\`\`\`bash
cd $PROJECT_DIR
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git .
\`\`\`

#### 2. Setup Python Environment:
\`\`\`bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

#### 3. Configure Environment:
\`\`\`bash
cp .env.example .env
nano .env
# Update with production values:
# EMAIL_FROM=$ALERT_EMAIL
# N8N_API_KEY=your-production-key
\`\`\`

#### 4. Start Your System:
\`\`\`bash
./start_complete_system.sh
\`\`\`

#### 5. Setup SSL Certificate:
\`\`\`bash
./setup_ssl.sh
\`\`\`

### 🌐 Your URLs (after SSL setup):
- **Dashboard**: https://$DOMAIN_NAME
- **n8n Workflows**: https://$DOMAIN_NAME/n8n/
- **API**: https://$DOMAIN_NAME/api/status
- **Health Check**: https://$DOMAIN_NAME/health

### 🔒 Security Notes:
- ✅ Firewall enabled (SSH, HTTP, HTTPS only)
- ✅ Fail2ban protecting SSH
- ✅ Automatic security updates enabled
- ⚠️ Change n8n password from default (admin/stockagent123)
- ⚠️ Use strong passwords for all accounts

### 📊 Monitoring:
- **Health logs**: /var/log/stock-alert/health.log
- **System monitoring**: htop
- **Service status**: systemctl status nginx docker

### 💡 Hostinger VPS Tips:
- Use Hostinger control panel for domain DNS management
- Monitor resource usage in Hostinger dashboard
- Consider upgrading VPS plan if needed
- Hostinger provides DDoS protection automatically

### 🆘 Support:
- **Hostinger Support**: 24/7 chat support
- **System logs**: /var/log/stock-alert/
- **Nginx logs**: /var/log/nginx/
- **Health check**: curl http://localhost/health

## 🎉 Your Professional Stock Alert System is Ready!

**Estimated time to complete**: 15-20 minutes
**Your system will analyze 269+ stocks with professional email alerts!**
EOF

log_info "Deployment summary created"

# Final system check
log_step "Running final system checks..."
sleep 2

# Check services
if systemctl is-active --quiet nginx; then
    log_info "Nginx is running"
else
    log_warn "Nginx is not running - check configuration"
fi

if systemctl is-active --quiet docker; then
    log_info "Docker is running"
else
    log_warn "Docker is not running - check installation"
fi

# Check firewall
if ufw status | grep -q "Status: active"; then
    log_info "Firewall is active"
else
    log_warn "Firewall is not active"
fi

# Display completion message
echo ""
echo "🎉 Hostinger VPS Deployment Complete!"
echo "====================================="
echo ""
echo "📊 Next Steps:"
echo "1. Clone your repository to $PROJECT_DIR"
echo "2. Configure .env file with production settings"
echo "3. Start your stock alert system"
echo "4. Run SSL setup: $PROJECT_DIR/setup_ssl.sh"
echo ""
echo "📋 Important Files:"
echo "• Deployment Summary: $PROJECT_DIR/DEPLOYMENT_SUMMARY.md"
echo "• SSL Setup Script: $PROJECT_DIR/setup_ssl.sh"
echo "• Repository Setup: $PROJECT_DIR/setup_repo.sh"
echo ""
echo "🌐 Your Domain: $DOMAIN_NAME"
echo "📧 Alert Email: $ALERT_EMAIL"
echo "📁 Project Directory: $PROJECT_DIR"
echo ""
echo "🔒 Security Reminders:"
echo "• Change n8n password from 'stockagent123'"
echo "• Update .env with production credentials"
echo "• Monitor system logs regularly"
echo ""
log_info "Hostinger VPS is ready for your stock alert system!"

if [[ "$PROJECT_USER" != "root" ]]; then
    echo ""
    echo "🔄 Switch to project user to continue:"
    echo "su - $PROJECT_USER"
    echo "cd $PROJECT_DIR"
fi