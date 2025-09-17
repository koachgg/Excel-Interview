"""
Resume upload and analysis endpoints.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging

# Import with fallback for missing dependencies
try:
    from services.resume_parser import ResumeParser, PersonalizedQuestionGenerator
    RESUME_PARSING_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Resume parsing not available: {e}")
    RESUME_PARSING_AVAILABLE = False

router = APIRouter()

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Upload and analyze resume for personalized interview questions."""
    
    if not RESUME_PARSING_AVAILABLE:
        return JSONResponse(
            status_code=501,
            content={
                "error": "Resume parsing not available",
                "message": "Install required packages: pip install PyPDF2 python-docx",
                "fallback": True
            }
        )
    
    # Validate file type
    allowed_types = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"File type {file.content_type} not supported. Use PDF, DOCX, or TXT files."
        )
    
    # Validate file size (max 5MB)
    file_content = await file.read()
    if len(file_content) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 5MB.")
    
    try:
        # Parse resume
        parser = ResumeParser()
        analysis = parser.parse_resume(file_content, file.filename or "resume")
        
        if 'error' in analysis:
            return JSONResponse(
                status_code=422,
                content={"error": analysis['error']}
            )
        
        # Generate personalized questions
        question_generator = PersonalizedQuestionGenerator()
        personalized_questions = question_generator.generate_personalized_questions(analysis)
        
        return {
            "status": "success",
            "filename": file.filename,
            "analysis": {
                "experience_level": analysis['experience_level'],
                "skills_found": analysis['skills'],
                "domains": analysis['domains'],
                "skills_count": analysis['skills_count']
            },
            "personalized_questions": personalized_questions,
            "recommendations": {
                "suggested_difficulty": analysis['experience_level'],
                "focus_areas": analysis['domains'],
                "interview_duration": "45 minutes" if analysis['experience_level'] in ['advanced', 'expert'] else "30 minutes"
            }
        }
        
    except Exception as e:
        logging.error(f"Resume parsing error: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing resume: {str(e)}")

@router.get("/resume-parsing-status")
async def resume_parsing_status():
    """Check if resume parsing is available."""
    return {
        "available": RESUME_PARSING_AVAILABLE,
        "required_packages": ["PyPDF2", "python-docx"] if not RESUME_PARSING_AVAILABLE else [],
        "supported_formats": ["PDF", "DOCX", "TXT"] if RESUME_PARSING_AVAILABLE else []
    }
