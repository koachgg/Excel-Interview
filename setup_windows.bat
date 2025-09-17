@echo off
echo 🚀 Setting up Excel Interviewer on Windows
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found, creating virtual environment...

REM Remove existing venv if it exists
if exist venv (
    echo 🗑️ Removing existing virtual environment...
    rmdir /s /q venv
)

REM Create new virtual environment
echo 📦 Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo 📈 Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo 📥 Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo ⚠️ requirements.txt not found, installing basic dependencies...
    pip install fastapi uvicorn sqlalchemy pydantic pytest httpx
)

REM Setup environment file
echo 🔧 Setting up environment configuration...
if not exist .env (
    if exist .env.example (
        copy .env.example .env
        echo ✅ Created .env from .env.example
    ) else (
        echo # Excel Interviewer Environment Configuration > .env
        echo DATABASE_URL=sqlite:///interviews.db >> .env
        echo ENVIRONMENT=development >> .env
        echo # Add your API keys below: >> .env
        echo # GOOGLE_API_KEY=your-gemini-key-here >> .env
        echo # GROQ_API_KEY=your-groq-key-here >> .env
        echo # ANTHROPIC_API_KEY=your-claude-key-here >> .env
        echo ✅ Created basic .env file
    )
)

echo.
echo 🎉 Setup complete! 
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your API keys
echo 2. To activate virtual environment: call venv\Scripts\activate.bat
echo 3. To run the backend: cd server && python main.py
echo 4. To run tests: python run_tests.py
echo.
echo 💡 Quick commands:
echo   - Activate venv: venv\Scripts\activate.bat
echo   - Deactivate venv: deactivate
echo   - Run backend: cd server ^&^& uvicorn main:app --reload
echo   - Run frontend: cd frontend ^&^& npm install ^&^& npm run dev
echo.
pause
