from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import statistics

from graders.rule_based import RuleBasedGrader, RuleResult
from graders.llm_based import LLMBasedGrader, LLMGradingResult

@dataclass
class HybridGradingResult:
    rule_score: Optional[float]
    llm_score: Optional[float] 
    hybrid_score: float
    confidence: float
    error_tags: List[str]
    feedback: str
    grading_method: str  # "rule_only", "llm_only", "hybrid", "escalated"

class HybridGrader:
    """
    Hybrid grader that combines rule-based validation with LLM evaluation.
    Uses intelligent fallback and escalation strategies.
    """
    
    def __init__(self):
        self.rule_grader = RuleBasedGrader()
        self.llm_grader = LLMBasedGrader()
        
        # Confidence thresholds for different grading strategies
        self.high_confidence_threshold = 0.8
        self.escalation_threshold = 0.5
        self.disagreement_threshold = 20  # Points difference
        
        # Skills that are primarily rule-based vs LLM-based
        self.rule_heavy_skills = [
            "references", "basic_formulas", "vlookup", "if_functions"
        ]
        self.llm_heavy_skills = [
            "pivot_tables", "case_analysis", "charts", "best_practices"
        ]
    
    async def grade_answer(self, question: str, answer: str, target_skill: str,
                          difficulty: int, expected_answer: str = None) -> Dict[str, Any]:
        """Grade answer using hybrid approach with intelligent routing"""
        
        # Step 1: Always run rule-based grading for applicable skills
        rule_result = None
        if target_skill in self.rule_heavy_skills or self._contains_formulas(answer):
            rule_result = self.rule_grader.grade_answer(
                question, answer, target_skill, difficulty, expected_answer
            )
        
        # Step 2: Determine if LLM grading is needed
        needs_llm = self._needs_llm_grading(rule_result, target_skill, difficulty, answer)
        
        llm_result = None
        if needs_llm:
            llm_result = await self.llm_grader.grade_answer(
                question, answer, target_skill, difficulty, expected_answer,
                rule_results=rule_result.__dict__ if rule_result else None
            )
        
        # Step 3: Combine results intelligently
        hybrid_result = self._combine_results(rule_result, llm_result, target_skill, difficulty)
        
        # Step 4: Check for escalation needs
        if self._needs_escalation(hybrid_result, rule_result, llm_result):
            escalated_result = await self._escalate_grading(
                question, answer, target_skill, difficulty, rule_result, llm_result
            )
            return escalated_result
        
        return {
            "rule_score": rule_result.score * 100 if rule_result else None,
            "llm_score": llm_result.total_score if llm_result else None,
            "hybrid_score": hybrid_result.hybrid_score,
            "confidence": hybrid_result.confidence,
            "error_tags": hybrid_result.error_tags,
            "feedback": hybrid_result.feedback,
            "grading_method": hybrid_result.grading_method
        }
    
    def _needs_llm_grading(self, rule_result: Optional[RuleResult], target_skill: str,
                          difficulty: int, answer: str) -> bool:
        """Determine if LLM grading is necessary"""
        
        # Always use LLM for LLM-heavy skills
        if target_skill in self.llm_heavy_skills:
            return True
        
        # Use LLM for high difficulty questions
        if difficulty >= 3:
            return True
        
        # Use LLM if rule-based grading is uncertain
        if rule_result and rule_result.score < 0.3:  # Very low rule score
            return True
        
        # Use LLM for complex answers (long explanations)
        if len(answer.split()) > 50:
            return True
        
        # Use LLM if rule-based found errors but answer seems sophisticated
        if rule_result and rule_result.error_tags and len(answer) > 100:
            return True
        
        return False
    
    def _combine_results(self, rule_result: Optional[RuleResult],
                        llm_result: Optional[LLMGradingResult],
                        target_skill: str, difficulty: int) -> HybridGradingResult:
        """Intelligently combine rule and LLM results"""
        
        # Case 1: Only rule-based result
        if rule_result and not llm_result:
            return HybridGradingResult(
                rule_score=rule_result.score * 100,
                llm_score=None,
                hybrid_score=rule_result.score * 100,
                confidence=0.8 if rule_result.passed else 0.6,
                error_tags=rule_result.error_tags,
                feedback=rule_result.feedback,
                grading_method="rule_only"
            )
        
        # Case 2: Only LLM result
        if llm_result and not rule_result:
            return HybridGradingResult(
                rule_score=None,
                llm_score=llm_result.total_score,
                hybrid_score=llm_result.total_score,
                confidence=llm_result.confidence,
                error_tags=llm_result.error_tags,
                feedback=llm_result.feedback_short,
                grading_method="llm_only"
            )
        
        # Case 3: Both results available
        if rule_result and llm_result:
            rule_score = rule_result.score * 100
            llm_score = llm_result.total_score
            
            # Check for significant disagreement
            score_diff = abs(rule_score - llm_score)
            
            if score_diff <= self.disagreement_threshold:
                # Scores agree - use weighted average
                weight_rule = 0.7 if target_skill in self.rule_heavy_skills else 0.3
                weight_llm = 1 - weight_rule
                
                hybrid_score = (rule_score * weight_rule) + (llm_score * weight_llm)
                confidence = min(0.9, (rule_result.confidence if hasattr(rule_result, 'confidence') else 0.8) + llm_result.confidence) / 2
                
                combined_feedback = f"Rule-based: {rule_result.feedback}. LLM analysis: {llm_result.feedback_short}"
                combined_errors = list(set(rule_result.error_tags + llm_result.error_tags))
                
                return HybridGradingResult(
                    rule_score=rule_score,
                    llm_score=llm_score,
                    hybrid_score=hybrid_score,
                    confidence=confidence,
                    error_tags=combined_errors,
                    feedback=combined_feedback,
                    grading_method="hybrid"
                )
            
            else:
                # Significant disagreement - flag for potential escalation
                # For now, trust LLM more for complex reasoning, rules for syntax
                if target_skill in self.rule_heavy_skills and rule_result.passed:
                    primary_score = rule_score
                    primary_method = "rule_primary"
                else:
                    primary_score = llm_score
                    primary_method = "llm_primary"
                
                return HybridGradingResult(
                    rule_score=rule_score,
                    llm_score=llm_score,
                    hybrid_score=primary_score,
                    confidence=0.6,  # Lower confidence due to disagreement
                    error_tags=rule_result.error_tags + llm_result.error_tags + ["scoring_disagreement"],
                    feedback=f"Rule vs LLM disagreement ({score_diff:.1f} points). Primary: {primary_method}",
                    grading_method="disagreement"
                )
        
        # Fallback case
        return HybridGradingResult(
            rule_score=None,
            llm_score=None,
            hybrid_score=50,  # Conservative fallback
            confidence=0.3,
            error_tags=["grading_error"],
            feedback="Unable to grade properly",
            grading_method="fallback"
        )
    
    def _needs_escalation(self, hybrid_result: HybridGradingResult,
                         rule_result: Optional[RuleResult],
                         llm_result: Optional[LLMGradingResult]) -> bool:
        """Determine if grading needs escalation to premium model"""
        
        # Escalate if confidence is very low
        if hybrid_result.confidence < self.escalation_threshold:
            return True
        
        # Escalate if there's significant disagreement
        if "scoring_disagreement" in hybrid_result.error_tags:
            return True
        
        # Escalate if answer is very complex but scoring is unclear
        if hybrid_result.grading_method == "fallback":
            return True
        
        return False
    
    async def _escalate_grading(self, question: str, answer: str, target_skill: str,
                               difficulty: int, rule_result: Optional[RuleResult],
                               llm_result: Optional[LLMGradingResult]) -> Dict[str, Any]:
        """Escalate to premium model (Claude) for complex cases"""
        
        try:
            # Switch to Claude for escalation
            from llm.provider_abstraction import provider_manager
            original_provider = provider_manager.provider
            
            # Temporarily switch to Claude if available
            if original_provider != "claude":
                try:
                    provider_manager.switch_provider("claude", "claude-3-5-sonnet-20241022")
                    
                    # Re-grade with Claude
                    claude_result = await self.llm_grader.grade_answer(
                        question, answer, target_skill, difficulty,
                        rule_results=rule_result.__dict__ if rule_result else None
                    )
                    
                    return {
                        "rule_score": rule_result.score * 100 if rule_result else None,
                        "llm_score": claude_result.total_score,
                        "hybrid_score": claude_result.total_score,
                        "confidence": min(0.9, claude_result.confidence + 0.1),  # Boost confidence slightly
                        "error_tags": claude_result.error_tags,
                        "feedback": f"Escalated to premium model. {claude_result.feedback_short}",
                        "grading_method": "escalated_claude"
                    }
                    
                finally:
                    # Switch back to original provider
                    provider_manager.switch_provider(original_provider)
            
        except Exception as e:
            # Escalation failed - return best available result
            pass
        
        # Fallback to best available result
        if llm_result:
            return {
                "rule_score": rule_result.score * 100 if rule_result else None,
                "llm_score": llm_result.total_score,
                "hybrid_score": llm_result.total_score,
                "confidence": llm_result.confidence,
                "error_tags": llm_result.error_tags + ["escalation_failed"],
                "feedback": f"Escalation failed. {llm_result.feedback_short}",
                "grading_method": "escalation_failed"
            }
        
        return {
            "rule_score": rule_result.score * 100 if rule_result else None,
            "llm_score": None,
            "hybrid_score": rule_result.score * 100 if rule_result else 50,
            "confidence": 0.4,
            "error_tags": ["escalation_failed", "grading_incomplete"],
            "feedback": "Unable to complete escalated grading",
            "grading_method": "escalation_failed"
        }
    
    def _contains_formulas(self, answer: str) -> bool:
        """Check if answer contains Excel formulas"""
        formula_indicators = ["=", "SUM(", "VLOOKUP(", "IF(", "COUNTIF(", "INDEX(", "MATCH("]
        return any(indicator in answer.upper() for indicator in formula_indicators)
    
    async def grade_multiple_turns(self, turns_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Grade multiple interview turns efficiently"""
        results = []
        
        for turn_data in turns_data:
            result = await self.grade_answer(
                question=turn_data["question"],
                answer=turn_data["answer"],
                target_skill=turn_data["target_skill"],
                difficulty=turn_data["difficulty"],
                expected_answer=turn_data.get("expected_answer")
            )
            results.append(result)
        
        return results
    
    def calculate_overall_confidence(self, turn_results: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence across all turns"""
        confidences = [result.get("confidence", 0.5) for result in turn_results]
        if not confidences:
            return 0.5
        
        # Use weighted average with recent turns having higher weight
        weights = [min(1.0, 0.5 + i * 0.1) for i in range(len(confidences))]
        weighted_sum = sum(c * w for c, w in zip(confidences, weights))
        weight_sum = sum(weights)
        
        return weighted_sum / weight_sum if weight_sum > 0 else 0.5
