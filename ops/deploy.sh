#!/bin/bash
# Deployment script for production environments
set -e

echo "🚀 Starting Excel Interviewer deployment..."

# Configuration
APP_NAME="excel-interviewer"
DOCKER_IMAGE="$APP_NAME:latest"
CONTAINER_NAME="$APP_NAME-container"
PORT=${PORT:-8000}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    echo "✓ Prerequisites check passed"
}

# Backup current deployment
backup_current() {
    print_step "Creating backup of current deployment..."
    
    if [ -d "./data" ]; then
        BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        cp -r ./data "$BACKUP_DIR/"
        echo "✓ Backup created at $BACKUP_DIR"
    else
        echo "ℹ️ No existing data to backup"
    fi
}

# Build Docker image
build_image() {
    print_step "Building Docker image..."
    
    docker build -t "$DOCKER_IMAGE" .
    
    if [ $? -eq 0 ]; then
        echo "✓ Docker image built successfully"
    else
        print_error "Failed to build Docker image"
        exit 1
    fi
}

# Stop existing container
stop_existing() {
    print_step "Stopping existing container..."
    
    if [ $(docker ps -q -f name=$CONTAINER_NAME) ]; then
        docker stop "$CONTAINER_NAME"
        docker rm "$CONTAINER_NAME"
        echo "✓ Existing container stopped and removed"
    else
        echo "ℹ️ No existing container to stop"
    fi
}

# Start new container
start_container() {
    print_step "Starting new container..."
    
    docker run -d \
        --name "$CONTAINER_NAME" \
        -p "$PORT:8000" \
        -v "$(pwd)/data:/app/data" \
        --env-file .env \
        --restart unless-stopped \
        "$DOCKER_IMAGE"
    
    if [ $? -eq 0 ]; then
        echo "✓ Container started successfully"
    else
        print_error "Failed to start container"
        exit 1
    fi
}

# Health check
health_check() {
    print_step "Running health check..."
    
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f "http://localhost:$PORT/health" > /dev/null 2>&1; then
            echo "✅ Application is healthy and responding"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Waiting for application to be ready..."
        sleep 2
        ((attempt++))
    done
    
    print_error "Application failed health check after $max_attempts attempts"
    return 1
}

# Database migration
migrate_database() {
    print_step "Running database migrations..."
    
    docker exec "$CONTAINER_NAME" python scripts/migrate_database.py
    
    if [ $? -eq 0 ]; then
        echo "✓ Database migrations completed"
    else
        print_warning "Database migrations failed or not needed"
    fi
}

# Seed database (optional)
seed_database() {
    if [ "$1" == "--seed" ]; then
        print_step "Seeding database with sample data..."
        
        docker exec "$CONTAINER_NAME" python scripts/seed_comprehensive.py --force
        
        if [ $? -eq 0 ]; then
            echo "✓ Database seeded successfully"
        else
            print_warning "Database seeding failed"
        fi
    fi
}

# Cleanup old images
cleanup() {
    print_step "Cleaning up old Docker images..."
    
    # Remove dangling images
    docker image prune -f
    
    echo "✓ Cleanup completed"
}

# Main deployment flow
main() {
    echo "🎯 Deploying Excel Interviewer v$(date +%Y%m%d-%H%M%S)"
    
    check_prerequisites
    backup_current
    build_image
    stop_existing
    start_container
    
    if health_check; then
        migrate_database
        seed_database "$@"
        cleanup
        
        echo ""
        echo "🎉 Deployment completed successfully!"
        echo "📊 Application is running at: http://localhost:$PORT"
        echo "🏥 Health check: http://localhost:$PORT/health"
        echo "📚 API docs: http://localhost:$PORT/docs"
        echo ""
        echo "📝 Useful commands:"
        echo "  View logs: docker logs $CONTAINER_NAME"
        echo "  Stop app: docker stop $CONTAINER_NAME"
        echo "  Restart app: docker restart $CONTAINER_NAME"
    else
        print_error "Deployment failed - application is not healthy"
        exit 1
    fi
}

# Handle script arguments
case "$1" in
    --help|-h)
        echo "Excel Interviewer Deployment Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --seed    Seed database with sample data after deployment"
        echo "  --help    Show this help message"
        echo ""
        echo "Environment Variables:"
        echo "  PORT      Application port (default: 8000)"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
