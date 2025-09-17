#!/bin/bash
# Setup script for Excel Interviewer development environment
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[SETUP]${NC} $1"
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

# Check system requirements
check_requirements() {
    print_step "Checking system requirements..."
    
    # Check Python
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        print_success "Python $python_version found"
    else
        print_error "Python 3.11+ is required but not found"
        exit 1
    fi
    
    # Check Node.js
    if command -v node &> /dev/null; then
        node_version=$(node --version)
        print_success "Node.js $node_version found"
    else
        print_error "Node.js 18+ is required but not found"
        exit 1
    fi
    
    # Check Docker (optional)
    if command -v docker &> /dev/null; then
        docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
        print_success "Docker $docker_version found"
    else
        print_warning "Docker not found (optional for deployment)"
    fi
    
    # Check npm
    if command -v npm &> /dev/null; then
        npm_version=$(npm --version)
        print_success "npm $npm_version found"
    else
        print_error "npm is required but not found"
        exit 1
    fi
}

# Setup environment file
setup_environment() {
    print_step "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Created .env file from template"
        
        echo ""
        print_warning "IMPORTANT: Please edit .env file and add your API keys:"
        echo "  - GEMINI_API_KEY: Get from https://makersuite.google.com/app/apikey"
        echo "  - GROQ_API_KEY: Get from https://console.groq.com/keys"
        echo "  - ANTHROPIC_API_KEY: Get from https://console.anthropic.com/"
        echo ""
        
        read -p "Press Enter to continue after updating API keys..."
    else
        print_success ".env file already exists"
    fi
}

# Install Python dependencies
install_python_deps() {
    print_step "Installing Python dependencies..."
    
    cd server
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Created Python virtual environment"
    fi
    
    # Activate virtual environment
    source venv/bin/activate || source venv/Scripts/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
    cd ..
}

# Install Node.js dependencies
install_node_deps() {
    print_step "Installing Node.js dependencies..."
    
    cd frontend
    npm install
    print_success "Node.js dependencies installed"
    cd ..
}

# Setup database
setup_database() {
    print_step "Setting up database..."
    
    # Create data directory
    mkdir -p data
    mkdir -p logs
    mkdir -p backups
    
    cd server
    source venv/bin/activate || source venv/Scripts/activate
    
    # Run database migrations
    python -c "from storage.db import create_tables; create_tables()"
    
    # Seed database with sample data
    if [ "$1" == "--with-seed" ]; then
        python ../scripts/seed_comprehensive.py --force
        print_success "Database seeded with sample data"
    fi
    
    print_success "Database setup completed"
    cd ..
}

# Create useful scripts
create_scripts() {
    print_step "Creating utility scripts..."
    
    # Development start script
    cat > start-dev.sh << 'EOF'
#!/bin/bash
echo "Starting Excel Interviewer development environment..."

# Start backend
echo "Starting backend server..."
cd server
source venv/bin/activate || source venv/Scripts/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "🚀 Development servers started!"
echo "📊 Backend API: http://localhost:8000"
echo "🎨 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    
    chmod +x start-dev.sh
    
    # Test script
    cat > run-tests.sh << 'EOF'
#!/bin/bash
echo "Running all tests..."

# Backend tests
echo "Running backend tests..."
cd server
source venv/bin/activate || source venv/Scripts/activate
pytest tests/ -v
cd ..

# Frontend tests
echo "Running frontend tests..."
cd frontend
npm run test
npm run type-check
npm run lint
cd ..

echo "✅ All tests completed"
EOF
    
    chmod +x run-tests.sh
    
    print_success "Utility scripts created"
}

# Verify installation
verify_installation() {
    print_step "Verifying installation..."
    
    # Test backend
    cd server
    source venv/bin/activate || source venv/Scripts/activate
    python -c "import fastapi, sqlalchemy; print('Backend dependencies OK')"
    cd ..
    
    # Test frontend
    cd frontend
    if npm run build > /dev/null 2>&1; then
        print_success "Frontend build test passed"
    else
        print_error "Frontend build test failed"
        return 1
    fi
    cd ..
    
    print_success "Installation verified successfully"
}

# Print final instructions
print_instructions() {
    echo ""
    echo "🎉 Setup completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your API keys (if not done already)"
    echo "2. Run './start-dev.sh' to start development servers"
    echo "3. Open http://localhost:5173 in your browser"
    echo ""
    echo "Available commands:"
    echo "  ./start-dev.sh     - Start development environment"
    echo "  ./run-tests.sh     - Run all tests"
    echo "  ./ops/deploy.sh    - Deploy with Docker"
    echo "  ./ops/monitor.sh   - Monitor running application"
    echo ""
    echo "Documentation:"
    echo "  README.md          - Project overview and quick start"
    echo "  docs/design.md     - Detailed system design"
    echo "  API docs           - http://localhost:8000/docs (when running)"
    echo ""
}

# Main setup flow
main() {
    echo "🚀 Excel Interviewer Setup Script"
    echo "================================="
    echo ""
    
    check_requirements
    setup_environment
    install_python_deps
    install_node_deps
    setup_database "$@"
    create_scripts
    verify_installation
    print_instructions
}

# Handle command line arguments
case "$1" in
    "--help"|"-h")
        echo "Excel Interviewer Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --with-seed    Seed database with sample data"
        echo "  --help         Show this help message"
        echo ""
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
