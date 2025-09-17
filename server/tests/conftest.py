# Test Configuration
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add the server directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import app
from storage.db import get_db, create_tables
from storage.models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Test database configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as client:
        yield client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)
    if os.path.exists("test.db"):
        os.remove("test.db")

@pytest.fixture(scope="session")
def test_db():
    """Create a test database session"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    """Mock environment variables for testing"""
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_key")
    monkeypatch.setenv("GROQ_API_KEY", "test_groq_key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test_anthropic_key")
    monkeypatch.setenv("PRIMARY_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("MOCK_LLM_RESPONSES", "true")
    monkeypatch.setenv("DEBUG", "true")

# Test data fixtures
@pytest.fixture
def sample_interview_data():
    return {
        "candidate_name": "Test Candidate",
        "start_time": "2024-01-15T10:00:00",
        "state": "INTRO"
    }

@pytest.fixture  
def sample_question_data():
    return {
        "skill": "vlookup",
        "category": "functions",
        "difficulty": 2,
        "question_text": "How would you use VLOOKUP to find a product name?",
        "expected_answer": "=VLOOKUP(lookup_value, table_array, col_index, FALSE)",
        "validation_rules": ["uses_vlookup", "correct_syntax", "exact_match"]
    }

@pytest.fixture
def sample_response_data():
    return {
        "answer_text": "I would use =VLOOKUP(A1, B:C, 2, FALSE) to find the product name.",
        "score": 85.0,
        "feedback": "Good use of VLOOKUP with exact match."
    }
