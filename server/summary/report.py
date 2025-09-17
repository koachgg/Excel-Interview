from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime
import statistics
import json

from storage.db import InterviewRepository, Turn, Interview
from llm.provider_abstraction import provider_manager

class ReportGenerator:
    """
    Generate comprehensive interview summary reports with scores,
    strengths, gaps, and actionable recommendations.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.repo = InterviewRepository(db)
        
        self.skill_categories = {
            "foundations": {
                "skills": ["references", "ranges", "formatting"],
                "weight": 0.15,
                "description": "Basic Excel fundamentals"
            },
            "functions": {
                "skills": ["if_functions", "vlookup", "index_match", "countif", "sumif", "text_functions", "date_functions"],
                "weight": 0.35,
                "description": "Excel formulas and functions"
            },
            "data_ops": {
                "skills": ["sorting", "filtering", "pivot_tables", "validation", "conditional_formatting"],
                "weight": 0.25,
                "description": "Data manipulation and organization"
            },
            "analysis": {
                "skills": ["whatif_analysis", "goal_seek", "statistics", "error_tracing"],
                "weight": 0.15,
                "description": "Data analysis and problem solving"
            },
            "charts": {
                "skills": ["charts"],
                "weight": 0.10,
                "description": "Data visualization"
            }
        }
        
        self.performance_bands = {
            (90, 100): {"level": "Expert", "description": "Exceptional Excel proficiency"},
            (80, 89): {"level": "Advanced", "description": "Strong Excel skills with minor gaps"},
            (70, 79): {"level": "Intermediate", "description": "Good foundation with areas to improve"},
            (60, 69): {"level": "Basic", "description": "Fundamental skills present, needs development"},
            (0, 59): {"level": "Novice", "description": "Requires significant Excel training"}
        }
    
    def generate_report(self, interview_id: int) -> Dict[str, Any]:
        """Generate comprehensive interview report"""
        interview = self.repo.get_interview(interview_id)
        if not interview:
            raise ValueError("Interview not found")
        
        # Calculate scores by skill and category
        scores_by_skill = self._calculate_skill_scores(interview)
        scores_by_category = self._calculate_category_scores(scores_by_skill)
        total_score = self._calculate_total_score(scores_by_category)
        
        # Analyze performance patterns
        strengths = self._identify_strengths(scores_by_skill, scores_by_category)
        gaps = self._identify_gaps(scores_by_skill, scores_by_category) 
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            total_score, scores_by_category, gaps, interview
        )
        
        # Extract meaningful transcript excerpts
        transcript_excerpts = self._extract_transcript_excerpts(interview)
        
        # Determine performance level
        performance_level = self._get_performance_level(total_score)
        
        # Update interview with final score
        self.repo.update_interview(interview_id, total_score=total_score, end_time=datetime.utcnow())
        
        return {
            "interview_id": interview_id,
            "candidate_name": interview.candidate_name,
            "total_score": round(total_score, 1),
            "performance_level": performance_level,
            "scores_by_skill": scores_by_skill,
            "scores_by_category": scores_by_category,
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations,
            "transcript_excerpts": transcript_excerpts,
            "interview_metadata": {
                "duration_minutes": self._calculate_duration(interview),
                "total_turns": len(interview.turns),
                "coverage_completeness": self._calculate_coverage_completeness(interview),
                "grading_confidence": self._calculate_avg_confidence(interview)
            }
        }
    
    def _calculate_skill_scores(self, interview: Interview) -> Dict[str, float]:
        """Calculate scores for each individual skill"""
        skill_scores = {}
        
        for turn in interview.turns:
            if turn.target_skill and turn.hybrid_score is not None:
                skill = turn.target_skill
                score = turn.hybrid_score
                
                # Take the best score for each skill (allows improvement)
                if skill in skill_scores:
                    skill_scores[skill] = max(skill_scores[skill], score)
                else:
                    skill_scores[skill] = score
        
        return skill_scores
    
    def _calculate_category_scores(self, scores_by_skill: Dict[str, float]) -> Dict[str, float]:
        """Calculate weighted scores for each skill category"""
        category_scores = {}
        
        for category, info in self.skill_categories.items():
            category_skills = info["skills"]
            relevant_scores = [scores_by_skill.get(skill, 0) for skill in category_skills 
                             if skill in scores_by_skill]
            
            if relevant_scores:
                # Use weighted average of actual scores
                category_scores[category] = statistics.mean(relevant_scores)
            else:
                # No coverage in this category
                category_scores[category] = 0
        
        return category_scores
    
    def _calculate_total_score(self, scores_by_category: Dict[str, float]) -> float:
        """Calculate weighted total score across all categories"""
        weighted_sum = 0
        total_weight = 0
        
        for category, score in scores_by_category.items():
            weight = self.skill_categories[category]["weight"]
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0
    
    def _identify_strengths(self, scores_by_skill: Dict[str, float], 
                          scores_by_category: Dict[str, float]) -> List[str]:
        """Identify candidate's strongest areas"""
        strengths = []
        
        # High-scoring categories
        for category, score in scores_by_category.items():
            if score >= 80:
                description = self.skill_categories[category]["description"]
                strengths.append(f"Strong {description.lower()} (Score: {score:.0f})")
        
        # Exceptional individual skills
        for skill, score in scores_by_skill.items():
            if score >= 85:
                skill_name = skill.replace("_", " ").title()
                strengths.append(f"Excellent {skill_name} knowledge (Score: {score:.0f})")
        
        # Pattern-based strengths
        if scores_by_category.get("functions", 0) >= 75:
            strengths.append("Demonstrates solid understanding of Excel formulas")
        
        if len([s for s in scores_by_skill.values() if s >= 70]) >= 5:
            strengths.append("Consistent performance across multiple skill areas")
        
        return strengths[:5]  # Limit to top 5 strengths
    
    def _identify_gaps(self, scores_by_skill: Dict[str, float], 
                      scores_by_category: Dict[str, float]) -> List[str]:
        """Identify areas needing improvement"""
        gaps = []
        
        # Low-scoring categories
        for category, score in scores_by_category.items():
            if score < 60:
                description = self.skill_categories[category]["description"]
                gaps.append(f"Needs development in {description.lower()} (Score: {score:.0f})")
        
        # Missing or weak individual skills
        critical_skills = ["vlookup", "if_functions", "pivot_tables"]
        for skill in critical_skills:
            score = scores_by_skill.get(skill, 0)
            if score < 65:
                skill_name = skill.replace("_", " ").title()
                if score == 0:
                    gaps.append(f"No demonstration of {skill_name} skills")
                else:
                    gaps.append(f"Weak {skill_name} understanding (Score: {score:.0f})")
        
        # Pattern-based gaps
        if scores_by_category.get("analysis", 0) < 50:
            gaps.append("Limited analytical and problem-solving capabilities")
        
        return gaps[:5]  # Limit to top 5 gaps
    
    def _generate_recommendations(self, total_score: float, scores_by_category: Dict[str, float],
                                gaps: List[str], interview: Interview) -> List[str]:
        """Generate actionable improvement recommendations"""
        recommendations = []
        
        # Score-based recommendations
        if total_score < 60:
            recommendations.append("Focus on Excel fundamentals: basic formulas, cell references, and simple functions")
            recommendations.append("Complete a comprehensive Excel basics course")
        
        elif total_score < 80:
            recommendations.append("Strengthen intermediate Excel skills through practice with real datasets")
            recommendations.append("Focus on areas with lowest scores for targeted improvement")
        
        # Category-specific recommendations
        if scores_by_category.get("functions", 0) < 70:
            recommendations.extend([
                "Practice VLOOKUP, INDEX/MATCH, and nested IF statements",
                "Learn COUNTIF, SUMIF, and other conditional functions"
            ])
        
        if scores_by_category.get("data_ops", 0) < 70:
            recommendations.extend([
                "Master pivot tables for data analysis and reporting",
                "Practice data validation and conditional formatting"
            ])
        
        if scores_by_category.get("analysis", 0) < 70:
            recommendations.append("Develop analytical thinking with what-if analysis and goal seek")
        
        # Performance-specific recommendations
        confidence_scores = [turn.confidence for turn in interview.turns 
                           if turn.confidence is not None]
        if confidence_scores and statistics.mean(confidence_scores) < 0.7:
            recommendations.append("Build confidence through regular practice with varied Excel scenarios")
        
        # Generic helpful recommendations
        recommendations.extend([
            "Create a personal Excel reference sheet with commonly used formulas",
            "Practice with real-world datasets relevant to your work domain"
        ])
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _extract_transcript_excerpts(self, interview: Interview) -> List[Dict[str, str]]:
        """Extract meaningful excerpts from the interview transcript"""
        excerpts = []
        
        # Find turns with interesting patterns
        for turn in interview.turns:
            if not turn.answer:
                continue
                
            excerpt_reasons = []
            
            # High-scoring answers
            if turn.hybrid_score and turn.hybrid_score >= 85:
                excerpt_reasons.append("Excellent response")
            
            # Answers with interesting errors
            if turn.error_tags and len(turn.error_tags) > 0:
                excerpt_reasons.append("Learning opportunity")
            
            # Long, detailed answers
            if len(turn.answer.split()) > 50:
                excerpt_reasons.append("Detailed explanation")
            
            # Answers containing formulas
            if "=" in turn.answer or any(func in turn.answer.upper() 
                                       for func in ["SUM", "VLOOKUP", "IF", "INDEX"]):
                excerpt_reasons.append("Technical demonstration")
            
            if excerpt_reasons and len(excerpts) < 4:
                excerpts.append({
                    "question": turn.question[:100] + "..." if len(turn.question) > 100 else turn.question,
                    "answer": turn.answer[:200] + "..." if len(turn.answer) > 200 else turn.answer,
                    "skill": turn.target_skill.replace("_", " ").title(),
                    "score": f"{turn.hybrid_score:.0f}" if turn.hybrid_score else "N/A",
                    "reason": ", ".join(excerpt_reasons)
                })
        
        return excerpts
    
    def _get_performance_level(self, total_score: float) -> Dict[str, str]:
        """Get performance level based on total score"""
        for (min_score, max_score), level_info in self.performance_bands.items():
            if min_score <= total_score <= max_score:
                return level_info
        
        return {"level": "Unknown", "description": "Unable to determine performance level"}
    
    def _calculate_duration(self, interview: Interview) -> int:
        """Calculate interview duration in minutes"""
        if interview.end_time and interview.start_time:
            duration = interview.end_time - interview.start_time
            return int(duration.total_seconds() / 60)
        return 0
    
    def _calculate_coverage_completeness(self, interview: Interview) -> float:
        """Calculate what percentage of skills were covered"""
        all_skills = []
        for category_info in self.skill_categories.values():
            all_skills.extend(category_info["skills"])
        
        covered_skills = set(turn.target_skill for turn in interview.turns if turn.target_skill)
        coverage = len(covered_skills) / len(all_skills) * 100
        return round(coverage, 1)
    
    def _calculate_avg_confidence(self, interview: Interview) -> float:
        """Calculate average grading confidence"""
        confidences = [turn.confidence for turn in interview.turns 
                      if turn.confidence is not None]
        if confidences:
            return round(statistics.mean(confidences) * 100, 1)
        return 50.0
    
    async def generate_detailed_analysis(self, interview_id: int) -> str:
        """Generate detailed narrative analysis using LLM"""
        basic_report = self.generate_report(interview_id)
        
        analysis_prompt = f"""Generate a detailed narrative analysis of this Excel interview performance:

CANDIDATE: {basic_report.get('candidate_name', 'Anonymous')}
TOTAL SCORE: {basic_report['total_score']}/100
PERFORMANCE LEVEL: {basic_report['performance_level']['level']}

CATEGORY SCORES:
{json.dumps(basic_report['scores_by_category'], indent=2)}

STRENGTHS:
{chr(10).join(f"- {s}" for s in basic_report['strengths'])}

GAPS:
{chr(10).join(f"- {g}" for g in basic_report['gaps'])}

SAMPLE RESPONSES:
{json.dumps(basic_report['transcript_excerpts'], indent=2)}

Write a comprehensive 300-400 word analysis covering:
1. Overall performance assessment
2. Technical skill evaluation
3. Reasoning and problem-solving approach
4. Readiness for Excel-dependent roles
5. Specific next steps for improvement

Write in professional but encouraging tone suitable for candidate feedback."""
        
        try:
            detailed_analysis = await provider_manager.generate_summary(analysis_prompt, temperature=0.4)
            return detailed_analysis
        except Exception as e:
            return f"Unable to generate detailed analysis due to: {str(e)}"
