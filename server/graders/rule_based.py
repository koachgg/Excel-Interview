import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class RuleResult:
    passed: bool
    score: float  # 0.0 to 1.0
    error_tags: List[str]
    feedback: str

class RuleBasedGrader:
    """
    Rule-based grader for Excel formulas and concepts.
    Validates specific patterns, syntax, and common errors.
    """
    
    def __init__(self):
        self.formula_patterns = {
            "sum": r"=?\s*SUM\s*\([^)]+\)",
            "vlookup": r"=?\s*VLOOKUP\s*\([^,]+,[^,]+,[^,]+,.*\)",
            "if": r"=?\s*IF\s*\([^,]+,[^,]+.*\)",
            "countif": r"=?\s*COUNTIF\s*\([^,]+,[^)]+\)",
            "index_match": r"=?\s*INDEX\s*\([^,]+,\s*MATCH\s*\([^)]+\)\s*\)",
            "absolute_ref": r"\$[A-Z]+\$[0-9]+",
            "relative_ref": r"[A-Z]+[0-9]+",
            "range": r"[A-Z]+[0-9]+:[A-Z]+[0-9]+"
        }
        
        self.common_errors = {
            "circular_reference": r"(?i)circular",
            "div_zero": r"#DIV/0!",
            "name_error": r"#NAME\?",
            "ref_error": r"#REF!",
            "value_error": r"#VALUE!",
            "na_error": r"#N/A"
        }
    
    def grade_answer(self, question: str, answer: str, target_skill: str, 
                    difficulty: int, expected_answer: str = None) -> RuleResult:
        """Grade an answer using rule-based validation"""
        
        if target_skill == "references":
            return self._grade_references(question, answer, difficulty)
        elif target_skill == "vlookup":
            return self._grade_vlookup(question, answer, difficulty)
        elif target_skill == "if_functions":
            return self._grade_if_functions(question, answer, difficulty)
        elif target_skill == "basic_formulas":
            return self._grade_basic_formulas(question, answer, difficulty)
        elif target_skill == "pivot_tables":
            return self._grade_pivot_tables(question, answer, difficulty)
        elif target_skill == "case_analysis":
            return self._grade_case_analysis(question, answer, difficulty)
        else:
            return self._grade_generic(question, answer, target_skill, difficulty)
    
    def _grade_references(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade questions about cell references"""
        answer_lower = answer.lower()
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        # Check for understanding of absolute vs relative references
        if "absolute" in question.lower() or "$" in question:
            if re.search(self.formula_patterns["absolute_ref"], answer):
                score += 0.5
                feedback_parts.append("Correctly identified absolute reference syntax")
            else:
                error_tags.append("missing_absolute_reference")
                feedback_parts.append("Missing absolute reference syntax ($A$1)")
        
        # Check for relative reference understanding  
        if "relative" in question.lower() or re.search(r"reference.*change|move", question.lower()):
            if re.search(self.formula_patterns["relative_ref"], answer):
                score += 0.3
                feedback_parts.append("Showed understanding of relative references")
            else:
                error_tags.append("missing_relative_concept")
        
        # Check for range syntax
        if re.search(self.formula_patterns["range"], answer):
            score += 0.2
            feedback_parts.append("Used proper range syntax")
        
        # Bonus points for explanation
        if len(answer.split()) > 10 and any(word in answer_lower for word in ["because", "when", "will", "changes"]):
            score += 0.2
            feedback_parts.append("Provided good explanation of concepts")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_vlookup(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade VLOOKUP related answers"""
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        # Check for VLOOKUP syntax
        vlookup_match = re.search(self.formula_patterns["vlookup"], answer, re.IGNORECASE)
        if vlookup_match:
            score += 0.4
            feedback_parts.append("Used VLOOKUP function")
            
            # Parse VLOOKUP parameters
            vlookup_content = vlookup_match.group(0)
            params = self._extract_function_params(vlookup_content)
            
            if len(params) >= 3:
                score += 0.2
                feedback_parts.append("Included required parameters")
                
                # Check for proper table array (range or reference)
                if re.search(self.formula_patterns["range"], params[1]) or ":" in params[1]:
                    score += 0.1
                else:
                    error_tags.append("invalid_table_array")
                
                # Check column index (should be number)
                if params[2].strip().isdigit():
                    score += 0.1
                else:
                    error_tags.append("invalid_column_index")
                
                # Check for exact/approximate match parameter
                if len(params) >= 4:
                    match_param = params[3].lower().strip()
                    if match_param in ["false", "0", "true", "1"]:
                        score += 0.1
                        feedback_parts.append("Specified lookup match type")
            else:
                error_tags.append("incomplete_vlookup_params")
        
        else:
            # Check if they mentioned alternative approaches
            if any(alt in answer.lower() for alt in ["index", "match", "xlookup", "filter"]):
                score += 0.3
                feedback_parts.append("Mentioned alternative lookup methods")
            else:
                error_tags.append("no_lookup_function")
        
        # Check for common errors
        if "approximate" in question.lower() and difficulty >= 3:
            if "approximate" in answer.lower() or "true" in answer.lower() or "1" in answer:
                score += 0.1
            else:
                error_tags.append("missing_approximate_match_discussion")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_if_functions(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade IF function related answers"""
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        # Check for IF function syntax
        if_match = re.search(self.formula_patterns["if"], answer, re.IGNORECASE)
        if if_match:
            score += 0.3
            feedback_parts.append("Used IF function")
            
            # Check for proper IF structure
            if_content = if_match.group(0)
            params = self._extract_function_params(if_content)
            
            if len(params) >= 2:
                score += 0.2
                feedback_parts.append("Included condition and result")
                
                # Check for comparison operators
                if any(op in params[0] for op in [">=", "<=", ">", "<", "=", "<>"]):
                    score += 0.1
                    feedback_parts.append("Used comparison operator")
                
                # For difficulty 3+, check for nested IFs
                if difficulty >= 3:
                    nested_ifs = len(re.findall(r"IF\s*\(", answer, re.IGNORECASE))
                    if nested_ifs > 1:
                        score += 0.2
                        feedback_parts.append("Used nested IF functions")
                    elif "nested" in question.lower():
                        error_tags.append("missing_nested_if")
        else:
            error_tags.append("no_if_function")
        
        # Check for logical operators
        if difficulty >= 3 and any(op in answer.upper() for op in ["AND", "OR"]):
            score += 0.1
            feedback_parts.append("Used logical operators")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_basic_formulas(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade basic formula questions"""
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        # Check for formula syntax (starts with =)
        if answer.strip().startswith("=") or "=" in answer:
            score += 0.2
            feedback_parts.append("Used formula syntax")
        
        # Check for SUM function if question involves summing
        if "sum" in question.lower():
            if re.search(self.formula_patterns["sum"], answer, re.IGNORECASE):
                score += 0.4
                feedback_parts.append("Used SUM function correctly")
            else:
                error_tags.append("missing_sum_function")
        
        # Check for proper range syntax
        if re.search(self.formula_patterns["range"], answer):
            score += 0.2
            feedback_parts.append("Used proper range notation")
        
        # Check for understanding of basic concepts
        conceptual_words = ["formula", "function", "cell", "range", "reference"]
        concept_count = sum(1 for word in conceptual_words if word in answer.lower())
        if concept_count >= 2:
            score += 0.2
            feedback_parts.append("Demonstrated understanding of Excel concepts")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_pivot_tables(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade pivot table related answers"""
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        pivot_keywords = ["pivot", "pivot table", "summarize", "group", "aggregate"]
        if any(keyword in answer.lower() for keyword in pivot_keywords):
            score += 0.3
            feedback_parts.append("Mentioned pivot tables")
        
        # Check for understanding of pivot table components
        components = ["rows", "columns", "values", "filters", "fields"]
        component_count = sum(1 for comp in components if comp in answer.lower())
        score += min(0.3, component_count * 0.1)
        
        if component_count >= 2:
            feedback_parts.append("Understood pivot table structure")
        
        # Check for steps/process
        step_indicators = ["first", "then", "next", "step", "insert", "create", "drag", "drop"]
        if any(indicator in answer.lower() for indicator in step_indicators):
            score += 0.2
            feedback_parts.append("Provided step-by-step approach")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_case_analysis(self, question: str, answer: str, difficulty: int) -> RuleResult:
        """Grade case study analysis"""
        error_tags = []
        score = 0.0
        feedback_parts = []
        
        # Look for specific formulas mentioned in the case
        formula_functions = ["AVERAGEIF", "COUNTIF", "INDEX", "MATCH", "VLOOKUP", "DATEDIF", "TODAY"]
        formula_count = sum(1 for func in formula_functions if func.upper() in answer.upper())
        
        score += min(0.4, formula_count * 0.1)
        if formula_count >= 2:
            feedback_parts.append(f"Used {formula_count} relevant functions")
        
        # Check for range references (important in case studies)
        range_count = len(re.findall(self.formula_patterns["range"], answer))
        if range_count >= 2:
            score += 0.2
            feedback_parts.append("Used appropriate data ranges")
        
        # Check for structured approach (numbered responses)
        if re.search(r"\d+\.", answer):
            score += 0.2
            feedback_parts.append("Provided structured responses")
        
        # Check for explanation/reasoning
        explanation_words = ["because", "since", "this will", "to calculate", "in order to"]
        if any(word in answer.lower() for word in explanation_words):
            score += 0.2
            feedback_parts.append("Provided reasoning for approach")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(score, 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _grade_generic(self, question: str, answer: str, target_skill: str, difficulty: int) -> RuleResult:
        """Generic grading for skills not specifically handled"""
        error_tags = []
        score = 0.5  # Default middle score for generic grading
        feedback_parts = ["Used generic rule-based evaluation"]
        
        # Basic checks
        if len(answer.strip()) < 10:
            score -= 0.2
            error_tags.append("answer_too_short")
        
        if len(answer.split()) > 20:
            score += 0.1
            feedback_parts.append("Provided detailed response")
        
        return RuleResult(
            passed=score >= 0.6,
            score=min(max(score, 0.0), 1.0),
            error_tags=error_tags,
            feedback="; ".join(feedback_parts)
        )
    
    def _extract_function_params(self, function_str: str) -> List[str]:
        """Extract parameters from a function string"""
        # Find content between parentheses
        match = re.search(r"\(([^)]+)\)", function_str)
        if match:
            params_str = match.group(1)
            # Split by comma, but be careful of nested functions
            params = []
            current_param = ""
            paren_depth = 0
            
            for char in params_str:
                if char == '(':
                    paren_depth += 1
                elif char == ')':
                    paren_depth -= 1
                elif char == ',' and paren_depth == 0:
                    params.append(current_param.strip())
                    current_param = ""
                    continue
                
                current_param += char
            
            if current_param.strip():
                params.append(current_param.strip())
            
            return params
        return []
