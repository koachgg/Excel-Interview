"""
Simple test version of main.py to check basic FastAPI setup
"""
from fastapi import FastAPI

# Initialize FastAPI app
app = FastAPI(title="Excel Interview System", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Excel Interview System is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "System is operational"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
