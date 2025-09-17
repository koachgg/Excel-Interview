"""
Timing analytics API endpoints.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from services.timing_service import timing_service

router = APIRouter()

class StartTimingRequest(BaseModel):
    interview_id: int
    question_id: str
    question_text: str

class KeystrokeEvent(BaseModel):
    timing_key: str
    keystroke_type: str  # 'character', 'backspace', 'delete'
    char: Optional[str] = None
    timestamp: Optional[datetime] = None

class PasteEvent(BaseModel):
    timing_key: str
    content_length: int
    timestamp: Optional[datetime] = None

class FocusEvent(BaseModel):
    timing_key: str
    event_type: str  # 'focus' or 'blur'
    timestamp: Optional[datetime] = None

class FinishTimingRequest(BaseModel):
    timing_key: str
    final_answer: str
    timestamp: Optional[datetime] = None

@router.post("/start-timing")
async def start_timing(request: StartTimingRequest) -> Dict[str, str]:
    """Start timing for a new question."""
    try:
        timing_key = timing_service.start_question_timing(
            request.interview_id,
            request.question_id,
            request.question_text
        )
        return {"timing_key": timing_key, "status": "started"}
    except Exception as e:
        logging.error(f"Error starting timing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-keystroke")
async def record_keystroke(event: KeystrokeEvent) -> Dict[str, str]:
    """Record keystroke events for timing analysis."""
    try:
        timing_service.record_keystroke(
            event.timing_key,
            event.keystroke_type,
            event.char,
            event.timestamp
        )
        return {"status": "recorded"}
    except Exception as e:
        logging.error(f"Error recording keystroke: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-paste")
async def record_paste(event: PasteEvent) -> Dict[str, str]:
    """Record paste events for authenticity analysis."""
    try:
        timing_service.record_paste_event(
            event.timing_key,
            event.content_length,
            event.timestamp
        )
        warning_msg = "Large paste detected" if event.content_length > 100 else ""
        return {"status": "recorded", "warning": warning_msg}
    except Exception as e:
        logging.error(f"Error recording paste: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/record-focus")
async def record_focus(event: FocusEvent) -> Dict[str, str]:
    """Record focus/blur events for tab switching detection."""
    try:
        timing_service.record_focus_event(
            event.timing_key,
            event.event_type,
            event.timestamp
        )
        return {"status": "recorded"}
    except Exception as e:
        logging.error(f"Error recording focus event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/finish-timing")
async def finish_timing(request: FinishTimingRequest) -> Dict[str, Any]:
    """Complete timing analysis for a response."""
    try:
        completed_timing = timing_service.finish_response_timing(
            request.timing_key,
            request.final_answer,
            request.timestamp
        )
        
        if not completed_timing:
            raise HTTPException(status_code=404, detail="Timing session not found")
        
        return {
            "status": "completed",
            "analysis": {
                "time_to_first_keystroke": completed_timing.time_to_first_keystroke,
                "total_response_time": completed_timing.total_response_time,
                "typing_speed": completed_timing.typing_speed,
                "paste_count": completed_timing.paste_count,
                "focus_loss_count": completed_timing.focus_loss_count,
                "authenticity_score": completed_timing.authenticity_score,
                "red_flags": []
            }
        }
    except Exception as e:
        logging.error(f"Error finishing timing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/timing-analytics/{interview_id}")
async def get_timing_analytics(interview_id: int) -> Dict[str, Any]:
    """Get comprehensive timing analytics for an interview."""
    # Note: In a full implementation, we'd retrieve stored timing data
    # For now, return placeholder analytics
    return {
        "interview_id": interview_id,
        "message": "Timing analytics would show comprehensive analysis here",
        "features": [
            "Response time patterns",
            "Authenticity scoring",
            "Copy-paste detection",
            "Tab switching analysis",
            "Typing speed analysis",
            "Behavioral red flags"
        ]
    }
