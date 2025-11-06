#!/bin/bash
# Production Health Monitoring Script
# Monitors system health and automatically restarts failed services

# Configuration
LOG_FILE="/var/log/stock-alert-health.log"
ALERT_EMAIL="masterai6612@gmail.com"
MAX_RETRIES=3
RETRY_DELAY=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Logging function
log_message() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log_message "INFO" "${GREEN}✅ $1${NC}"
}

log_warn() {
    log_message "WARN" "${YELLOW}⚠️ $1${NC}"
}

log_error() {
    log_message "ERROR" "${RED}❌ $1${NC}"
}

# Service restart function
restart_service() {
    local service=$1
    local command=$2
    local retries=0
    
    log_warn "Attempting to restart $service..."
    
    while [[ $retries -lt $MAX_RETRIES ]]; do
        eval "$command"
        sleep $RETRY_DELAY
        
        # Check if service is now healthy
        case $service in
            "dashboard")
                if curl -s http://localhost:5001/api/status > /dev/null; then
                    log_info "$service restarted successfully"
                    return 0
                fi
                ;;
            "n8n")
                if curl -s http://localhost:5678/healthz > /dev/null; then
                    log_info "$service restarted successfully"
                    return 0
                fi
                ;;
        esac
        
        retries=$((retries + 1))
        log_warn "$service restart attempt $retries/$MAX_RETRIES failed"
    done
    
    log_error "$service failed to restart after $MAX_RETRIES attempts"
    return 1
}

# Send alert email
send_alert() {
    local subject=$1
    local message=$2
    
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "$subject" "$ALERT_EMAIL"
        log_info "Alert email sent to $ALERT_EMAIL"
    else
        log_warn "Mail command not available, cannot send alert email"
    fi
}

# System resource checks
check_system_resources() {
    # Check disk space
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    if [[ $disk_usage -gt 90 ]]; then
        log_error "Critical disk usage: ${disk_usage}%"
        send_alert "🚨 Critical Disk Usage" "Disk usage is at ${disk_usage}% on $(hostname)"
    elif [[ $disk_usage -gt 80 ]]; then
        log_warn "High disk usage: ${disk_usage}%"
    fi
    
    # Check memory usage
    local mem_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100.0}')
    if [[ $mem_usage -gt 90 ]]; then
        log_error "Critical memory usage: ${mem_usage}%"
        send_alert "🚨 Critical Memory Usage" "Memory usage is at ${mem_usage}% on $(hostname)"
    elif [[ $mem_usage -gt 80 ]]; then
        log_warn "High memory usage: ${mem_usage}%"
    fi
    
    # Check load average
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local cpu_cores=$(nproc)
    local load_threshold=$(echo "$cpu_cores * 2" | bc -l)
    
    if (( $(echo "$load_avg > $load_threshold" | bc -l) )); then
        log_warn "High load average: $load_avg (threshold: $load_threshold)"
    fi
}

# Check dashboard health
check_dashboard() {
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5001/api/status)
    
    if [[ "$status_code" == "200" ]]; then
        log_info "Dashboard is healthy (HTTP $status_code)"
        return 0
    else
        log_error "Dashboard is unhealthy (HTTP $status_code)"
        
        # Try to restart dashboard
        if systemctl is-active --quiet stock-dashboard; then
            restart_service "dashboard" "sudo systemctl restart stock-dashboard"
        else
            restart_service "dashboard" "cd /opt/stock-alert && ./start_complete_system.sh"
        fi
        
        return 1
    fi
}

# Check n8n health
check_n8n() {
    local status_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz)
    
    if [[ "$status_code" == "200" ]]; then
        log_info "n8n is healthy (HTTP $status_code)"
        return 0
    else
        log_error "n8n is unhealthy (HTTP $status_code)"
        
        # Try to restart n8n
        if command -v docker-compose &> /dev/null; then
            restart_service "n8n" "cd /opt/stock-alert && sudo docker-compose -f config/docker-compose.yml restart n8n"
        else
            log_error "Docker compose not available, cannot restart n8n"
        fi
        
        return 1
    fi
}

# Check process health
check_processes() {
    local critical_processes=("gunicorn" "python")
    local missing_processes=()
    
    for process in "${critical_processes[@]}"; do
        if ! pgrep -f "$process" > /dev/null; then
            missing_processes+=("$process")
        fi
    done
    
    if [[ ${#missing_processes[@]} -gt 0 ]]; then
        log_warn "Missing processes: ${missing_processes[*]}"
    else
        log_info "All critical processes are running"
    fi
}

# Check log file sizes
check_log_sizes() {
    local max_size_mb=100
    local log_dirs=("/var/log" "/tmp" ".")
    
    for dir in "${log_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            find "$dir" -name "*.log" -size +${max_size_mb}M 2>/dev/null | while read -r large_log; do
                log_warn "Large log file detected: $large_log (>$max_size_mb MB)"
            done
        fi
    done
}

# Main health check function
run_health_checks() {
    log_info "Starting health check cycle..."
    
    local failed_checks=0
    
    # System resource checks
    check_system_resources
    
    # Service health checks
    if ! check_dashboard; then
        failed_checks=$((failed_checks + 1))
    fi
    
    if ! check_n8n; then
        failed_checks=$((failed_checks + 1))
    fi
    
    # Process checks
    check_processes
    
    # Log size checks
    check_log_sizes
    
    # Summary
    if [[ $failed_checks -eq 0 ]]; then
        log_info "All health checks passed ✅"
    else
        log_error "$failed_checks health check(s) failed ❌"
        send_alert "🚨 Stock Alert System Health Issues" "$failed_checks service(s) failed health checks on $(hostname). Check logs for details."
    fi
    
    log_info "Health check cycle completed"
    echo "----------------------------------------"
}

# Create log directory if it doesn't exist
sudo mkdir -p "$(dirname "$LOG_FILE")"
sudo touch "$LOG_FILE"
sudo chmod 666 "$LOG_FILE"

# Run health checks
if [[ "${1:-}" == "--continuous" ]]; then
    log_info "Starting continuous health monitoring..."
    while true; do
        run_health_checks
        sleep 300  # Check every 5 minutes
    done
else
    run_health_checks
fi