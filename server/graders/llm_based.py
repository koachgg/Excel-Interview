from typing import Dict, Any, List, Optional
import json
from dataclasses import dataclass
import asyncio

from llm.provider_abstraction import provider_manager

@dataclass 
class LLMGradingResult:
    scores_by_dimension: Dict[str, float]
    total_score: float  # 0-100
    error_tags: List[str]
    confidence: float  # 0-1
    feedback_short: str

class LLMBasedGrader:
    """
    LLM-based grader that uses AI models to evaluate Excel answers
    with nuanced understanding and contextual scoring.
    """
    
    def __init__(self):
        self.grading_dimensions = [
            "technical_accuracy",
            "completeness", 
            "clarity",
            "efficiency",
            "best_practices"
        ]
        
        self.skill_rubrics = {
            "vlookup": {
                "technical_accuracy": "Correct VLOOKUP syntax and parameters",
                "completeness": "All required parameters included",
                "efficiency": "Appropriate use vs alternatives",
                "best_practices": "Proper error handling and match type"
            },
            "if_functions": {
                "technical_accuracy": "Correct IF syntax and logical operators",
                "completeness": "Handles all conditions mentioned",
                "efficiency": "Optimal nesting/structure",
                "best_practices": "Readable formula construction"
            },
            "pivot_tables": {
                "technical_accuracy": "Correct understanding of pivot components",
                "completeness": "All required steps mentioned", 
                "clarity": "Clear explanation of process",
                "efficiency": "Efficient data organization approach"
            }
        }
    
    async def grade_answer(self, question: str, answer: str, target_skill: str,
                          difficulty: int, expected_answer: str = None,
                          rule_results: Dict = None) -> LLMGradingResult:
        """Grade answer using LLM with structured evaluation"""
        
        # Build comprehensive grading prompt
        prompt = self._build_grading_prompt(
            question, answer, target_skill, difficulty, expected_answer, rule_results
        )
        
        try:
            # Generate grading response with low temperature for consistency
            response = await provider_manager.grade_answer(prompt, temperature=0.1)
            
            # Parse structured response
            grading_result = json.loads(response)
            
            return LLMGradingResult(
                scores_by_dimension=grading_result.get("scores_by_dimension", {}),
                total_score=grading_result.get("total_score", 0),
                error_tags=grading_result.get("error_tags", []),
                confidence=grading_result.get("confidence", 0.5),
                feedback_short=grading_result.get("feedback_short", "")
            )
            
        except Exception as e:
            # Fallback scoring
            return self._fallback_grading(answer, target_skill, str(e))
    
    def _build_grading_prompt(self, question: str, answer: str, target_skill: str,
                            difficulty: int, expected_answer: str = None,
                            rule_results: Dict = None) -> str:
        """Build comprehensive grading prompt"""
        
        rubric = self.skill_rubrics.get(target_skill, {
            "technical_accuracy": "Correctness of Excel knowledge",
            "completeness": "Addresses all parts of question",
            "clarity": "Clear explanation and reasoning"
        })
        
        prompt = f"""You are an expert Excel interviewer evaluating a candidate's response. Please grade this answer comprehensively.

QUESTION: {question}

CANDIDATE ANSWER: {answer}

TARGET SKILL: {target_skill}
DIFFICULTY LEVEL: {difficulty}/3

GRADING RUBRIC:
{json.dumps(rubric, indent=2)}
"""
        
        if expected_answer:
            prompt += f"\n\nEXPECTED APPROACH: {expected_answer}"
        
        if rule_results:
            prompt += f"\n\nRULE-BASED ANALYSIS: {json.dumps(rule_results, indent=2)}"
        
        prompt += """

GRADING INSTRUCTIONS:
- Score each dimension 0-100 based on quality and correctness
- Consider the difficulty level (higher difficulty = more stringent grading)
- Identify specific error types and areas for improvement
- Be fair but thorough - Excel interviews require precision
- Consider both technical correctness and practical understanding

Respond with JSON in this exact format:
{
    "scores_by_dimension": {
        "technical_accuracy": 85,
        "completeness": 75,
        "clarity": 90,
        "efficiency": 80,
        "best_practices": 70
    },
    "total_score": 80,
    "error_tags": ["minor_syntax_error", "missing_error_handling"],
    "confidence": 0.85,
    "feedback_short": "Good understanding of VLOOKUP basics. Consider using IFERROR for better error handling. Syntax is correct but could explain approximate vs exact match better."
}"""
        
        return prompt
    
    async def grade_batch(self, answers: List[Dict[str, Any]]) -> List[LLMGradingResult]:
        """Grade multiple answers in batch for efficiency"""
        tasks = []
        for answer_data in answers:
            task = self.grade_answer(
                question=answer_data["question"],
                answer=answer_data["answer"], 
                target_skill=answer_data["target_skill"],
                difficulty=answer_data["difficulty"],
                expected_answer=answer_data.get("expected_answer"),
                rule_results=answer_data.get("rule_results")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create fallback result
                processed_results.append(
                    self._fallback_grading(
                        answers[i]["answer"], 
                        answers[i]["target_skill"],
                        str(result)
                    )
                )
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def calibrate_grading(self, sample_answers: List[Dict[str, Any]], 
                               expected_scores: List[float]) -> Dict[str, Any]:
        """Calibrate grading against known good/bad answers"""
        results = await self.grade_batch(sample_answers)
        
        # Compare predicted vs expected scores
        differences = []
        for result, expected in zip(results, expected_scores):
            diff = abs(result.total_score - expected)
            differences.append(diff)
        
        avg_error = sum(differences) / len(differences)
        accuracy = sum(1 for diff in differences if diff <= 10) / len(differences)
        
        return {
            "average_error": avg_error,
            "accuracy_within_10_points": accuracy,
            "sample_size": len(sample_answers),
            "calibration_quality": "good" if accuracy >= 0.8 else "needs_adjustment"
        }
    
    def _fallback_grading(self, answer: str, target_skill: str, error: str) -> LLMGradingResult:
        """Provide fallback grading when LLM fails"""
        base_score = 60  # Conservative baseline
        
        # Simple heuristics
        if len(answer.strip()) < 20:
            base_score -= 20
        
        if "=" in answer:  # Has formula
            base_score += 10
        
        if len(answer.split()) > 50:  # Detailed answer
            base_score += 10
        
        return LLMGradingResult(
            scores_by_dimension={
                "technical_accuracy": base_score,
                "completeness": base_score - 5,
                "clarity": base_score + 5
            },
            total_score=base_score,
            error_tags=["llm_grading_failed"],
            confidence=0.3,
            feedback_short=f"Fallback grading used due to error: {error[:100]}"
        )
    
    async def explain_score(self, question: str, answer: str, score: float,
                           target_skill: str) -> str:
        """Generate detailed explanation for why a score was given"""
        
        prompt = f"""Explain why this Excel interview answer received a score of {score}/100.

QUESTION: {question}
ANSWER: {answer}
SKILL: {target_skill}
SCORE: {score}/100

Provide a detailed but concise explanation covering:
1. What the candidate did well
2. What could be improved
3. Specific suggestions for better answers
4. How this relates to practical Excel usage

Keep explanation under 200 words."""
        
        try:
            return await provider_manager.generate_summary(prompt, temperature=0.3)
        except Exception:
            return f"Score of {score}/100 reflects the overall quality and correctness of the response for {target_skill} skills."
