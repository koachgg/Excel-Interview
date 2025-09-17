from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any

Base = declarative_base()

class Interview(Base):
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String, nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    state = Column(String, default="INTRO")
    total_score = Column(Float, nullable=True)
    difficulty_level = Column(Integer, default=1)
    coverage_vector = Column(JSON, default=dict)  # Track skills covered
    additional_info = Column(JSON, default=dict)  # Renamed from metadata to avoid SQLAlchemy conflict
    
    turns = relationship("Turn", back_populates="interview")
    
class Turn(Base):
    __tablename__ = "turns"
    
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    turn_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    question = Column(Text)
    answer = Column(Text)
    target_skill = Column(String)
    difficulty = Column(Integer)
    
    # Grading results
    rule_score = Column(Float, nullable=True)
    llm_score = Column(Float, nullable=True)
    hybrid_score = Column(Float, nullable=True)
    error_tags = Column(JSON, default=list)
    feedback = Column(Text, nullable=True)
    confidence = Column(Float, nullable=True)
    
    interview = relationship("Interview", back_populates="turns")

class Rubric(Base):
    __tablename__ = "rubrics"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, default="1.0")
    skill_name = Column(String)
    category = Column(String)  # foundations, functions, data_ops, analysis, charts
    difficulty_tier = Column(Integer)  # 1=basic, 2=intermediate, 3=advanced
    
    rubric_data = Column(JSON)  # Detailed scoring criteria
    created_at = Column(DateTime, default=datetime.utcnow)

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String)
    category = Column(String)
    difficulty = Column(Integer)
    question_text = Column(Text)
    expected_answer = Column(Text)
    validation_rules = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
