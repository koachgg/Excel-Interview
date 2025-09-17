# Windows Setup Guide for Excel Interviewer

## Quick Fix for Your Current Issue

You're getting an error because `sqlite3` doesn't need to be installed via pip (it's built into Python). Here's how to proceed:

### Option 1: Continue with Your Current Setup

Since you already have the virtual environment activated (you can see `(venv)` in your prompt), run these commands one by one:

```cmd
# Install core packages first
pip install fastapi uvicorn websockets python-multipart sqlalchemy

# Install data handling packages
pip install pandas pydantic requests

# Install testing packages
pip install pytest pytest-asyncio

# Install LLM packages (optional for now)
pip install httpx
```

If you get errors with specific versions, try without version constraints.

### Option 2: Use the Simplified Requirements

I've created `requirements-simple.txt` with more flexible versions:

```cmd
pip install -r requirements-simple.txt
```

### Option 3: Use the Windows Setup Script

Run the automated setup script:

```cmd
setup_windows.bat
```

## After Dependencies are Installed

1. **Set up environment variables:**
   ```cmd
   copy .env.example .env
   ```
   Then edit `.env` with your API keys (you can use Notepad):
   ```
   GOOGLE_API_KEY=your-actual-key-here
   GROQ_API_KEY=your-actual-key-here  
   ANTHROPIC_API_KEY=your-actual-key-here
   ```

2. **Test the backend:**
   ```cmd
   cd server
   python -m uvicorn main:app --reload
   ```
   This should start the server at http://localhost:8000

3. **Test the frontend (in a new terminal):**
   ```cmd
   cd frontend
   npm install
   npm run dev
   ```
   This should start the frontend at http://localhost:3000

## Troubleshooting Tips

- **If pip is slow:** Try adding `--no-cache-dir` flag
- **If versions conflict:** Remove version numbers from requirements
- **If import errors:** Make sure you're in the activated virtual environment
- **If port conflicts:** Change ports in the startup commands

## Quick Test

Once packages are installed, test if the basic structure works:

```cmd
python check_structure.py
```

This will validate that all components are properly set up.

Let me know if you encounter any specific errors and I can help troubleshoot!
