#!/usr/bin/env python3
"""
Comprehensive Excel Interview Database Seeder
Seeds the database with rubrics and questions for conducting Excel skill interviews.
"""

import sys
import os

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))

from storage.db import create_tables, get_db, RubricRepository, QuestionRepository
from storage.models import Base

def seed_rubrics(db):
    """Seed the database with comprehensive Excel skill rubrics"""
    repo = RubricRepository(db)
    
    # Foundations rubrics (Difficulty Tier 1)
    foundations_rubrics = [
        {
            "skill_name": "references",
            "category": "foundations", 
            "difficulty_tier": 1,
            "version": "1.0",
            "rubric_data": {
                "description": "Cell references and addressing fundamentals",
                "scoring_criteria": {
                    "novice": "No understanding of reference types or syntax",
                    "basic": "Knows A1 notation but confused about relative/absolute",
                    "proficient": "Clearly explains $A$1 vs A1 behavior when copying",
                    "advanced": "Uses mixed references ($A1, A$1) strategically"
                },
                "key_concepts": ["Relative references", "Absolute references", "Mixed references", "Copy behavior"],
                "common_errors": ["Confusing $ placement", "Not understanding copy behavior"]
            }
        },
        {
            "skill_name": "ranges",
            "category": "foundations",
            "difficulty_tier": 1, 
            "version": "1.0",
            "rubric_data": {
                "description": "Range selection and specification",
                "scoring_criteria": {
                    "novice": "Cannot specify ranges correctly",
                    "basic": "Uses basic range notation (A1:A10)",
                    "proficient": "Comfortable with various range types and selection methods",
                    "advanced": "Uses dynamic ranges and named ranges effectively"
                },
                "key_concepts": ["Continuous ranges", "Non-contiguous ranges", "Named ranges", "Dynamic ranges"]
            }
        },
        {
            "skill_name": "basic_formulas",
            "category": "foundations",
            "difficulty_tier": 1,
            "version": "1.0",
            "rubric_data": {
                "description": "Basic mathematical operations and formula construction",
                "scoring_criteria": {
                    "novice": "Cannot create basic formulas",
                    "basic": "Creates simple arithmetic formulas (+, -, *, /)",
                    "proficient": "Uses SUM, AVERAGE, COUNT functions confidently",
                    "advanced": "Combines multiple functions and understands precedence"
                },
                "key_concepts": ["Mathematical operators", "Function syntax", "Order of operations"]
            }
        }
    ]
    
    # Functions rubrics (Difficulty Tier 2-3)
    functions_rubrics = [
        {
            "skill_name": "if_functions",
            "category": "functions",
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Conditional logic with IF statements",
                "scoring_criteria": {
                    "novice": "Cannot construct IF statements",
                    "basic": "Creates simple IF with single condition",
                    "proficient": "Uses nested IF and logical operators (AND, OR)",
                    "advanced": "Efficiently handles complex multi-condition logic"
                },
                "key_concepts": ["IF syntax", "Nested IF", "Logical operators", "Error handling"],
                "syntax_requirements": "=IF(condition, value_if_true, value_if_false)"
            }
        },
        {
            "skill_name": "vlookup",
            "category": "functions",
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Data lookup using VLOOKUP function",
                "scoring_criteria": {
                    "novice": "No experience with lookup functions",
                    "basic": "Understands VLOOKUP concept, needs help with syntax",
                    "proficient": "Writes correct VLOOKUP with proper parameters",
                    "advanced": "Handles errors, knows exact vs approximate match nuances"
                },
                "key_concepts": ["Lookup value", "Table array", "Column index", "Range lookup"],
                "syntax_requirements": "=VLOOKUP(lookup_value, table_array, col_index, [range_lookup])",
                "common_errors": ["Wrong column index", "#N/A errors", "Incorrect table range"]
            }
        },
        {
            "skill_name": "index_match",
            "category": "functions",
            "difficulty_tier": 3,
            "version": "1.0",
            "rubric_data": {
                "description": "Advanced lookup using INDEX/MATCH combination",
                "scoring_criteria": {
                    "novice": "Unfamiliar with INDEX or MATCH functions",
                    "basic": "Understands INDEX and MATCH separately",
                    "proficient": "Can combine INDEX/MATCH for basic lookups",
                    "advanced": "Prefers INDEX/MATCH over VLOOKUP, understands advantages"
                },
                "key_concepts": ["INDEX function", "MATCH function", "Flexible lookup", "Two-way lookups"]
            }
        },
        {
            "skill_name": "countif",
            "category": "functions",
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Conditional counting functions",
                "scoring_criteria": {
                    "novice": "Uses basic COUNT function only",
                    "basic": "Can use COUNTIF with simple text criteria",
                    "proficient": "Uses wildcards and numeric criteria effectively",
                    "advanced": "Uses COUNTIFS for multiple criteria analysis"
                },
                "key_concepts": ["Criteria syntax", "Wildcards", "Multiple conditions", "COUNTIFS"]
            }
        },
        {
            "skill_name": "sumif",
            "category": "functions", 
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Conditional summation functions",
                "criteria": {
                    "basic": "Can use SUMIF with simple criteria",
                    "proficient": "Uses SUMIFS for multiple conditions", 
                    "advanced": "Combines with other functions for reporting"
                }
            }
        }
    ]
    
    # Data operations rubrics
    data_ops_rubrics = [
        {
            "skill_name": "pivot_tables",
            "category": "data_ops",
            "difficulty_tier": 2,
            "rubric_data": {
                "description": "Creating and configuring pivot tables",
                "criteria": {
                    "basic": "Understands pivot table concept and components",
                    "proficient": "Can create basic pivot tables with proper field placement",
                    "advanced": "Uses calculated fields, slicers, and advanced pivot features"
                },
                "key_concepts": ["rows", "columns", "values", "filters"]
            }
        },
        {
            "skill_name": "sorting",
            "category": "data_ops",
            "difficulty_tier": 1,
            "rubric_data": {
                "description": "Sorting data and maintaining data integrity",
                "criteria": {
                    "basic": "Can perform simple sorts",
                    "proficient": "Uses multi-level sorting and custom sort orders",
                    "advanced": "Understands data integrity issues with sorting"
                }
            }
        },
        {
            "skill_name": "filtering",
            "category": "data_ops",
            "difficulty_tier": 2,
            "rubric_data": {
                "description": "Filtering and data selection",
                "criteria": {
                    "basic": "Can apply AutoFilter to columns",
                    "proficient": "Uses advanced filters and custom criteria",
                    "advanced": "Combines filtering with other analysis techniques"
                }
            }
        }
    ]
    
    # Analysis rubrics
    analysis_rubrics = [
        {
            "skill_name": "whatif_analysis",
            "category": "analysis",
            "difficulty_tier": 3,
            "rubric_data": {
                "description": "What-if analysis and scenario planning",
                "criteria": {
                    "basic": "Understands concept of what-if analysis",
                    "proficient": "Can use data tables and scenario manager",
                    "advanced": "Builds comprehensive sensitivity analysis models"
                }
            }
        },
        {
            "skill_name": "charts",
            "category": "charts",
            "difficulty_tier": 2,
            "rubric_data": {
                "description": "Creating appropriate charts and visualizations",
                "criteria": {
                    "basic": "Can create basic charts (column, line, pie)",
                    "proficient": "Chooses appropriate chart types for data",
                    "advanced": "Creates professional charts with proper formatting and context"
                }
            }
        }
    ]
    
    # Combine all rubrics
    all_rubrics = foundations_rubrics + functions_rubrics + data_ops_rubrics + analysis_rubrics
    
    print(f"Seeding {len(all_rubrics)} rubrics...")
    
    for rubric_data in all_rubrics:
        rubric = repo.create_rubric(**rubric_data)
        print(f"Created rubric: {rubric.skill_name} ({rubric.category})")

def seed_questions(db):
    """Seed the database with Excel interview questions"""
    repo = QuestionRepository(db)
    
    questions = [
        # Foundations - Tier 1
        {
            "skill": "references",
            "category": "foundations",
            "difficulty": 1,
            "question_text": "What's the difference between A1 and $A$1 in Excel formulas?",
            "expected_answer": "A1 is a relative reference that changes when copied, $A$1 is an absolute reference that stays fixed",
            "validation_rules": ["mentions_relative", "mentions_absolute", "explains_copying_behavior"]
        },
        {
            "skill": "ranges",
            "category": "foundations", 
            "difficulty": 1,
            "question_text": "How would you select all cells from A1 to A100 in Excel?",
            "expected_answer": "Use A1:A100 or select A1 and drag to A100, or Ctrl+Shift+End",
            "validation_rules": ["shows_range_syntax", "mentions_selection_method"]
        },
        
        # Functions - Tier 2
        {
            "skill": "vlookup",
            "category": "functions",
            "difficulty": 2,
            "question_text": "You have a table with Product IDs in column A and Product Names in column B (rows 2-101). How would you use VLOOKUP to find the product name for ID 'P123' in another worksheet?",
            "expected_answer": "=VLOOKUP('P123',A2:B101,2,FALSE) or similar with proper table reference and exact match",
            "validation_rules": ["uses_vlookup", "correct_syntax", "mentions_exact_match", "proper_column_index"]
        },
        {
            "skill": "if_functions",
            "category": "functions",
            "difficulty": 2, 
            "question_text": "Create a formula that shows 'Pass' if a score in B2 is 70 or above, and 'Fail' if below 70.",
            "expected_answer": "=IF(B2>=70,'Pass','Fail')",
            "validation_rules": ["uses_if", "correct_condition", "proper_syntax"]
        },
        {
            "skill": "if_functions",
            "category": "functions",
            "difficulty": 3,
            "question_text": "Create a nested IF formula to assign letter grades: A (90+), B (80-89), C (70-79), D (60-69), F (<60) based on score in B2.",
            "expected_answer": "=IF(B2>=90,'A',IF(B2>=80,'B',IF(B2>=70,'C',IF(B2>=60,'D','F'))))",
            "validation_rules": ["uses_nested_if", "all_grade_levels", "proper_logic_order"]
        },
        
        # Data Operations - Tier 2
        {
            "skill": "pivot_tables",
            "category": "data_ops",
            "difficulty": 2,
            "question_text": "Describe the steps to create a pivot table that shows total sales by region from a dataset with columns: SalesPerson, Region, Product, SalesAmount.",
            "expected_answer": "Insert > PivotTable, drag Region to Rows, SalesAmount to Values (Sum), configure as needed",
            "validation_rules": ["mentions_insert_pivot", "correct_field_placement", "describes_process"]
        },
        {
            "skill": "countif",
            "category": "functions",
            "difficulty": 2,
            "question_text": "How would you count how many cells in range A1:A100 contain values greater than 50?",
            "expected_answer": "=COUNTIF(A1:A100,'>50')",
            "validation_rules": ["uses_countif", "correct_criteria_syntax", "proper_range"]
        },
        
        # Analysis - Tier 3
        {
            "skill": "case_analysis",
            "category": "analysis", 
            "difficulty": 3,
            "question_text": """Given this dataset structure:
A: Employee Name (A2:A101)
B: Department (B2:B101) 
C: Salary (C2:C101)
D: Performance Rating 1-5 (D2:D101)

Provide formulas for:
1. Average salary by department
2. Count of employees with rating 4 or 5
3. Highest salary in Sales department""",
            "expected_answer": "1. Use AVERAGEIF or pivot table 2. COUNTIFS(D2:D101,'>=4') 3. MAXIFS(C2:C101,B2:B101,'Sales')",
            "validation_rules": ["addresses_all_parts", "uses_appropriate_functions", "demonstrates_analysis_skills"]
        },
        
        # Additional questions for comprehensive coverage
        {
            "skill": "sumif", 
            "category": "functions",
            "difficulty": 2,
            "question_text": "How would you sum all sales amounts for the 'North' region from columns B (Region) and C (Sales)?",
            "expected_answer": "=SUMIF(B:B,'North',C:C)",
            "validation_rules": ["uses_sumif", "correct_criteria", "proper_sum_range"]
        },
        {
            "skill": "index_match",
            "category": "functions", 
            "difficulty": 3,
            "question_text": "Explain why you might use INDEX/MATCH instead of VLOOKUP, and provide an example formula.",
            "expected_answer": "INDEX/MATCH is more flexible - can look left, doesn't break when columns change. Example: =INDEX(B:B,MATCH(E1,A:A,0))",
            "validation_rules": ["explains_advantages", "provides_formula", "shows_understanding"]
        },
        {
            "skill": "charts",
            "category": "charts",
            "difficulty": 2,
            "question_text": "What chart type would you choose to show monthly sales trends over 2 years, and why?",
            "expected_answer": "Line chart - best for showing trends over time, can easily see patterns and changes",
            "validation_rules": ["suggests_line_chart", "explains_reasoning", "mentions_time_series"]
        }
    ]
    
    print(f"Seeding {len(questions)} questions...")
    
    for question_data in questions:
        question = repo.create_question(**question_data)
        print(f"Created question: {question.skill} (difficulty {question.difficulty})")

def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Create tables if they don't exist
    create_tables()
    print("Database tables created/verified")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Seed rubrics and questions
        seed_rubrics(db)
        seed_questions(db)
        
        print("\nDatabase seeding completed successfully!")
        print(f"- Created rubrics for major Excel skill areas")
        print(f"- Created questions across difficulty levels 1-3") 
        print(f"- Ready for interview system to use")
        
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
