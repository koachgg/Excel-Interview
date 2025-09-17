from enum import Enum
from typing import Dict, Any, List, Optional, Tuple
import json
import random
from datetime import datetime
from sqlalchemy.orm import Session

from llm.provider_abstraction import provider_manager
from storage.db import InterviewRepository, QuestionRepository, Turn
from graders.hybrid import HybridGrader

class InterviewState(Enum):
    INTRO = "INTRO"
    CALIBRATE = "CALIBRATE"
    CORE_Q = "CORE_Q"
    DEEP_DIVE = "DEEP_DIVE"
    CASE = "CASE"
    REVIEW = "REVIEW"
    SUMMARY = "SUMMARY"

class InterviewAgent:
    """
    State machine-based interview agent that conducts structured Excel interviews
    with adaptive difficulty and comprehensive coverage tracking.
    """
    
    def __init__(self):
        self.coverage_skills = [
            "references", "ranges", "formatting", "if_functions", "vlookup",
            "index_match", "countif", "sumif", "text_functions", "date_functions",
            "sorting", "filtering", "pivot_tables", "validation", "conditional_formatting",
            "whatif_analysis", "goal_seek", "statistics", "error_tracing", "charts"
        ]
        
        self.skill_categories = {
            "foundations": ["references", "ranges", "formatting"],
            "functions": ["if_functions", "vlookup", "index_match", "countif", "sumif", "text_functions", "date_functions"],
            "data_ops": ["sorting", "filtering", "pivot_tables", "validation", "conditional_formatting"],
            "analysis": ["whatif_analysis", "goal_seek", "statistics", "error_tracing"],
            "charts": ["charts"]
        }
        
        self.max_turns = 25
        self.time_limit_minutes = 45
        self.grader = HybridGrader()
    
    def start_interview(self, interview_id: int) -> Dict[str, Any]:
        """Start a new interview session"""
        coverage_vector = {skill: 0 for skill in self.coverage_skills}
        
        question = """Hello! I'm your Excel interviewer today. I'll be conducting a comprehensive assessment of your Excel skills across various areas including formulas, data analysis, and chart creation.

The interview will take approximately 30-45 minutes and will progressively increase in difficulty based on your responses. Please answer as thoroughly as possible and feel free to explain your reasoning.

Let's start with a brief introduction: Could you tell me about your experience with Excel and what you consider your strongest Excel skills?"""

        return {
            "state": InterviewState.INTRO.value,
            "question": question,
            "target_skill": "introduction",
            "difficulty": 1,
            "next_action": "AWAIT_ANSWER",
            "coverage_vector": coverage_vector,
            "rubric_ref": None,
            "ask_clarification_opt": None
        }
    
    def process_turn(self, interview_id: int, answer: str, current_state: str, db: Session) -> Dict[str, Any]:
        """Process candidate answer and generate next question"""
        repo = InterviewRepository(db)
        interview = repo.get_interview(interview_id)
        
        if not interview:
            raise ValueError("Interview not found")
        
        # Get turn count
        turn_count = len(interview.turns)
        
        # Check termination conditions
        if turn_count >= self.max_turns:
            return self._end_interview("Maximum turns reached")
        
        # PREVENT EARLY TERMINATION - require minimum 8 questions
        if turn_count < 8:
            # Force continuation in current state or CORE_Q
            if current_state in [InterviewState.INTRO, InterviewState.CALIBRATE]:
                pass  # Let normal flow continue
            else:
                # Force back to CORE_Q if trying to exit too early
                current_state = InterviewState.CORE_Q.value
        
        # Get current state and coverage
        state = InterviewState(current_state)
        coverage_vector = interview.coverage_vector or {skill: 0 for skill in self.coverage_skills}
        
        # Grade the previous answer if applicable
        if turn_count > 1:
            # TODO: Fix async grading - temporarily disabled to prevent coroutine errors
            pass  # self._grade_previous_answer(interview_id, answer, db)
        
        # Determine next state and question
        next_response = self._state_transition(state, interview_id, coverage_vector, db)
        
        return next_response
    
    def _state_transition(self, current_state: InterviewState, interview_id: int, 
                         coverage_vector: Dict[str, int], db: Session) -> Dict[str, Any]:
        """Handle state transitions and generate appropriate questions"""
        
        if current_state == InterviewState.INTRO:
            return self._transition_to_calibrate(coverage_vector, db)
        
        elif current_state == InterviewState.CALIBRATE:
            return self._transition_to_core(coverage_vector, db)
        
        elif current_state == InterviewState.CORE_Q:
            # Check if we need deep dive or continue with core questions
            if self._needs_deep_dive(coverage_vector):
                return self._transition_to_deep_dive(coverage_vector, db)
            elif self._core_coverage_sufficient(coverage_vector):
                return self._transition_to_case(coverage_vector)
            else:
                return self._continue_core_questions(coverage_vector, db)
        
        elif current_state == InterviewState.DEEP_DIVE:
            if self._deep_dive_complete(coverage_vector):
                return self._transition_to_case(coverage_vector)
            else:
                return self._continue_deep_dive(coverage_vector, db)
        
        elif current_state == InterviewState.CASE:
            return self._transition_to_review(coverage_vector)
        
        elif current_state == InterviewState.REVIEW:
            return self._transition_to_summary()
        
        else:
            return self._end_interview("Interview complete")
    
    def _transition_to_calibrate(self, coverage_vector: Dict[str, int], db: Session) -> Dict[str, Any]:
        """Transition to calibration with a basic formula question"""
        question_prompt = """
        Generate a calibration question for an Excel interview. This should be a basic question about Excel formulas or functions to gauge the candidate's fundamental skill level.
        
        Examples of good calibration questions:
        - How would you create a formula to sum values in cells A1 through A10?
        - What's the difference between relative and absolute cell references?
        - How would you use the VLOOKUP function to find data?
        
        Respond with JSON:
        {
            "question": "The calibration question text",
            "target_skill": "skill being tested",
            "difficulty": 1,
            "expected_approach": "brief description of expected answer approach"
        }
        """
        
        try:
            response = provider_manager.generate_interview_question(question_prompt, temperature=0.7)
            parsed = json.loads(response)
            
            # Update coverage for calibration skill
            skill = parsed.get("target_skill", "references")
            coverage_vector[skill] = max(coverage_vector.get(skill, 0), 1)
            
            return {
                "state": InterviewState.CALIBRATE.value,
                "question": parsed["question"],
                "target_skill": skill,
                "difficulty": 1,
                "next_action": "AWAIT_ANSWER",
                "coverage_vector": coverage_vector,
                "rubric_ref": f"calibration_{skill}",
                "ask_clarification_opt": None
            }
            
        except Exception as e:
            # Fallback question
            return {
                "state": InterviewState.CALIBRATE.value,
                "question": "How would you create a formula to sum all values in column A from row 1 to row 100?",
                "target_skill": "basic_formulas",
                "difficulty": 1,
                "next_action": "AWAIT_ANSWER",
                "coverage_vector": coverage_vector,
                "rubric_ref": "calibration_basic_formulas"
            }
    
    def _transition_to_core(self, coverage_vector: Dict[str, int], db: Session) -> Dict[str, Any]:
        """Transition to core questions based on coverage gaps"""
        # Find skill with lowest coverage in foundations/functions
        priority_skills = self.skill_categories["foundations"] + self.skill_categories["functions"]
        uncovered_skills = [skill for skill in priority_skills if coverage_vector.get(skill, 0) == 0]
        
        if uncovered_skills:
            target_skill = random.choice(uncovered_skills)
        else:
            # Find skill with lowest coverage overall
            target_skill = min(priority_skills, key=lambda x: coverage_vector.get(x, 0))
        
        question = self._generate_skill_question(target_skill, difficulty=2)
        coverage_vector[target_skill] = max(coverage_vector.get(target_skill, 0), 2)
        
        return {
            "state": InterviewState.CORE_Q.value,
            "question": question["question"],
            "target_skill": target_skill,
            "difficulty": 2,
            "next_action": "AWAIT_ANSWER",
            "coverage_vector": coverage_vector,
            "rubric_ref": f"core_{target_skill}_level2"
        }
    
    def _continue_core_questions(self, coverage_vector: Dict[str, int], db: Session) -> Dict[str, Any]:
        """Continue with core questions for uncovered skills"""
        # Find next skill to test
        all_skills = self.skill_categories["foundations"] + self.skill_categories["functions"] + self.skill_categories["data_ops"]
        uncovered = [skill for skill in all_skills if coverage_vector.get(skill, 0) < 2]
        
        if uncovered:
            target_skill = random.choice(uncovered)
            difficulty = 2
        else:
            # Increase difficulty for already covered skills
            target_skill = random.choice(all_skills)
            difficulty = min(3, coverage_vector.get(target_skill, 0) + 1)
        
        question = self._generate_skill_question(target_skill, difficulty)
        coverage_vector[target_skill] = max(coverage_vector.get(target_skill, 0), difficulty)
        
        return {
            "state": InterviewState.CORE_Q.value,
            "question": question["question"],
            "target_skill": target_skill,
            "difficulty": difficulty,
            "next_action": "AWAIT_ANSWER",
            "coverage_vector": coverage_vector,
            "rubric_ref": f"core_{target_skill}_level{difficulty}"
        }
    
    def _transition_to_case(self, coverage_vector: Dict[str, int]) -> Dict[str, Any]:
        """Transition to case study"""
        case_question = """
        Now I'd like you to work through a practical scenario. Imagine you have a dataset with the following columns in Excel:
        
        A: Employee Name
        B: Department 
        C: Hire Date
        D: Salary
        E: Performance Rating (1-5)
        
        The data spans rows 2-101 (100 employees, with headers in row 1).
        
        Please provide Excel formulas or approaches for the following:
        1. Calculate the average salary by department
        2. Count how many employees have a performance rating of 4 or 5
        3. Find the employee with the highest salary in the Sales department
        4. Calculate the percentage of employees hired in the last 2 years
        
        Explain your formulas and reasoning for each solution.
        """
        
        return {
            "state": InterviewState.CASE.value,
            "question": case_question,
            "target_skill": "case_analysis",
            "difficulty": 3,
            "next_action": "AWAIT_ANSWER",
            "coverage_vector": coverage_vector,
            "rubric_ref": "case_study_comprehensive"
        }
    
    def _transition_to_review(self, coverage_vector: Dict[str, int]) -> Dict[str, Any]:
        """Transition to review phase"""
        return {
            "state": InterviewState.REVIEW.value,
            "question": "Thank you for working through that case study. Before we conclude, do you have any questions about Excel functionality, or would you like to clarify any of your previous answers?",
            "target_skill": "review",
            "difficulty": 1,
            "next_action": "AWAIT_ANSWER",
            "coverage_vector": coverage_vector,
            "rubric_ref": "review_clarification"
        }
    
    def _transition_to_summary(self) -> Dict[str, Any]:
        """Transition to summary/end"""
        return {
            "state": InterviewState.SUMMARY.value,
            "question": "That concludes our Excel interview. Thank you for your time and responses. I'll now prepare your detailed feedback report.",
            "target_skill": "conclusion",
            "difficulty": 1,
            "next_action": "END_INTERVIEW",
            "coverage_vector": {},
            "rubric_ref": "interview_conclusion"
        }
    
    def _generate_skill_question(self, skill: str, difficulty: int) -> Dict[str, Any]:
        """Generate a question for a specific skill and difficulty level"""
        question_templates = {
            "vlookup": {
                2: "You have a table with Product IDs in column A and Product Names in column B. How would you use VLOOKUP to find the product name for a specific ID in another worksheet?",
                3: "Explain how to use VLOOKUP with approximate match and why you might choose this over exact match. Provide an example formula."
            },
            "if_functions": {
                2: "How would you create a formula that displays 'Pass' if a score in cell B2 is 70 or above, and 'Fail' if below 70?",
                3: "Create a nested IF formula that assigns grades: A (90+), B (80-89), C (70-79), D (60-69), F (<60) based on a score in cell B2."
            },
            "pivot_tables": {
                2: "Describe the steps to create a basic pivot table from a dataset with Sales Rep, Region, and Sales Amount columns.",
                3: "How would you modify a pivot table to show both count and percentage of total sales by region, and add a filter for specific time periods?"
            }
        }
        
        if skill in question_templates and difficulty in question_templates[skill]:
            return {"question": question_templates[skill][difficulty]}
        
        # Fallback to generic question generation
        return {"question": f"Please explain how you would approach {skill.replace('_', ' ')} in Excel."}
    
    def _grade_previous_answer(self, interview_id: int, answer: str, db: Session):
        """Grade the previous answer using hybrid grader"""
        repo = InterviewRepository(db)
        
        # Get the most recent turn
        recent_turn = db.query(Turn).filter(
            Turn.interview_id == interview_id
        ).order_by(Turn.turn_number.desc()).first()
        
        if recent_turn:
            # Grade using hybrid grader
            grading_result = self.grader.grade_answer(
                question=recent_turn.question,
                answer=answer,
                target_skill=recent_turn.target_skill,
                difficulty=recent_turn.difficulty
            )
            
            # Update turn with grading results
            repo.update_turn(
                recent_turn.id,
                answer=answer,
                rule_score=grading_result.get("rule_score"),
                llm_score=grading_result.get("llm_score"),
                hybrid_score=grading_result.get("hybrid_score"),
                error_tags=grading_result.get("error_tags", []),
                feedback=grading_result.get("feedback"),
                confidence=grading_result.get("confidence")
            )
    
    def _needs_deep_dive(self, coverage_vector: Dict[str, int]) -> bool:
        """Determine if candidate needs deep dive questions - MADE MORE SELECTIVE"""
        # Only deep dive if candidate is performing very well (at least 15 questions asked)
        core_skills = self.skill_categories["foundations"] + self.skill_categories["functions"]
        total_asked = sum(coverage_vector.get(skill, 0) for skill in core_skills)
        avg_coverage = sum(coverage_vector.get(skill, 0) for skill in core_skills) / len(core_skills)
        return avg_coverage >= 3.0 and total_asked >= 15
    
    def _core_coverage_sufficient(self, coverage_vector: Dict[str, int]) -> bool:
        """Check if core coverage is sufficient to move to case - MADE MORE STRICT"""
        core_skills = self.skill_categories["foundations"] + self.skill_categories["functions"]
        # Require at least 8 questions instead of 70% coverage
        covered_count = sum(1 for skill in core_skills if coverage_vector.get(skill, 0) >= 2)
        total_asked = sum(coverage_vector.get(skill, 0) for skill in core_skills)
        return covered_count >= 8 and total_asked >= 12  # At least 12 questions asked in core skills
    
    def _deep_dive_complete(self, coverage_vector: Dict[str, int]) -> bool:
        """Check if deep dive is complete"""
        analysis_skills = self.skill_categories["analysis"]
        covered_count = sum(1 for skill in analysis_skills if coverage_vector.get(skill, 0) >= 3)
        return covered_count >= 2
    
    def _end_interview(self, reason: str) -> Dict[str, Any]:
        """End the interview"""
        return {
            "state": InterviewState.SUMMARY.value,
            "question": f"Interview completed: {reason}. Generating your detailed feedback report now.",
            "next_action": "END_INTERVIEW",
            "coverage_vector": {},
            "end_reason": reason
        }
