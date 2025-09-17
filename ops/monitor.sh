#!/bin/bash
# Monitoring and maintenance script for Excel Interviewer
set -e

# Configuration
APP_NAME="excel-interviewer"
CONTAINER_NAME="$APP_NAME-container"
LOG_DIR="./logs"
BACKUP_DIR="./backups"
DATA_DIR="./data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[STATUS]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check application health
check_health() {
    print_status "Checking application health..."
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        print_error "Container is not running"
        return 1
    fi
    
    # Check if container is healthy
    health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "unknown")
    
    case "$health_status" in
        "healthy")
            print_success "Container is healthy"
            ;;
        "unhealthy")
            print_error "Container is unhealthy"
            return 1
            ;;
        "starting")
            print_warning "Container is still starting..."
            ;;
        *)
            print_warning "Health status unknown, checking HTTP endpoint..."
            if curl -f "http://localhost:8000/health" > /dev/null 2>&1; then
                print_success "HTTP health check passed"
            else
                print_error "HTTP health check failed"
                return 1
            fi
            ;;
    esac
    
    return 0
}

# Get application status and metrics
get_status() {
    echo "📊 Excel Interviewer Status Report"
    echo "================================="
    echo ""
    
    # Container status
    if docker ps | grep -q "$CONTAINER_NAME"; then
        echo "🟢 Container Status: Running"
        
        # Uptime
        uptime=$(docker inspect --format='{{.State.StartedAt}}' "$CONTAINER_NAME" | xargs -I {} date -d {} +%s)
        current=$(date +%s)
        uptime_seconds=$((current - uptime))
        uptime_human=$(printf '%dd %dh %dm %ds' $((uptime_seconds/86400)) $((uptime_seconds%86400/3600)) $((uptime_seconds%3600/60)) $((uptime_seconds%60)))
        echo "⏱️  Uptime: $uptime_human"
        
        # Resource usage
        stats=$(docker stats "$CONTAINER_NAME" --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}")
        echo "💻 Resource Usage:"
        echo "$stats" | sed 's/^/   /'
        
    else
        echo "🔴 Container Status: Not Running"
    fi
    
    echo ""
    
    # Database status
    if [ -f "$DATA_DIR/interviews.db" ]; then
        db_size=$(stat -f%z "$DATA_DIR/interviews.db" 2>/dev/null || stat -c%s "$DATA_DIR/interviews.db" 2>/dev/null || echo "0")
        db_size_human=$(numfmt --to=iec "$db_size" 2>/dev/null || echo "${db_size} bytes")
        echo "🗄️  Database Size: $db_size_human"
        
        # Get interview count
        if command -v sqlite3 &> /dev/null; then
            interview_count=$(sqlite3 "$DATA_DIR/interviews.db" "SELECT COUNT(*) FROM interviews;" 2>/dev/null || echo "Unknown")
            echo "📋 Total Interviews: $interview_count"
        fi
    else
        echo "🗄️  Database: Not found"
    fi
    
    echo ""
    
    # Disk usage
    if [ -d "$DATA_DIR" ]; then
        data_usage=$(du -sh "$DATA_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
        echo "💾 Data Directory Size: $data_usage"
    fi
    
    if [ -d "$LOG_DIR" ]; then
        log_usage=$(du -sh "$LOG_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
        echo "📝 Log Directory Size: $log_usage"
    fi
    
    if [ -d "$BACKUP_DIR" ]; then
        backup_usage=$(du -sh "$BACKUP_DIR" 2>/dev/null | cut -f1 || echo "Unknown")
        backup_count=$(find "$BACKUP_DIR" -type d -mindepth 1 2>/dev/null | wc -l || echo "0")
        echo "💼 Backups: $backup_count backups, $backup_usage total"
    fi
}

# View application logs
view_logs() {
    local lines="${1:-50}"
    
    print_status "Showing last $lines log lines..."
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker logs --tail "$lines" -f "$CONTAINER_NAME"
    else
        print_error "Container is not running"
        return 1
    fi
}

# Create database backup
create_backup() {
    print_status "Creating database backup..."
    
    if [ ! -f "$DATA_DIR/interviews.db" ]; then
        print_error "Database file not found"
        return 1
    fi
    
    # Create backup directory
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_path="$BACKUP_DIR/backup_$timestamp"
    mkdir -p "$backup_path"
    
    # Copy database
    cp "$DATA_DIR/interviews.db" "$backup_path/interviews.db"
    
    # Create metadata
    cat > "$backup_path/metadata.txt" << EOF
Backup Created: $(date)
Database Size: $(stat -f%z "$DATA_DIR/interviews.db" 2>/dev/null || stat -c%s "$DATA_DIR/interviews.db" 2>/dev/null || echo "Unknown")
Application Version: $(docker inspect --format='{{.Config.Image}}' "$CONTAINER_NAME" 2>/dev/null || echo "Unknown")
Container Status: $(docker inspect --format='{{.State.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "Unknown")
EOF
    
    # Compress backup
    tar -czf "$backup_path.tar.gz" -C "$BACKUP_DIR" "backup_$timestamp"
    rm -rf "$backup_path"
    
    print_success "Backup created: $backup_path.tar.gz"
}

# Clean old backups
clean_backups() {
    local keep_days="${1:-7}"
    
    print_status "Cleaning backups older than $keep_days days..."
    
    if [ ! -d "$BACKUP_DIR" ]; then
        print_warning "Backup directory does not exist"
        return 0
    fi
    
    # Find and remove old backups
    old_backups=$(find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +$keep_days 2>/dev/null)
    
    if [ -n "$old_backups" ]; then
        echo "$old_backups" | xargs rm -f
        count=$(echo "$old_backups" | wc -l)
        print_success "Removed $count old backup(s)"
    else
        print_status "No old backups to remove"
    fi
}

# Restart application
restart_app() {
    print_status "Restarting application..."
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        docker restart "$CONTAINER_NAME"
        
        # Wait for health check
        sleep 5
        if check_health; then
            print_success "Application restarted successfully"
        else
            print_error "Application restart failed health check"
            return 1
        fi
    else
        print_error "Container is not running"
        return 1
    fi
}

# Update application
update_app() {
    print_status "Updating application..."
    
    # Pull latest code (if in git repo)
    if [ -d ".git" ]; then
        git pull origin main
    fi
    
    # Rebuild and restart
    ./ops/deploy.sh
}

# Show help
show_help() {
    echo "Excel Interviewer Monitoring Script"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  status              Show application status and metrics"
    echo "  health              Check application health"
    echo "  logs [lines]        View application logs (default: 50 lines)"
    echo "  backup              Create database backup"
    echo "  clean [days]        Clean backups older than N days (default: 7)"
    echo "  restart             Restart the application"
    echo "  update              Update and restart the application"
    echo "  help                Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 status           # Show current status"
    echo "  $0 logs 100         # Show last 100 log lines"
    echo "  $0 clean 30         # Keep only backups from last 30 days"
}

# Main command handler
case "$1" in
    "status")
        get_status
        ;;
    "health")
        if check_health; then
            echo "✅ Application is healthy"
            exit 0
        else
            echo "❌ Application is unhealthy"
            exit 1
        fi
        ;;
    "logs")
        view_logs "$2"
        ;;
    "backup")
        create_backup
        ;;
    "clean")
        clean_backups "$2"
        ;;
    "restart")
        restart_app
        ;;
    "update")
        update_app
        ;;
    "help"|"--help"|"-h"|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac
