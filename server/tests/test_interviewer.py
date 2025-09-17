"""
Test interview agent state machine
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.interviewer import InterviewAgent, InterviewState
from storage.models import Interview, Question, Response

class TestInterviewAgent:
    """Test interview agent functionality"""
    
    def setup_method(self):
        # Mock database session
        self.mock_db = Mock()
        self.agent = InterviewAgent(self.mock_db)
    
    def test_initial_state(self):
        """Test agent starts in correct state"""
        assert self.agent.state == InterviewState.INTRO
        assert self.agent.turn_count == 0
        assert self.agent.candidate_performance == {}
    
    def test_state_transitions(self):
        """Test state machine transitions"""
        # INTRO -> CALIBRATE
        self.agent.state = InterviewState.INTRO
        next_state = self.agent._determine_next_state()
        assert next_state == InterviewState.CALIBRATE
        
        # CALIBRATE -> CORE_Q (with good performance)
        self.agent.state = InterviewState.CALIBRATE
        self.agent.candidate_performance = {"overall_accuracy": 0.8}
        next_state = self.agent._determine_next_state()
        assert next_state == InterviewState.CORE_Q
        
        # CORE_Q -> DEEP_DIVE (with excellent performance)
        self.agent.state = InterviewState.CORE_Q
        self.agent.candidate_performance = {"overall_accuracy": 0.9, "questions_answered": 8}
        next_state = self.agent._determine_next_state()
        assert next_state == InterviewState.DEEP_DIVE
        
        # CORE_Q -> CASE (with moderate performance, skip deep dive)
        self.agent.candidate_performance = {"overall_accuracy": 0.75, "questions_answered": 8}
        next_state = self.agent._determine_next_state()
        assert next_state == InterviewState.CASE
    
    def test_question_difficulty_adjustment(self):
        """Test difficulty adjustment based on performance"""
        # Low performance -> easier questions
        self.agent.candidate_performance = {"overall_accuracy": 0.4}
        difficulty = self.agent._get_target_difficulty()
        assert difficulty == 1
        
        # Good performance -> harder questions  
        self.agent.candidate_performance = {"overall_accuracy": 0.85}
        difficulty = self.agent._get_target_difficulty()
        assert difficulty == 3
        
        # Moderate performance -> medium questions
        self.agent.candidate_performance = {"overall_accuracy": 0.7}
        difficulty = self.agent._get_target_difficulty()
        assert difficulty == 2
    
    @patch('storage.repositories.QuestionRepository.get_questions_by_criteria')
    def test_question_selection(self, mock_get_questions):
        """Test question selection logic"""
        # Mock available questions
        mock_questions = [
            Mock(id=1, skill="vlookup", difficulty=2),
            Mock(id=2, skill="if_functions", difficulty=2),  
            Mock(id=3, skill="pivot_tables", difficulty=3)
        ]
        mock_get_questions.return_value = mock_questions
        
        self.agent.state = InterviewState.CORE_Q
        self.agent.asked_questions = set()
        self.agent.skill_coverage = {"vlookup": 0, "if_functions": 0}
        
        question = self.agent._select_next_question()
        
        assert question is not None
        assert question.id in [1, 2, 3]
        mock_get_questions.assert_called_once()
    
    def test_skill_coverage_tracking(self):
        """Test tracking of skill area coverage"""
        # Initialize coverage
        self.agent._initialize_skill_coverage()
        assert len(self.agent.skill_coverage) > 0
        
        # Update coverage after question
        mock_question = Mock(skill="vlookup")
        self.agent._update_skill_coverage(mock_question, 85.0)
        assert self.agent.skill_coverage["vlookup"] > 0
    
    def test_performance_calculation(self):
        """Test candidate performance calculation"""
        # Add some mock responses
        mock_responses = [
            Mock(score=85.0, question=Mock(skill="vlookup", difficulty=2)),
            Mock(score=70.0, question=Mock(skill="if_functions", difficulty=1)),
            Mock(score=90.0, question=Mock(skill="sumif", difficulty=2))
        ]
        
        self.agent.responses = mock_responses
        performance = self.agent._calculate_performance()
        
        assert "overall_accuracy" in performance
        assert "questions_answered" in performance
        assert "skill_breakdown" in performance
        assert 0 <= performance["overall_accuracy"] <= 1
        assert performance["questions_answered"] == 3
    
    def test_interview_completion_logic(self):
        """Test logic for determining interview completion"""
        # Not enough questions asked
        self.agent.turn_count = 5
        self.agent.skill_coverage = {"vlookup": 1, "if_functions": 0}
        assert not self.agent._should_end_interview()
        
        # Sufficient questions and coverage
        self.agent.turn_count = 20
        self.agent.skill_coverage = {"vlookup": 3, "if_functions": 2, "sumif": 2}
        self.agent.state = InterviewState.CASE
        assert self.agent._should_end_interview()
        
        # Maximum questions reached
        self.agent.turn_count = 25
        assert self.agent._should_end_interview()
    
    @patch('graders.hybrid.HybridGrader.grade_response')
    def test_response_processing(self, mock_grader):
        """Test processing of candidate responses"""
        # Mock grading result
        mock_grader.return_value = {
            "score": 80.0,
            "feedback": "Good answer with minor issues",
            "method": "hybrid"
        }
        
        mock_question = Mock(
            id=1,
            skill="vlookup", 
            difficulty=2,
            question_text="Test question"
        )
        
        result = self.agent.process_response("=VLOOKUP(A1,B:C,2,FALSE)", mock_question)
        
        assert result["score"] == 80.0
        assert "feedback" in result
        mock_grader.assert_called_once()

class TestInterviewFlow:
    """Test complete interview flow scenarios"""
    
    def setup_method(self):
        self.mock_db = Mock()
        self.agent = InterviewAgent(self.mock_db)
    
    @patch('agents.interviewer.InterviewAgent._select_next_question')
    @patch('graders.hybrid.HybridGrader.grade_response')  
    def test_novice_interview_path(self, mock_grader, mock_question_selector):
        """Test interview path for novice candidate"""
        # Mock questions for novice level
        mock_questions = [
            Mock(id=1, skill="references", difficulty=1, question_text="What is A1?"),
            Mock(id=2, skill="basic_formulas", difficulty=1, question_text="How to sum?"),
            Mock(id=3, skill="ranges", difficulty=1, question_text="What is A1:A10?")
        ]
        mock_question_selector.side_effect = mock_questions
        
        # Mock low scores
        mock_grader.return_value = {
            "score": 45.0,
            "feedback": "Basic understanding, needs improvement",
            "method": "hybrid"
        }
        
        # Simulate interview flow
        responses = [
            "Hello, I'm ready to start",
            "A1 is a cell",
            "Add numbers together", 
            "Select multiple cells"
        ]
        
        for i, response in enumerate(responses):
            if i == 0:
                # Introduction turn
                result = self.agent.process_turn(response)
                assert self.agent.state in [InterviewState.INTRO, InterviewState.CALIBRATE]
            else:
                # Question turns
                result = self.agent.process_turn(response)
                assert "score" in result or "question" in result
        
        # Should stay at lower difficulty levels
        assert self.agent._get_target_difficulty() <= 2
    
    @patch('agents.interviewer.InterviewAgent._select_next_question')
    @patch('graders.hybrid.HybridGrader.grade_response')
    def test_advanced_interview_path(self, mock_grader, mock_question_selector):
        """Test interview path for advanced candidate"""
        # Mock questions progressing in difficulty
        mock_questions = [
            Mock(id=1, skill="references", difficulty=1, question_text="References?"),
            Mock(id=2, skill="vlookup", difficulty=2, question_text="VLOOKUP formula?"),
            Mock(id=3, skill="index_match", difficulty=3, question_text="INDEX/MATCH vs VLOOKUP?"),
            Mock(id=4, skill="case_analysis", difficulty=3, question_text="Complex scenario?")
        ]
        mock_question_selector.side_effect = mock_questions
        
        # Mock high scores
        mock_grader.return_value = {
            "score": 90.0,
            "feedback": "Excellent understanding and application",
            "method": "hybrid"
        }
        
        responses = [
            "Ready to begin the assessment",
            "$A$1 is absolute, A1 is relative reference that adjusts when copied",
            "=VLOOKUP(lookup_value,table_array,col_index,FALSE) for exact match",
            "INDEX/MATCH is more flexible, can look left, doesn't break with column changes",
            "I would analyze requirements, create pivot tables, use advanced functions"
        ]
        
        for i, response in enumerate(responses):
            result = self.agent.process_turn(response)
            
            if i > 0:  # After intro
                # Should progress through states
                expected_states = [
                    InterviewState.CALIBRATE,
                    InterviewState.CORE_Q, 
                    InterviewState.DEEP_DIVE,
                    InterviewState.CASE
                ]
                assert self.agent.state in expected_states
        
        # Should reach higher difficulty levels
        assert self.agent._get_target_difficulty() >= 2
    
    def test_interview_state_persistence(self):
        """Test that interview state is properly maintained"""
        # Track state changes
        initial_state = self.agent.state
        
        self.agent.state = InterviewState.CALIBRATE
        self.agent.turn_count = 3
        self.agent.skill_coverage = {"vlookup": 2}
        
        # State should persist
        assert self.agent.state == InterviewState.CALIBRATE
        assert self.agent.turn_count == 3
        assert self.agent.skill_coverage["vlookup"] == 2
    
    def test_adaptive_questioning(self):
        """Test that questioning adapts to candidate level"""
        # Start with low performance
        self.agent.candidate_performance = {"overall_accuracy": 0.3}
        difficulty1 = self.agent._get_target_difficulty()
        
        # Improve performance
        self.agent.candidate_performance = {"overall_accuracy": 0.8}
        difficulty2 = self.agent._get_target_difficulty()
        
        # Difficulty should increase with better performance
        assert difficulty2 >= difficulty1

class TestInterviewEdgeCases:
    """Test edge cases and error handling"""
    
    def setup_method(self):
        self.mock_db = Mock()
        self.agent = InterviewAgent(self.mock_db)
    
    def test_empty_response_handling(self):
        """Test handling of empty responses"""
        result = self.agent.process_turn("")
        assert "message" in result
        assert "please provide" in result["message"].lower() or "empty" in result["message"].lower()
    
    def test_very_long_response_handling(self):
        """Test handling of very long responses"""
        long_response = "This is a very long response. " * 100
        result = self.agent.process_turn(long_response)
        # Should handle gracefully without errors
        assert "message" in result or "feedback" in result
    
    def test_no_questions_available(self):
        """Test behavior when no questions are available"""
        with patch('storage.repositories.QuestionRepository.get_questions_by_criteria') as mock_get:
            mock_get.return_value = []
            
            # Should handle gracefully
            question = self.agent._select_next_question()
            # May return None or a default question
            assert question is None or hasattr(question, 'question_text')
    
    def test_grading_error_recovery(self):
        """Test recovery from grading errors"""
        with patch('graders.hybrid.HybridGrader.grade_response') as mock_grader:
            # Simulate grading error
            mock_grader.side_effect = Exception("Grading service unavailable")
            
            mock_question = Mock(id=1, skill="test", difficulty=1)
            
            # Should not crash, return default response
            result = self.agent.process_response("test answer", mock_question)
            assert isinstance(result, dict)
            assert "score" in result or "error" in str(result).lower()
    
    def test_interview_timeout_handling(self):
        """Test handling of interview timeouts"""
        # Simulate very long interview
        self.agent.turn_count = 50  # Exceed normal limits
        
        # Should force completion
        assert self.agent._should_end_interview() == True
    
    def test_invalid_state_transitions(self):
        """Test handling of invalid state transitions"""
        # Try to go backwards in states
        self.agent.state = InterviewState.SUMMARY
        
        # Should not allow going back to earlier states
        next_state = self.agent._determine_next_state()
        assert next_state == InterviewState.SUMMARY  # Should stay in final state

if __name__ == "__main__":
    pytest.main([__file__])
