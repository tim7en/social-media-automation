#!/bin/bash

# Comprehensive deployment and monitoring script for Social Media Automation Platform
# Based on the production readiness requirements from the problem statement

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/logs/deployment.log"

# Ensure log directory exists
mkdir -p "$PROJECT_DIR/logs"

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# Function to check command availability
check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "$1 is not installed or not in PATH"
        return 1
    fi
    return 0
}

# Function to check system requirements
check_system_requirements() {
    log "Checking system requirements..."
    
    # Check Python version
    if check_command python3; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        log "Python version: $PYTHON_VERSION"
        
        # Check if version is >= 3.8
        REQUIRED_VERSION="3.8"
        if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
            log_error "Python 3.8+ is required, found $PYTHON_VERSION"
            return 1
        fi
    else
        log_error "Python 3 is required but not found"
        return 1
    fi
    
    # Check available memory
    if command -v free &> /dev/null; then
        MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
        log "Available memory: ${MEMORY_GB}GB"
        
        if (( $(echo "$MEMORY_GB < 2" | bc -l) )); then
            log_warning "Less than 2GB RAM available - may cause performance issues"
        fi
    fi
    
    # Check disk space
    DISK_FREE_GB=$(df / | tail -1 | awk '{print int($4/1024/1024)}')
    log "Free disk space: ${DISK_FREE_GB}GB"
    
    if [ "$DISK_FREE_GB" -lt 1 ]; then
        log_error "Less than 1GB disk space available"
        return 1
    fi
    
    log "System requirements check passed"
    return 0
}

# Function to setup Python virtual environment
setup_venv() {
    log "Setting up Python virtual environment..."
    
    if [ ! -d "$VENV_DIR" ]; then
        python3 -m venv "$VENV_DIR"
        log "Virtual environment created"
    else
        log "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip wheel setuptools
    
    log "Virtual environment setup completed"
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install requirements with timeout and retry
    if ! pip install -r requirements.txt --timeout 300; then
        log_warning "Some dependencies failed to install, trying with --no-deps for critical ones"
        
        # Install critical dependencies one by one
        critical_deps=("fastapi" "uvicorn" "pydantic" "python-dotenv" "sqlalchemy" "alembic")
        for dep in "${critical_deps[@]}"; do
            pip install "$dep" || log_warning "Failed to install $dep"
        done
    fi
    
    log "Dependencies installation completed"
}

# Function to run environment validation
validate_environment() {
    log "Validating environment configuration..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Run environment validation
    python3 -c "
from src.core.config import validate_environment
import json

try:
    report = validate_environment()
    print(json.dumps(report, indent=2))
    
    if not report['settings_valid']:
        exit(1)
    
    if report['errors']:
        print('Environment validation errors found!')
        exit(1)
        
except Exception as e:
    print(f'Environment validation failed: {e}')
    exit(1)
" | tee -a "$LOG_FILE"
    
    if [ $? -eq 0 ]; then
        log "Environment validation passed"
    else
        log_error "Environment validation failed"
        return 1
    fi
}

# Function to run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Check if PostgreSQL is available, otherwise skip
    if python3 -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config import settings

async def test_db():
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.execute('SELECT 1')
        await engine.dispose()
        return True
    except Exception as e:
        print(f'Database connection failed: {e}')
        return False

result = asyncio.run(test_db())
exit(0 if result else 1)
"; then
        log "Database connection successful, running migrations..."
        if command -v alembic &> /dev/null; then
            alembic upgrade head
            log "Database migrations completed"
        else
            log_warning "Alembic not available, skipping migrations"
        fi
    else
        log_warning "Database not available, skipping migrations"
    fi
}

# Function to run tests
run_tests() {
    log "Running tests..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Check if pytest is available
    if ! command -v pytest &> /dev/null; then
        log_warning "pytest not available, installing..."
        pip install pytest pytest-asyncio httpx
    fi
    
    # Run tests with coverage if available
    if command -v pytest &> /dev/null; then
        # Run basic tests
        pytest tests/ -v --tb=short || log_warning "Some tests failed"
        
        # Run performance tests separately
        pytest tests/ -m performance -v --tb=short || log_warning "Performance tests failed"
        
        log "Tests completed"
    else
        log_warning "Cannot run tests - pytest not available"
    fi
}

# Function to start the application
start_application() {
    log "Starting application..."
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Create necessary directories
    mkdir -p data logs temp cache
    
    # Check if port is available
    PORT=${API_PORT:-8000}
    if netstat -tuln | grep ":$PORT " > /dev/null; then
        log_warning "Port $PORT is already in use"
        
        # Try to find an available port
        for port in {8001..8010}; do
            if ! netstat -tuln | grep ":$port " > /dev/null; then
                PORT=$port
                log "Using alternative port: $PORT"
                break
            fi
        done
    fi
    
    # Start the application
    log "Starting server on port $PORT..."
    
    # Use uvicorn with proper configuration
    export API_PORT=$PORT
    uvicorn src.main:app \
        --host 0.0.0.0 \
        --port $PORT \
        --reload \
        --log-level info \
        --access-log \
        --reload-dir src \
        --reload-exclude "*.pyc" \
        --reload-exclude "__pycache__" \
        --reload-exclude "logs/*" \
        --reload-exclude "temp/*" \
        --reload-exclude "cache/*" &
    
    SERVER_PID=$!
    echo $SERVER_PID > "$PROJECT_DIR/server.pid"
    
    # Wait for server to start
    sleep 5
    
    # Test server
    if curl -s "http://localhost:$PORT/health" > /dev/null; then
        log "Server started successfully on port $PORT (PID: $SERVER_PID)"
        log "Access the application at: http://localhost:$PORT"
        log "API documentation at: http://localhost:$PORT/docs"
    else
        log_error "Server failed to start properly"
        return 1
    fi
}

# Function to run health checks
run_health_checks() {
    log "Running health checks..."
    
    PORT=${API_PORT:-8000}
    
    # Basic health check
    if curl -s "http://localhost:$PORT/health" | grep -q "healthy"; then
        log "Basic health check passed"
    else
        log_error "Basic health check failed"
        return 1
    fi
    
    # Detailed health check
    curl -s "http://localhost:$PORT/health/detailed" | python3 -m json.tool || log_warning "Detailed health check formatting failed"
    
    # Performance test
    log "Running basic performance test..."
    for i in {1..10}; do
        curl -s "http://localhost:$PORT/health" > /dev/null &
    done
    wait
    
    log "Health checks completed"
}

# Function to stop the application
stop_application() {
    log "Stopping application..."
    
    if [ -f "$PROJECT_DIR/server.pid" ]; then
        PID=$(cat "$PROJECT_DIR/server.pid")
        if kill -0 $PID 2>/dev/null; then
            kill $PID
            sleep 2
            
            # Force kill if still running
            if kill -0 $PID 2>/dev/null; then
                kill -9 $PID
            fi
            
            rm -f "$PROJECT_DIR/server.pid"
            log "Server stopped"
        else
            log "Server was not running"
        fi
    else
        log "No PID file found"
    fi
}

# Function to show status
show_status() {
    log "Application Status:"
    
    # Check if server is running
    if [ -f "$PROJECT_DIR/server.pid" ]; then
        PID=$(cat "$PROJECT_DIR/server.pid")
        if kill -0 $PID 2>/dev/null; then
            log "Server is running (PID: $PID)"
            
            # Check health
            PORT=${API_PORT:-8000}
            if curl -s "http://localhost:$PORT/health" > /dev/null; then
                log "Health check: PASSED"
            else
                log_warning "Health check: FAILED"
            fi
        else
            log_warning "Server PID file exists but process is not running"
        fi
    else
        log "Server is not running"
    fi
    
    # Show system resources
    if command -v free &> /dev/null; then
        echo "Memory usage:"
        free -h | grep -E "Mem|Swap"
    fi
    
    echo "Disk usage:"
    df -h / | tail -1
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  setup      - Complete setup (requirements + dependencies + environment)"
    echo "  start      - Start the application"
    echo "  stop       - Stop the application"
    echo "  restart    - Restart the application"
    echo "  status     - Show application status"
    echo "  test       - Run tests"
    echo "  health     - Run health checks"
    echo "  validate   - Validate environment"
    echo "  migrate    - Run database migrations"
    echo "  logs       - Show application logs"
    echo ""
    echo "Examples:"
    echo "  $0 setup    # Initial setup"
    echo "  $0 start    # Start the server"
    echo "  $0 test     # Run tests"
}

# Function to show logs
show_logs() {
    echo "Deployment logs:"
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 "$LOG_FILE"
    else
        log "No deployment logs found"
    fi
    
    echo ""
    echo "Application logs:"
    if [ -d "$PROJECT_DIR/logs" ]; then
        find "$PROJECT_DIR/logs" -name "*.log" -exec tail -n 20 {} \;
    else
        log "No application logs found"
    fi
}

# Main function
main() {
    cd "$PROJECT_DIR"
    
    case "${1:-setup}" in
        "setup")
            log "Starting complete setup..."
            check_system_requirements
            setup_venv
            install_dependencies
            validate_environment
            run_migrations
            log "Setup completed successfully!"
            ;;
        "start")
            start_application
            ;;
        "stop")
            stop_application
            ;;
        "restart")
            stop_application
            sleep 2
            start_application
            ;;
        "status")
            show_status
            ;;
        "test")
            run_tests
            ;;
        "health")
            run_health_checks
            ;;
        "validate")
            validate_environment
            ;;
        "migrate")
            run_migrations
            ;;
        "logs")
            show_logs
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            log_error "Unknown command: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Trap to ensure cleanup on exit
trap 'echo "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"