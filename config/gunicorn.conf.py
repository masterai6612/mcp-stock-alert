# Gunicorn Configuration for Stock Alert Dashboard
# Production-ready WSGI server configuration

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # Recommended formula
worker_class = "sync"
worker_connections = 1000
timeout = 120
keepalive = 5

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload app for better performance
preload_app = True

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "stock-dashboard"

# Daemon mode (set to True to run in background)
daemon = False

# PID file
pidfile = "/tmp/stock-dashboard.pid"

# User/group to run as (uncomment and modify if needed)
# user = "www-data"
# group = "www-data"

# Temp directory
tmp_upload_dir = None

# SSL (uncomment and configure if using HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Environment variables
raw_env = [
    'FLASK_ENV=production',
    'PYTHONPATH=/Users/monie/Desktop/kiro/mcp-stock-alert copy'
]

# Graceful timeout for worker restart
graceful_timeout = 30

# Enable automatic worker restarts
max_worker_memory = 200  # MB (requires psutil)
worker_tmp_dir = "/dev/shm"  # Use RAM disk for better performance

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("🚀 Stock Alert Dashboard is ready!")
    server.log.info("📊 Access at: http://localhost:5001")

def worker_int(worker):
    """Called just after a worker has been killed."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")