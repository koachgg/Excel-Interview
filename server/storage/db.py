from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
import os
from typing import Generator

from storage.models import Base, Interview, Turn, Rubric, Question

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./interviews.db")

# Ensure directory exists for SQLite database
if DATABASE_URL.startswith("sqlite:///"):
    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not db_path.startswith(":memory:"):
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class InterviewRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_interview(self, candidate_name: str = None) -> Interview:
        interview = Interview(candidate_name=candidate_name)
        self.db.add(interview)
        self.db.commit()
        self.db.refresh(interview)
        return interview
    
    def get_interview(self, interview_id: int) -> Interview:
        return self.db.query(Interview).filter(Interview.id == interview_id).first()
    
    def update_interview(self, interview_id: int, **kwargs) -> Interview:
        interview = self.get_interview(interview_id)
        if interview:
            for key, value in kwargs.items():
                setattr(interview, key, value)
            self.db.commit()
            self.db.refresh(interview)
        return interview
    
    def add_turn(self, interview_id: int, turn_number: int, question: str, 
                 target_skill: str, difficulty: int) -> Turn:
        turn = Turn(
            interview_id=interview_id,
            turn_number=turn_number,
            question=question,
            target_skill=target_skill,
            difficulty=difficulty
        )
        self.db.add(turn)
        self.db.commit()
        self.db.refresh(turn)
        return turn
    
    def update_turn(self, turn_id: int, **kwargs) -> Turn:
        turn = self.db.query(Turn).filter(Turn.id == turn_id).first()
        if turn:
            for key, value in kwargs.items():
                setattr(turn, key, value)
            self.db.commit()
            self.db.refresh(turn)
        return turn

class RubricRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_rubric(self, skill_name: str, category: str, difficulty_tier: int,
                      rubric_data: dict, version: str = "1.0") -> Rubric:
        rubric = Rubric(
            skill_name=skill_name,
            category=category,
            difficulty_tier=difficulty_tier,
            rubric_data=rubric_data,
            version=version
        )
        self.db.add(rubric)
        self.db.commit()
        self.db.refresh(rubric)
        return rubric
    
    def get_rubrics_by_skill(self, skill_name: str):
        return self.db.query(Rubric).filter(Rubric.skill_name == skill_name).all()
    
    def get_all_rubrics(self):
        return self.db.query(Rubric).all()

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_question(self, skill: str, category: str, difficulty: int,
                       question_text: str, expected_answer: str, 
                       validation_rules: list = None) -> Question:
        question = Question(
            skill=skill,
            category=category,
            difficulty=difficulty,
            question_text=question_text,
            expected_answer=expected_answer,
            validation_rules=validation_rules or []
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question
    
    def get_questions_by_skill(self, skill: str, difficulty: int = None):
        query = self.db.query(Question).filter(Question.skill == skill)
        if difficulty:
            query = query.filter(Question.difficulty == difficulty)
        return query.all()
    
    def get_random_question(self, skill: str, difficulty: int):
        return self.db.query(Question).filter(
            Question.skill == skill,
            Question.difficulty == difficulty
        ).first()
