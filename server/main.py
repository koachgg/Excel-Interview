from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="../.env")

from storage.db import get_db, create_tables, InterviewRepository, Turn
from agents.interviewer import InterviewAgent
from summary.report import ReportGenerator
from api.resume_simple import router as resume_router
from api.timing import router as timing_router

# Initialize FastAPI app
app = FastAPI(title="Excel Interview System", version="1.0.0")

# Include routers
app.include_router(resume_router, prefix="/api", tags=["resume"])
app.include_router(timing_router, prefix="/api/timing", tags=["timing"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Pydantic models
class StartInterviewRequest(BaseModel):
    candidate_name: Optional[str] = None

class TurnRequest(BaseModel):
    interview_id: int
    answer: str

class InterviewResponse(BaseModel):
    id: int
    state: str
    question: Optional[str] = None
    target_skill: Optional[str] = None
    difficulty: Optional[int] = None
    ask_clarification_opt: Optional[str] = None
    next_action: str
    turn_number: int
    coverage_vector: Dict[str, Any]
    time_remaining: Optional[int] = None

class SummaryResponse(BaseModel):
    interview_id: int
    total_score: float
    scores_by_skill: Dict[str, float]
    strengths: List[str]
    gaps: List[str]
    recommendations: List[str]
    transcript_excerpts: List[Dict[str, str]]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

# Routes
@app.post("/interviews", response_model=InterviewResponse)
async def start_interview(request: StartInterviewRequest, db: Session = Depends(get_db)):
    """Start a new interview session"""
    try:
        repo = InterviewRepository(db)
        interview = repo.create_interview(candidate_name=request.candidate_name)
        
        # Initialize interview agent
        agent = InterviewAgent()
        response = agent.start_interview(interview.id)
        
        # Add the first turn (intro question)
        repo.add_turn(
            interview_id=interview.id,
            turn_number=1,
            question=response["question"],
            target_skill="introduction",
            difficulty=1
        )
        
        return InterviewResponse(
            id=interview.id,
            state=response["state"],
            question=response["question"],
            target_skill=response.get("target_skill"),
            difficulty=response.get("difficulty"),
            ask_clarification_opt=response.get("ask_clarification_opt"),
            next_action=response["next_action"],
            turn_number=1,
            coverage_vector=response.get("coverage_vector", {}),
            time_remaining=45 * 60  # 45 minutes in seconds
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/turn", response_model=InterviewResponse)
async def process_turn(request: TurnRequest, db: Session = Depends(get_db)):
    """Process a candidate's answer and generate next question"""
    try:
        repo = InterviewRepository(db)
        interview = repo.get_interview(request.interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Get the current turn to update with answer
        current_turn = db.query(Turn).filter(
            Turn.interview_id == request.interview_id
        ).order_by(Turn.turn_number.desc()).first()
        
        if current_turn:
            repo.update_turn(current_turn.id, answer=request.answer)
        
        # Generate next question using interview agent
        agent = InterviewAgent()
        response = agent.process_turn(
            interview_id=request.interview_id,
            answer=request.answer,
            current_state=interview.state,
            db=db
        )
        
        # Update interview state
        repo.update_interview(
            request.interview_id,
            state=response["state"],
            coverage_vector=response.get("coverage_vector", {})
        )
        
        # Add next turn if not finished
        turn_number = current_turn.turn_number + 1 if current_turn else 1
        if response["next_action"] != "END_INTERVIEW":
            repo.add_turn(
                interview_id=request.interview_id,
                turn_number=turn_number,
                question=response["question"],
                target_skill=response.get("target_skill", "unknown"),
                difficulty=response.get("difficulty", 1)
            )
        
        return InterviewResponse(
            id=request.interview_id,
            state=response["state"],
            question=response.get("question"),
            target_skill=response.get("target_skill"),
            difficulty=response.get("difficulty"),
            ask_clarification_opt=response.get("ask_clarification_opt"),
            next_action=response["next_action"],
            turn_number=turn_number,
            coverage_vector=response.get("coverage_vector", {}),
            time_remaining=response.get("time_remaining")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/summary/{interview_id}", response_model=SummaryResponse)
async def get_interview_summary(interview_id: int, db: Session = Depends(get_db)):
    """Generate and return interview summary report"""
    try:
        repo = InterviewRepository(db)
        interview = repo.get_interview(interview_id)
        
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found")
        
        # Generate report
        report_generator = ReportGenerator(db)
        summary = report_generator.generate_report(interview_id)
        
        return SummaryResponse(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/stream/{interview_id}")
async def websocket_endpoint(websocket: WebSocket, interview_id: int):
    """WebSocket endpoint for real-time interview streaming"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "answer":
                # Process answer and get next question
                # This would integrate with the turn processing logic
                response = {"type": "question", "content": "Next question..."}
                await manager.send_personal_message(json.dumps(response), websocket)
            elif message["type"] == "ping":
                await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
