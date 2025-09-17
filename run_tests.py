"""
Test runner for Excel Interviewer system
Runs all tests: backend, frontend unit tests, and E2E tests
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def run_command(command, cwd=None, description=""):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description or command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        print("✅ SUCCESS")
        if result.stdout:
            print("STDOUT:", result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ FAILED: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False

def check_prerequisites():
    """Check if all required tools are installed"""
    print("Checking prerequisites...")
    
    prerequisites = [
        ("python", "python --version"),
        ("node", "node --version"),
        ("npm", "npm --version"),
        ("pip", "pip --version")
    ]
    
    missing = []
    for name, command in prerequisites:
        if not run_command(command, description=f"Checking {name}"):
            missing.append(name)
    
    if missing:
        print(f"\n❌ Missing prerequisites: {', '.join(missing)}")
        return False
    
    print("\n✅ All prerequisites found")
    return True

def setup_python_environment():
    """Setup Python testing environment"""
    print("\nSetting up Python environment...")
    
    server_dir = Path(__file__).parent / "server"
    
    # Install Python dependencies
    if not run_command(
        "pip install -r requirements.txt",
        cwd=server_dir,
        description="Installing Python dependencies"
    ):
        return False
    
    # Install test dependencies
    if not run_command(
        "pip install pytest pytest-asyncio pytest-mock httpx",
        cwd=server_dir,
        description="Installing test dependencies"
    ):
        return False
    
    return True

def run_backend_tests():
    """Run backend Python tests"""
    print("\nRunning backend tests...")
    
    server_dir = Path(__file__).parent / "server"
    
    # Run pytest with coverage
    return run_command(
        "python -m pytest tests/ -v --tb=short",
        cwd=server_dir,
        description="Running backend tests"
    )

def setup_frontend_environment():
    """Setup frontend testing environment"""
    print("\nSetting up frontend environment...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Install frontend dependencies
    if not run_command(
        "npm install",
        cwd=frontend_dir,
        description="Installing frontend dependencies"
    ):
        return False
    
    # Install Playwright for E2E tests (if package-e2e.json exists)
    e2e_package = frontend_dir / "package-e2e.json"
    if e2e_package.exists():
        if not run_command(
            "npm install @playwright/test @types/node --save-dev",
            cwd=frontend_dir,
            description="Installing E2E test dependencies"
        ):
            return False
        
        # Install Playwright browsers
        if not run_command(
            "npx playwright install",
            cwd=frontend_dir,
            description="Installing Playwright browsers"
        ):
            return False
    
    return True

def run_frontend_unit_tests():
    """Run frontend unit tests"""
    print("\nRunning frontend unit tests...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if test script exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("⚠️ No package.json found, skipping frontend unit tests")
        return True
    
    # Run tests
    return run_command(
        "npm test",
        cwd=frontend_dir,
        description="Running frontend unit tests"
    )

def start_development_servers():
    """Start development servers for E2E testing"""
    print("\nStarting development servers...")
    
    # Start backend server in background
    server_dir = Path(__file__).parent / "server"
    backend_process = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=server_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Start frontend server in background
    frontend_dir = Path(__file__).parent / "frontend"
    frontend_process = subprocess.Popen(
        ["npm", "run", "dev"],
        cwd=frontend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    # Wait for servers to start
    print("Waiting for servers to start...")
    time.sleep(10)
    
    return backend_process, frontend_process

def run_e2e_tests():
    """Run end-to-end tests"""
    print("\nRunning E2E tests...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    # Check if Playwright config exists
    playwright_config = frontend_dir / "playwright.config.ts"
    if not playwright_config.exists():
        print("⚠️ No Playwright config found, skipping E2E tests")
        return True
    
    # Start servers
    try:
        backend_proc, frontend_proc = start_development_servers()
        
        # Run Playwright tests
        success = run_command(
            "npx playwright test",
            cwd=frontend_dir,
            description="Running E2E tests"
        )
        
        return success
        
    except Exception as e:
        print(f"❌ Failed to start servers: {e}")
        return False
    
    finally:
        # Clean up processes
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
        except:
            pass

def run_integration_tests():
    """Run integration tests between frontend and backend"""
    print("\nRunning integration tests...")
    
    # This could include API contract tests, data flow tests, etc.
    # For now, we'll use a simple health check
    
    try:
        backend_proc, frontend_proc = start_development_servers()
        
        # Test backend health
        import requests
        backend_health = requests.get("http://localhost:8000/health", timeout=5)
        if backend_health.status_code != 200:
            print("❌ Backend health check failed")
            return False
        
        # Test frontend accessibility
        frontend_health = requests.get("http://localhost:3000", timeout=5)
        if frontend_health.status_code != 200:
            print("❌ Frontend health check failed")
            return False
        
        print("✅ Integration health checks passed")
        return True
        
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False
    
    finally:
        try:
            backend_proc.terminate()
            frontend_proc.terminate()
        except:
            pass

def main():
    """Main test runner"""
    print("🧪 Excel Interviewer Test Suite")
    print("="*60)
    
    start_time = time.time()
    results = {}
    
    # Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed")
        sys.exit(1)
    
    # Setup environments
    print("\n🔧 Setting up test environments...")
    results['python_setup'] = setup_python_environment()
    results['frontend_setup'] = setup_frontend_environment()
    
    # Run tests
    print("\n🧪 Running tests...")
    results['backend_tests'] = run_backend_tests()
    results['frontend_tests'] = run_frontend_unit_tests()
    results['e2e_tests'] = run_e2e_tests()
    results['integration_tests'] = run_integration_tests()
    
    # Print results
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"\n{'='*60}")
    print("🏁 TEST RESULTS")
    print(f"{'='*60}")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 Summary: {passed}/{total} test suites passed")
    print(f"⏱️ Total time: {duration:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} test suite(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
