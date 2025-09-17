"""
Hugging Face Spaces deployment entry point for Excel Interviewer
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Import the FastAPI app
from main import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))  # HF Spaces uses port 7860
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
