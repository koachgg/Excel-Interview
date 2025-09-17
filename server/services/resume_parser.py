"""
Resume parsing and skill extraction service for personalized interviews.
"""

import re
import io
from typing import Dict, List, Set, Optional
from pathlib import Path

try:
    import PyPDF2
    import docx
except ImportError:
    print("Warning: Resume parsing libraries not installed. Run: pip install PyPDF2 python-docx")


class ResumeParser:
    """Parse resumes and extract Excel-relevant skills and experience."""
    
    # Excel skills keywords for extraction
    EXCEL_SKILLS = {
        'basic': [
            'excel', 'spreadsheet', 'microsoft excel', 'ms excel',
            'data entry', 'basic formulas', 'sorting', 'filtering'
        ],
        'intermediate': [
            'vlookup', 'hlookup', 'pivot table', 'pivot tables', 'charts',
            'conditional formatting', 'data validation', 'sumif', 'countif',
            'index', 'match', 'concatenate', 'text functions'
        ],
        'advanced': [
            'macro', 'vba', 'power query', 'power pivot', 'solver',
            'data analysis', 'statistical analysis', 'advanced formulas',
            'array formulas', 'dashboard', 'automation', 'xlookup'
        ],
        'expert': [
            'vba programming', 'excel automation', 'advanced macros',
            'power bi integration', 'sql queries', 'data modeling',
            'financial modeling', 'monte carlo', 'scenario analysis'
        ]
    }
    
    EXPERIENCE_INDICATORS = [
        'years', 'year', 'months', 'month', 'experience', 'proficient',
        'expert', 'advanced', 'intermediate', 'beginner', 'skilled'
    ]
    
    def __init__(self):
        self.skills_found = set()
        self.experience_level = 'beginner'
        self.domain_experience = []
        
    def parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF resume."""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
        except Exception as e:
            print(f"Error parsing PDF: {e}")
            return ""
    
    def parse_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX resume."""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return ""
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text based on file type."""
        if filename.lower().endswith('.pdf'):
            return self.parse_pdf(file_content)
        elif filename.lower().endswith(('.docx', '.doc')):
            return self.parse_docx(file_content)
        else:
            # Assume text file
            return file_content.decode('utf-8', errors='ignore')
    
    def analyze_skills(self, text: str) -> Dict[str, List[str]]:
        """Analyze text and extract Excel skills by category."""
        text_lower = text.lower()
        skills_by_level = {
            'basic': [],
            'intermediate': [],
            'advanced': [],
            'expert': []
        }
        
        for level, skills in self.EXCEL_SKILLS.items():
            for skill in skills:
                if skill in text_lower:
                    skills_by_level[level].append(skill)
                    self.skills_found.add(skill)
        
        return skills_by_level
    
    def extract_experience_level(self, text: str) -> str:
        """Determine experience level based on context."""
        text_lower = text.lower()
        
        # Look for explicit experience mentions
        experience_patterns = [
            r'(\d+)\s*\+?\s*years?\s+.*excel',
            r'excel.*(\d+)\s*\+?\s*years?',
            r'(\d+)\s*years?\s+.*spreadsheet',
            r'expert.*excel',
            r'advanced.*excel',
            r'proficient.*excel'
        ]
        
        max_years = 0
        for pattern in experience_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if isinstance(match, str) and match.isdigit():
                    max_years = max(max_years, int(match))
        
        # Determine level based on skills and experience
        skill_levels = self.analyze_skills(text)
        
        if skill_levels['expert'] or max_years >= 5:
            return 'expert'
        elif skill_levels['advanced'] or max_years >= 3:
            return 'advanced'
        elif skill_levels['intermediate'] or max_years >= 1:
            return 'intermediate'
        else:
            return 'beginner'
    
    def extract_domain_experience(self, text: str) -> List[str]:
        """Extract domain/industry experience relevant to Excel use cases."""
        domains = {
            'finance': ['finance', 'financial', 'accounting', 'budget', 'investment', 'banking'],
            'analytics': ['analytics', 'analysis', 'data science', 'statistics', 'reporting'],
            'operations': ['operations', 'supply chain', 'inventory', 'logistics', 'procurement'],
            'sales': ['sales', 'marketing', 'crm', 'revenue', 'forecasting'],
            'hr': ['hr', 'human resources', 'payroll', 'recruitment', 'workforce']
        }
        
        text_lower = text.lower()
        found_domains = []
        
        for domain, keywords in domains.items():
            if any(keyword in text_lower for keyword in keywords):
                found_domains.append(domain)
        
        return found_domains
    
    def parse_resume(self, file_content: bytes, filename: str) -> Dict:
        """Main method to parse resume and extract relevant information."""
        # Extract text
        text = self.extract_text(file_content, filename)
        
        if not text.strip():
            return {
                'error': 'Could not extract text from resume',
                'skills': {},
                'experience_level': 'beginner',
                'domains': [],
                'personalization_data': {}
            }
        
        # Analyze content
        skills_by_level = self.analyze_skills(text)
        experience_level = self.extract_experience_level(text)
        domains = self.extract_domain_experience(text)
        
        # Generate personalization data
        personalization_data = {
            'has_excel_experience': bool(self.skills_found),
            'claimed_skills': list(self.skills_found),
            'skill_categories': [level for level, skills in skills_by_level.items() if skills],
            'focus_areas': domains,
            'suggested_difficulty': experience_level
        }
        
        return {
            'skills': skills_by_level,
            'experience_level': experience_level,
            'domains': domains,
            'personalization_data': personalization_data,
            'raw_text_length': len(text),
            'skills_count': len(self.skills_found)
        }


class PersonalizedQuestionGenerator:
    """Generate personalized interview questions based on resume analysis."""
    
    def __init__(self):
        self.base_questions = {
            'beginner': [
                "Can you explain what Excel is and how you've used it?",
                "What basic Excel functions are you familiar with?",
                "How would you create a simple chart in Excel?",
                "Explain the difference between a row and a column.",
            ],
            'intermediate': [
                "How would you use VLOOKUP to find data in a large dataset?",
                "Explain how to create and use a pivot table.",
                "What is conditional formatting and when would you use it?",
                "How do you handle duplicate data in Excel?",
            ],
            'advanced': [
                "Explain the difference between VLOOKUP and INDEX-MATCH.",
                "How would you automate repetitive tasks in Excel?",
                "Describe your approach to building an Excel dashboard.",
                "What advanced Excel features have you used for data analysis?",
            ],
            'expert': [
                "How do you optimize Excel performance with large datasets?",
                "Explain your experience with VBA and Excel automation.",
                "How do you integrate Excel with other data sources?",
                "Describe a complex Excel model you've built.",
            ]
        }
        
        self.domain_questions = {
            'finance': [
                "How have you used Excel for financial modeling?",
                "Explain how you would build a budget tracking system in Excel.",
                "What Excel functions are most useful for financial calculations?",
            ],
            'analytics': [
                "How do you use Excel for data analysis and reporting?",
                "What statistical functions in Excel do you use regularly?",
                "How do you visualize data trends in Excel?",
            ],
            'operations': [
                "How have you used Excel for inventory management?",
                "Explain how you would track operational metrics in Excel.",
                "What Excel features help with process optimization?",
            ]
        }
    
    def generate_personalized_questions(self, resume_data: Dict) -> List[Dict]:
        """Generate questions tailored to the candidate's background."""
        questions = []
        
        # Base questions for their level
        level = resume_data.get('experience_level', 'beginner')
        base_qs = self.base_questions.get(level, self.base_questions['beginner'])
        
        for i, question in enumerate(base_qs[:3]):  # Limit to 3 base questions
            questions.append({
                'id': f'base_{i}',
                'question': question,
                'category': 'general',
                'difficulty': level,
                'source': 'base_level'
            })
        
        # Domain-specific questions
        for domain in resume_data.get('domains', []):
            domain_qs = self.domain_questions.get(domain, [])
            for i, question in enumerate(domain_qs[:2]):  # Limit to 2 per domain
                questions.append({
                    'id': f'{domain}_{i}',
                    'question': question,
                    'category': domain,
                    'difficulty': level,
                    'source': 'domain_specific'
                })
        
        # Skill-specific follow-ups
        claimed_skills = resume_data.get('personalization_data', {}).get('claimed_skills', [])
        if 'vlookup' in claimed_skills:
            questions.append({
                'id': 'vlookup_specific',
                'question': "I see you mentioned VLOOKUP on your resume. Can you walk me through a specific example of how you used it?",
                'category': 'skill_verification',
                'difficulty': level,
                'source': 'resume_claim'
            })
        
        if 'pivot table' in claimed_skills or 'pivot tables' in claimed_skills:
            questions.append({
                'id': 'pivot_specific',
                'question': "You mentioned pivot tables - can you describe a complex pivot table analysis you've performed?",
                'category': 'skill_verification',
                'difficulty': level,
                'source': 'resume_claim'
            })
        
        return questions
