"""
Test grading system components
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from graders.rule_based import RuleBasedGrader
from graders.llm_based import LLMBasedGrader
from graders.hybrid import HybridGrader

class TestRuleBasedGrader:
    """Test rule-based grading logic"""
    
    def setup_method(self):
        self.grader = RuleBasedGrader()
    
    def test_vlookup_formula_validation(self):
        """Test VLOOKUP formula validation"""
        # Valid VLOOKUP formulas
        valid_formulas = [
            "=VLOOKUP(A1,B:C,2,FALSE)",
            "=vlookup(\"test\",A1:B10,2,0)",
            "= VLOOKUP ( E1 , A:B , 2 , FALSE )",
        ]
        
        for formula in valid_formulas:
            result = self.grader.validate_formula(formula, "vlookup")
            assert result["is_valid"] == True
            assert "uses_vlookup" in result["matched_rules"]
    
    def test_if_formula_validation(self):
        """Test IF formula validation"""
        valid_if_formulas = [
            "=IF(A1>10,\"High\",\"Low\")",
            "=if(B2>=70,'Pass','Fail')",
            "=IF(AND(A1>0,A1<100),A1*2,0)"
        ]
        
        for formula in valid_if_formulas:
            result = self.grader.validate_formula(formula, "if_functions")
            assert result["is_valid"] == True
            assert "uses_if" in result["matched_rules"]
    
    def test_invalid_formula_detection(self):
        """Test detection of invalid formulas"""
        invalid_formulas = [
            "VLOOKUP(A1,B:C,2,FALSE)",  # Missing =
            "=VLOOKUP(A1,B:C)",         # Too few arguments
            "=IF(A1>10)",               # Incomplete IF
            "random text",              # Not a formula
        ]
        
        for formula in invalid_formulas:
            result = self.grader.validate_formula(formula, "vlookup")
            assert result["is_valid"] == False
    
    def test_sumif_validation(self):
        """Test SUMIF formula validation"""
        valid_sumif = [
            "=SUMIF(A:A,\"Sales\",B:B)",
            "=sumif(A1:A10,\">100\",B1:B10)",
            "=SUMIF(range,criteria,sum_range)"
        ]
        
        for formula in valid_sumif:
            result = self.grader.validate_formula(formula, "sumif")
            assert result["is_valid"] == True
            assert "uses_sumif" in result["matched_rules"]
    
    def test_countif_validation(self):
        """Test COUNTIF formula validation"""
        valid_countif = [
            "=COUNTIF(A:A,\">10\")",
            "=countif(B1:B50,\"criteria\")",
            "=COUNTIF(range,condition)"
        ]
        
        for formula in valid_countif:
            result = self.grader.validate_formula(formula, "countif")
            assert result["is_valid"] == True
            assert "uses_countif" in result["matched_rules"]
    
    def test_complex_formula_validation(self):
        """Test validation of complex formulas"""
        complex_formulas = [
            "=IF(VLOOKUP(A1,Sheet2!B:C,2,0)>100,\"High\",\"Low\")",
            "=SUMIF(A:A,\"Sales\",B:B)+SUMIF(A:A,\"Marketing\",B:B)",
            "=INDEX(B:B,MATCH(A1,C:C,0))"
        ]
        
        for formula in complex_formulas:
            # Should detect at least one valid function
            result = self.grader.validate_formula(formula, "if_functions")
            assert len(result["matched_rules"]) > 0
    
    def test_score_calculation(self):
        """Test score calculation based on rules"""
        # Test high match scenario
        validation_result = {
            "is_valid": True,
            "matched_rules": ["uses_vlookup", "correct_syntax", "exact_match"],
            "rule_scores": {"uses_vlookup": 40, "correct_syntax": 30, "exact_match": 20}
        }
        
        score = self.grader.calculate_score(validation_result)
        assert score >= 80  # Should get high score for matching all rules
        
        # Test partial match scenario
        validation_result = {
            "is_valid": True,
            "matched_rules": ["uses_vlookup"],
            "rule_scores": {"uses_vlookup": 40}
        }
        
        score = self.grader.calculate_score(validation_result)
        assert 30 <= score <= 60  # Should get partial score

class TestLLMBasedGrader:
    """Test LLM-based grading logic"""
    
    def setup_method(self):
        self.grader = LLMBasedGrader()
    
    @patch('llm.provider_abstraction.get_llm_client')
    def test_explanation_grading(self, mock_get_client):
        """Test grading of explanations"""
        # Mock LLM response
        mock_client = Mock()
        mock_client.generate.return_value = {
            "response": "Score: 85\nFeedback: Good explanation of VLOOKUP with clear understanding of parameters.",
            "usage": {"input_tokens": 100, "output_tokens": 50}
        }
        mock_get_client.return_value = mock_client
        
        question = {
            "question_text": "Explain how VLOOKUP works",
            "expected_answer": "VLOOKUP searches for a value and returns corresponding data",
            "skill": "vlookup"
        }
        
        answer = "VLOOKUP looks up a value in the first column and returns a value from another column in the same row."
        
        result = self.grader.grade_explanation(question, answer)
        
        assert result["score"] == 85
        assert "feedback" in result
        assert result["method"] == "llm_based"
    
    @patch('llm.provider_abstraction.get_llm_client')  
    def test_conceptual_understanding(self, mock_get_client):
        """Test grading of conceptual understanding"""
        mock_client = Mock()
        mock_client.generate.return_value = {
            "response": "Score: 75\nFeedback: Shows good understanding but missing some details about exact vs approximate match.",
            "usage": {"input_tokens": 120, "output_tokens": 60}
        }
        mock_get_client.return_value = mock_client
        
        question = {
            "question_text": "When would you use INDEX/MATCH instead of VLOOKUP?",
            "expected_answer": "INDEX/MATCH is more flexible and can look to the left",
            "skill": "index_match"
        }
        
        answer = "INDEX/MATCH is better when you need to look to the left of your lookup column."
        
        result = self.grader.grade_explanation(question, answer)
        
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 100
        assert "feedback" in result
    
    def test_error_handling(self):
        """Test error handling in LLM grading"""
        # Test with None answer
        result = self.grader.grade_explanation({}, None)
        assert result["score"] == 0
        assert "error" in result["feedback"].lower()
        
        # Test with empty answer  
        result = self.grader.grade_explanation({}, "")
        assert result["score"] == 0

class TestHybridGrader:
    """Test hybrid grading system"""
    
    def setup_method(self):
        self.grader = HybridGrader()
    
    @patch('graders.llm_based.LLMBasedGrader.grade_explanation')
    @patch('graders.rule_based.RuleBasedGrader.validate_formula')
    def test_formula_question_grading(self, mock_rule_grader, mock_llm_grader):
        """Test grading of formula questions using hybrid approach"""
        # Mock rule-based grading
        mock_rule_grader.return_value = {
            "is_valid": True,
            "matched_rules": ["uses_vlookup", "correct_syntax"],
            "score": 80
        }
        
        # Mock LLM-based grading
        mock_llm_grader.return_value = {
            "score": 75,
            "feedback": "Good formula structure",
            "method": "llm_based"
        }
        
        question = {
            "question_text": "Write a VLOOKUP formula",
            "expected_answer": "=VLOOKUP(...)",
            "skill": "vlookup",
            "validation_rules": ["uses_vlookup", "correct_syntax"]
        }
        
        answer = "=VLOOKUP(A1,B:C,2,FALSE)"
        
        result = self.grader.grade_response(question, answer)
        
        assert isinstance(result["score"], (int, float))
        assert 70 <= result["score"] <= 85  # Should be weighted average
        assert result["method"] == "hybrid"
        assert "feedback" in result
    
    @patch('graders.llm_based.LLMBasedGrader.grade_explanation')
    def test_explanation_question_grading(self, mock_llm_grader):
        """Test grading of explanation questions"""
        mock_llm_grader.return_value = {
            "score": 85,
            "feedback": "Excellent explanation",
            "method": "llm_based"
        }
        
        question = {
            "question_text": "Explain the difference between relative and absolute references",
            "expected_answer": "A1 changes when copied, $A$1 stays fixed",
            "skill": "references"
        }
        
        answer = "A1 is relative and changes when you copy the formula. $A$1 is absolute and stays the same."
        
        result = self.grader.grade_response(question, answer)
        
        assert result["score"] == 85
        assert result["method"] == "llm_based"
        assert "feedback" in result
    
    def test_grading_method_selection(self):
        """Test selection of appropriate grading method"""
        # Formula questions should use hybrid approach
        formula_question = {
            "question_text": "Write a SUM formula",
            "expected_answer": "=SUM(A1:A10)",
            "skill": "basic_formulas"
        }
        
        method = self.grader._determine_grading_method(formula_question, "=SUM(A1:A10)")
        assert method in ["hybrid", "rule_based"]
        
        # Explanation questions should use LLM approach
        explanation_question = {
            "question_text": "Explain when to use pivot tables",
            "expected_answer": "Pivot tables are useful for summarizing data",
            "skill": "pivot_tables"
        }
        
        method = self.grader._determine_grading_method(explanation_question, "Pivot tables help analyze large datasets")
        assert method == "llm_based"
    
    def test_error_recovery(self):
        """Test error recovery in hybrid grading"""
        question = {
            "question_text": "Test question",
            "expected_answer": "Test answer",
            "skill": "test_skill"
        }
        
        # Test with None answer
        result = self.grader.grade_response(question, None)
        assert result["score"] == 0
        assert "error" in result["feedback"].lower()
        
        # Test with empty answer
        result = self.grader.grade_response(question, "")
        assert result["score"] == 0
        assert "empty" in result["feedback"].lower()

class TestGradingIntegration:
    """Test integration between different grading components"""
    
    @patch('llm.provider_abstraction.get_llm_client')
    def test_end_to_end_grading(self, mock_get_client):
        """Test complete grading flow"""
        mock_client = Mock()
        mock_client.generate.return_value = {
            "response": "Score: 90\nFeedback: Excellent VLOOKUP usage with proper syntax.",
            "usage": {"input_tokens": 150, "output_tokens": 75}
        }
        mock_get_client.return_value = mock_client
        
        hybrid_grader = HybridGrader()
        
        question = {
            "question_text": "Create a VLOOKUP formula to find product names",
            "expected_answer": "=VLOOKUP(lookup_value, table_array, 2, FALSE)",
            "skill": "vlookup",
            "validation_rules": ["uses_vlookup", "correct_syntax", "exact_match"]
        }
        
        answer = "=VLOOKUP(A1,Products!B:C,2,FALSE)"
        
        result = hybrid_grader.grade_response(question, answer)
        
        assert isinstance(result["score"], (int, float))
        assert 0 <= result["score"] <= 100
        assert result["method"] in ["hybrid", "rule_based", "llm_based"]
        assert "feedback" in result
        assert len(result["feedback"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])
