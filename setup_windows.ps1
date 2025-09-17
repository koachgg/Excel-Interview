# Excel Interviewer Windows Setup Script (PowerShell)
Write-Host "🚀 Setting up Excel Interviewer on Windows" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python from https://python.org" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Remove existing venv if it exists
if (Test-Path "venv") {
    Write-Host "🗑️ Removing existing virtual environment..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "venv"
}

# Create new virtual environment
Write-Host "📦 Creating new virtual environment..." -ForegroundColor Cyan
try {
    python -m venv venv
    Write-Host "✅ Virtual environment created successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment and install dependencies
Write-Host "🔌 Activating virtual environment and installing dependencies..." -ForegroundColor Cyan

$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    # Execute in new PowerShell session to handle activation properly
    $installScript = @"
        & '.\venv\Scripts\Activate.ps1'
        Write-Host '📈 Upgrading pip...' -ForegroundColor Cyan
        python -m pip install --upgrade pip
        
        Write-Host '📥 Installing Python dependencies...' -ForegroundColor Cyan
        if (Test-Path 'requirements.txt') {
            pip install -r requirements.txt
            if (`$LASTEXITCODE -eq 0) {
                Write-Host '✅ Dependencies installed successfully' -ForegroundColor Green
            } else {
                Write-Host '❌ Failed to install some dependencies' -ForegroundColor Red
            }
        } else {
            Write-Host '⚠️ requirements.txt not found, installing basic dependencies...' -ForegroundColor Yellow
            pip install fastapi uvicorn sqlalchemy pydantic pytest httpx
        }
"@
    
    try {
        Invoke-Expression $installScript
    } catch {
        Write-Host "⚠️ Some packages may have failed to install. You can install them manually later." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Could not find activation script at $activateScript" -ForegroundColor Red
}

# Setup environment file
Write-Host "🔧 Setting up environment configuration..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ Created .env from .env.example" -ForegroundColor Green
    } else {
        $envContent = @"
# Excel Interviewer Environment Configuration
DATABASE_URL=sqlite:///interviews.db
ENVIRONMENT=development

# Add your API keys below:
# GOOGLE_API_KEY=your-gemini-key-here
# GROQ_API_KEY=your-groq-key-here
# ANTHROPIC_API_KEY=your-claude-key-here
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ Created basic .env file" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🎉 Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your API keys" -ForegroundColor White
Write-Host "2. To activate virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "3. To run the backend: cd server && python main.py" -ForegroundColor White
Write-Host "4. To run tests: python run_tests.py" -ForegroundColor White
Write-Host ""
Write-Host "💡 Quick commands:" -ForegroundColor Cyan
Write-Host "  - Activate venv: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  - Deactivate venv: deactivate" -ForegroundColor White
Write-Host "  - Run backend: cd server && uvicorn main:app --reload" -ForegroundColor White
Write-Host "  - Run frontend: cd frontend && npm install && npm run dev" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to continue"
