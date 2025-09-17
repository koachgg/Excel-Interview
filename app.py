"""
Hugging Face Spaces deployment entry point for Excel Interviewer
"""
import os
import sys
import gradio as gr
import uvicorn
from pathlib import Path
import threading
import time

# Add server directory to Python path
server_dir = Path(__file__).parent / "server"
sys.path.insert(0, str(server_dir))

# Import the FastAPI app
from main import app as fastapi_app

def start_fastapi():
    """Start FastAPI server in background"""
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

def create_gradio_interface():
    """Create Gradio interface for HF Spaces"""
    
    with gr.Blocks(
        title="Excel Interview AI",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        """
    ) as interface:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h1>🎯 Excel Interview AI System</h1>
            <p style="font-size: 18px; color: #666;">
                AI-powered technical interview system with resume analysis and anti-cheating features
            </p>
        </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.HTML("""
                <div style="padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           border-radius: 10px; color: white; margin: 10px;">
                    <h3>🚀 Quick Start</h3>
                    <ol style="text-align: left;">
                        <li><strong>Upload Resume:</strong> PDF resume for AI analysis</li>
                        <li><strong>Start Interview:</strong> Begin structured Excel interview</li>
                        <li><strong>Answer Questions:</strong> 8+ adaptive questions based on your skills</li>
                        <li><strong>Get Report:</strong> Comprehensive performance analysis</li>
                    </ol>
                </div>
                """)
                
            with gr.Column(scale=1):
                gr.HTML("""
                <div style="padding: 20px; background: #f8f9ff; border-radius: 10px; margin: 10px;">
                    <h3>✨ Features</h3>
                    <ul style="text-align: left;">
                        <li>🤖 AI Resume Analysis</li>
                        <li>📝 Adaptive Questioning</li>
                        <li>⏱️ Anti-Cheating Timing</li>
                        <li>🎯 Hybrid Grading</li>
                        <li>📊 Performance Reports</li>
                    </ul>
                </div>
                """)
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px;">
            <h3>🎯 Access the Full Interview System</h3>
            <p style="font-size: 16px;">
                The complete interview interface is running on the FastAPI backend.
                Click below to access the full system:
            </p>
            <a href="/static/index.html" target="_blank" 
               style="display: inline-block; padding: 15px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                      color: white; text-decoration: none; border-radius: 8px; font-weight: bold; font-size: 16px;">
                🚀 Launch Excel Interview System
            </a>
        </div>
        """)
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #666;">
            <p>Built with FastAPI + React + Gemini AI | 
               <a href="/docs" target="_blank">API Documentation</a>
            </p>
        </div>
        """)
    
    return interface

if __name__ == "__main__":
    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Give FastAPI time to start
    time.sleep(3)
    
    # Create and launch Gradio interface
    interface = create_gradio_interface()
    interface.launch(
        server_port=7860,
        server_name="0.0.0.0",
        show_api=False
    )
