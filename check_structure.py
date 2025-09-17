"""
Simple validation script for Excel Interviewer system
Validates basic structure and file existence
"""
import os
import json
from pathlib import Path

def check_file_exists(file_path, description=""):
    """Check if a file exists and report status"""
    if file_path.exists():
        print(f"  ✅ {description or file_path.name}")
        return True
    else:
        print(f"  ❌ Missing: {description or file_path.name}")
        return False

def validate_backend_structure():
    """Validate backend file structure"""
    print("🔍 Validating backend structure...")
    
    server_dir = Path(__file__).parent / "server"
    
    required_files = [
        (server_dir / "main.py", "FastAPI main application"),
        (server_dir / "__init__.py", "Server package init"),
        (server_dir / "agents" / "__init__.py", "Agents package"),
        (server_dir / "graders" / "__init__.py", "Graders package"),
        (server_dir / "llm" / "__init__.py", "LLM package"),
        (server_dir / "storage" / "__init__.py", "Storage package"),
        (server_dir / "summary" / "__init__.py", "Summary package"),
        (server_dir / "tests" / "conftest.py", "Test configuration"),
    ]
    
    results = []
    for file_path, description in required_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def validate_frontend_structure():
    """Validate frontend file structure"""
    print("🔍 Validating frontend structure...")
    
    frontend_dir = Path(__file__).parent / "frontend"
    
    required_files = [
        (frontend_dir / "package.json", "Frontend package configuration"),
        (frontend_dir / "tsconfig.json", "TypeScript configuration"),
        (frontend_dir / "vite.config.ts", "Vite build configuration"),
        (frontend_dir / "index.html", "HTML entry point"),
        (frontend_dir / "src" / "main.tsx", "React main entry"),
        (frontend_dir / "src" / "App.tsx", "Main React component"),
        (frontend_dir / "playwright.config.ts", "E2E test configuration"),
        (frontend_dir / "tests" / "interview.spec.ts", "E2E tests"),
    ]
    
    results = []
    for file_path, description in required_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def validate_documentation():
    """Validate documentation files"""
    print("🔍 Validating documentation...")
    
    docs_dir = Path(__file__).parent / "docs"
    
    required_docs = [
        (docs_dir / "design.md", "Technical design document"),
        (docs_dir / "testing.md", "Testing strategy documentation"),
        (Path(__file__).parent / "README.md", "Main project README"),
    ]
    
    results = []
    for doc_path, description in required_docs:
        results.append(check_file_exists(doc_path, description))
    
    return all(results)

def validate_deployment_config():
    """Validate deployment configuration"""
    print("🔍 Validating deployment configuration...")
    
    root_dir = Path(__file__).parent
    
    deployment_files = [
        (root_dir / "Dockerfile", "Docker container configuration"),
        (root_dir / "docker-compose.yml", "Docker Compose orchestration"),
        (root_dir / "render.yaml", "Render cloud deployment"),
        (root_dir / ".github" / "workflows" / "ci-cd.yml", "GitHub Actions CI/CD"),
        (root_dir / "requirements.txt", "Python dependencies"),
        (root_dir / ".env.example", "Environment variables template"),
    ]
    
    results = []
    for file_path, description in deployment_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def validate_sample_data():
    """Validate sample transcripts and data"""
    print("🔍 Validating sample data...")
    
    samples_dir = Path(__file__).parent / "samples"
    
    sample_files = [
        (samples_dir / "transcript_novice.md", "Novice interview transcript"),
        (samples_dir / "transcript_intermediate.md", "Intermediate interview transcript"),
        (samples_dir / "transcript_advanced.md", "Advanced interview transcript"),
    ]
    
    results = []
    for file_path, description in sample_files:
        if check_file_exists(file_path, description):
            # Check if file has meaningful content
            try:
                content = file_path.read_text()
                if len(content) > 1000:  # Should be substantial
                    print(f"    📊 {description} has {len(content)} characters")
                    results.append(True)
                else:
                    print(f"    ⚠️ {description} seems incomplete ({len(content)} chars)")
                    results.append(False)
            except Exception as e:
                print(f"    ❌ Error reading {description}: {e}")
                results.append(False)
        else:
            results.append(False)
    
    return all(results)

def validate_operational_tools():
    """Validate operational scripts and tools"""
    print("🔍 Validating operational tools...")
    
    root_dir = Path(__file__).parent
    
    ops_files = [
        (root_dir / "run_tests.py", "Comprehensive test runner"),
        (root_dir / "validate_system.py", "System validation script"),
        (root_dir / "scripts" / "seed_comprehensive.py", "Database seeding script"),
        (root_dir / "ops" / "deploy.sh", "Deployment script"),
        (root_dir / "ops" / "monitor.sh", "Monitoring script"),
    ]
    
    results = []
    for file_path, description in ops_files:
        results.append(check_file_exists(file_path, description))
    
    return all(results)

def validate_package_configurations():
    """Validate package configuration files"""
    print("🔍 Validating package configurations...")
    
    root_dir = Path(__file__).parent
    
    # Check Python requirements
    requirements_file = root_dir / "requirements.txt"
    if requirements_file.exists():
        content = requirements_file.read_text()
        required_packages = ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
        missing_packages = []
        
        for package in required_packages:
            if package not in content.lower():
                missing_packages.append(package)
        
        if missing_packages:
            print(f"    ⚠️ Missing Python packages: {', '.join(missing_packages)}")
        else:
            print("    ✅ All required Python packages listed")
    
    # Check frontend package.json
    frontend_package = root_dir / "frontend" / "package.json"
    if frontend_package.exists():
        try:
            package_data = json.loads(frontend_package.read_text())
            required_deps = ["react", "typescript", "vite"]
            missing_deps = []
            
            all_deps = {**package_data.get("dependencies", {}), **package_data.get("devDependencies", {})}
            
            for dep in required_deps:
                if dep not in all_deps:
                    missing_deps.append(dep)
            
            if missing_deps:
                print(f"    ⚠️ Missing frontend dependencies: {', '.join(missing_deps)}")
            else:
                print("    ✅ All required frontend dependencies listed")
        except Exception as e:
            print(f"    ❌ Error reading frontend package.json: {e}")
    
    return True

def main():
    """Run all validations"""
    print("🚀 Excel Interviewer System Structure Validation")
    print("="*60)
    
    validations = [
        ("Backend Structure", validate_backend_structure),
        ("Frontend Structure", validate_frontend_structure),
        ("Documentation", validate_documentation),
        ("Deployment Configuration", validate_deployment_config),
        ("Sample Data", validate_sample_data),
        ("Operational Tools", validate_operational_tools),
        ("Package Configurations", validate_package_configurations),
    ]
    
    results = {}
    
    for validation_name, validation_func in validations:
        print(f"\n{validation_name}:")
        try:
            results[validation_name] = validation_func()
        except Exception as e:
            print(f"  ❌ {validation_name} validation failed: {e}")
            results[validation_name] = False
    
    # Print summary
    print(f"\n{'='*60}")
    print("🏁 VALIDATION RESULTS")
    print(f"{'='*60}")
    
    for validation_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{validation_name:<25}: {status}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 Summary: {passed}/{total} structure validations passed")
    
    if passed == total:
        print("\n🎉 System structure is complete and ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment: cp .env.example .env")
        print("3. Run tests: python run_tests.py")
        print("4. Start development: docker-compose up")
        return True
    else:
        print(f"\n💥 {total - passed} validation(s) failed")
        print("Please review the missing files and components above.")
        return False

if __name__ == "__main__":
    main()
