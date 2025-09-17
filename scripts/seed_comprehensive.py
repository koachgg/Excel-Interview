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
                "scoring_criteria": {
                    "novice": "Uses basic SUM function only",
                    "basic": "Can use SUMIF with simple criteria",
                    "proficient": "Uses various criteria types effectively",
                    "advanced": "Uses SUMIFS for multiple criteria calculations"
                },
                "key_concepts": ["Criteria range", "Sum range", "Multiple conditions", "SUMIFS"]
            }
        }
    ]
    
    # Data Operations rubrics (Difficulty Tier 2-3)
    data_ops_rubrics = [
        {
            "skill_name": "pivot_tables",
            "category": "data_ops",
            "difficulty_tier": 3,
            "version": "1.0",
            "rubric_data": {
                "description": "Creating and using pivot tables for analysis",
                "scoring_criteria": {
                    "novice": "Never used pivot tables",
                    "basic": "Can create basic pivot tables with guidance",
                    "proficient": "Creates useful pivot tables independently",
                    "advanced": "Uses calculated fields, grouping, and advanced features"
                },
                "key_concepts": ["Field arrangement", "Value calculations", "Filtering", "Grouping", "Calculated fields"]
            }
        },
        {
            "skill_name": "filtering",
            "category": "data_ops", 
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Data filtering and sorting operations",
                "scoring_criteria": {
                    "novice": "Basic sorting only",
                    "basic": "Uses AutoFilter for simple criteria",
                    "proficient": "Combines multiple filters effectively",
                    "advanced": "Uses advanced filter with criteria ranges"
                },
                "key_concepts": ["AutoFilter", "Custom filters", "Multiple criteria", "Advanced filter"]
            }
        },
        {
            "skill_name": "data_validation",
            "category": "data_ops",
            "difficulty_tier": 2,
            "version": "1.0", 
            "rubric_data": {
                "description": "Input validation and data quality control",
                "scoring_criteria": {
                    "novice": "No experience with validation",
                    "basic": "Creates simple dropdown lists",
                    "proficient": "Uses various validation types with custom messages",
                    "advanced": "Creates complex validation rules with formulas"
                },
                "key_concepts": ["Validation types", "Custom messages", "Error handling", "List validation"]
            }
        }
    ]
    
    # Analysis rubrics (Difficulty Tier 3)
    analysis_rubrics = [
        {
            "skill_name": "statistics",
            "category": "analysis",
            "difficulty_tier": 3,
            "version": "1.0",
            "rubric_data": {
                "description": "Statistical analysis functions",
                "scoring_criteria": {
                    "novice": "Basic average/count functions only",
                    "basic": "Uses MEDIAN, MAX, MIN functions",
                    "proficient": "Uses STDEV, CORREL, and descriptive statistics",
                    "advanced": "Performs regression analysis and advanced statistics"
                },
                "key_concepts": ["Descriptive statistics", "Standard deviation", "Correlation", "Regression"]
            }
        },
        {
            "skill_name": "what_if_analysis",
            "category": "analysis",
            "difficulty_tier": 3,
            "version": "1.0",
            "rubric_data": {
                "description": "Scenario analysis and goal seeking",
                "scoring_criteria": {
                    "novice": "No experience with what-if tools",
                    "basic": "Understands goal seek concept",
                    "proficient": "Uses data tables and scenario manager",
                    "advanced": "Builds comprehensive sensitivity analysis models"
                },
                "key_concepts": ["Goal Seek", "Data Tables", "Scenario Manager", "Solver"]
            }
        },
        {
            "skill_name": "case_analysis", 
            "category": "analysis",
            "difficulty_tier": 3,
            "version": "1.0",
            "rubric_data": {
                "description": "Applied Excel skills in business scenarios",
                "scoring_criteria": {
                    "novice": "Cannot apply Excel to real problems",
                    "basic": "Can solve simple problems with heavy guidance",
                    "proficient": "Independently solves multi-step business problems", 
                    "advanced": "Optimizes solutions and handles edge cases elegantly"
                },
                "key_concepts": ["Problem decomposition", "Function selection", "Error handling", "Efficiency"]
            }
        }
    ]
    
    # Charts rubrics (Difficulty Tier 2)
    charts_rubrics = [
        {
            "skill_name": "charts",
            "category": "charts",
            "difficulty_tier": 2,
            "version": "1.0",
            "rubric_data": {
                "description": "Creating effective data visualizations",
                "scoring_criteria": {
                    "novice": "Cannot create charts",
                    "basic": "Creates basic charts with default settings",
                    "proficient": "Chooses appropriate chart types and formats them well",
                    "advanced": "Creates compelling visualizations with proper context and annotations"
                },
                "key_concepts": ["Chart types", "Data selection", "Formatting", "Storytelling"]
            }
        }
    ]
    
    # Combine all rubrics
    all_rubrics = foundations_rubrics + functions_rubrics + data_ops_rubrics + analysis_rubrics + charts_rubrics
    
    print(f"Seeding {len(all_rubrics)} rubrics...")
    
    for rubric_data in all_rubrics:
        rubric = repo.create_rubric(**rubric_data)
        print(f"Created rubric: {rubric.skill_name} ({rubric.category}, tier {rubric.difficulty_tier})")

def seed_questions(db):
    """Seed the database with comprehensive Excel interview questions"""
    repo = QuestionRepository(db)
    
    questions = [
        # === FOUNDATIONS (Tier 1) ===
        {
            "skill": "references",
            "category": "foundations",
            "difficulty": 1,
            "question_text": "What's the difference between A1 and $A$1 in Excel formulas? Give an example of when you'd use each.",
            "expected_answer": "A1 is a relative reference that changes when copied (A1 becomes B2 when copied to B2). $A$1 is an absolute reference that stays fixed when copied. Use relative for calculations that should adjust (like summing rows), absolute for fixed references (like tax rates).",
            "validation_rules": ["mentions_relative", "mentions_absolute", "explains_copy_behavior", "gives_use_case"]
        },
        {
            "skill": "basic_formulas",
            "category": "foundations", 
            "difficulty": 1,
            "question_text": "How would you create a formula to calculate the total of cells A1 through A10, then multiply that result by the value in cell B1?",
            "expected_answer": "=(SUM(A1:A10)*B1) or =SUM(A1:A10)*B1",
            "validation_rules": ["uses_sum_function", "correct_range_syntax", "multiplies_by_b1", "proper_parentheses_optional"]
        },
        {
            "skill": "ranges",
            "category": "foundations",
            "difficulty": 1, 
            "question_text": "Explain the difference between selecting A1:A10 and A1,A3,A5 in Excel. How would you type each in a formula?",
            "expected_answer": "A1:A10 is a continuous range from A1 to A10. A1,A3,A5 selects only specific cells A1, A3, and A5 (non-contiguous). In formulas: SUM(A1:A10) vs SUM(A1,A3,A5)",
            "validation_rules": ["explains_continuous_range", "explains_non_contiguous", "shows_formula_syntax", "uses_colon_vs_comma"]
        },
        
        # === FUNCTIONS (Tier 2) ===
        {
            "skill": "if_functions",
            "category": "functions",
            "difficulty": 2,
            "question_text": "Create a formula that displays 'Excellent' for scores 90+, 'Good' for scores 80-89, 'Fair' for 70-79, and 'Poor' for anything below 70. The score is in cell C2.",
            "expected_answer": "=IF(C2>=90,\"Excellent\",IF(C2>=80,\"Good\",IF(C2>=70,\"Fair\",\"Poor\")))",
            "validation_rules": ["uses_nested_if", "correct_thresholds", "proper_text_quotes", "logical_order_high_to_low"]
        },
        {
            "skill": "vlookup",
            "category": "functions",
            "difficulty": 2, 
            "question_text": "You have a table with Employee IDs in column A and Employee Names in column B (rows 2-101). Write a VLOOKUP formula to find the name of employee ID 'E123'.",
            "expected_answer": "=VLOOKUP(\"E123\",A2:B101,2,FALSE) or =VLOOKUP(\"E123\",A:B,2,FALSE)",
            "validation_rules": ["uses_vlookup", "correct_lookup_value", "proper_table_array", "column_index_2", "exact_match_false"]
        },
        {
            "skill": "countif",
            "category": "functions",
            "difficulty": 2,
            "question_text": "How would you count how many cells in range B1:B50 contain values greater than 1000?",
            "expected_answer": "=COUNTIF(B1:B50,\">1000\")",
            "validation_rules": ["uses_countif", "correct_range", "proper_criteria_syntax", "greater_than_operator"]
        },
        {
            "skill": "sumif",
            "category": "functions", 
            "difficulty": 2,
            "question_text": "You have departments in column A and salaries in column B. Write a formula to sum all salaries for the 'Sales' department.",
            "expected_answer": "=SUMIF(A:A,\"Sales\",B:B) or =SUMIF(A1:A100,\"Sales\",B1:B100)",
            "validation_rules": ["uses_sumif", "correct_criteria_range", "proper_criteria", "correct_sum_range"]
        },
        
        # === ADVANCED FUNCTIONS (Tier 3) ===
        {
            "skill": "index_match",
            "category": "functions",
            "difficulty": 3,
            "question_text": "Explain why someone might prefer INDEX/MATCH over VLOOKUP. Then write an INDEX/MATCH formula to look up a value in column C based on a match in column A.",
            "expected_answer": "INDEX/MATCH is more flexible - can look to the left, doesn't break when columns are inserted, and performs better. Formula: =INDEX(C:C,MATCH(lookup_value,A:A,0))",
            "validation_rules": ["explains_advantages", "mentions_flexibility", "correct_index_syntax", "correct_match_syntax", "exact_match_0"]
        },
        {
            "skill": "if_functions",
            "category": "functions",
            "difficulty": 3,
            "question_text": "Create a formula that checks if a value in A1 is between 10 and 50 (inclusive). If yes, multiply it by 2. If no, return 'Out of range'.",
            "expected_answer": "=IF(AND(A1>=10,A1<=50),A1*2,\"Out of range\")",
            "validation_rules": ["uses_if_and_and", "correct_range_logic", "proper_calculation", "handles_false_condition"]
        },
        
        # === DATA OPERATIONS (Tier 2-3) ===
        {
            "skill": "pivot_tables",
            "category": "data_ops",
            "difficulty": 3,
            "question_text": "You have sales data with columns: Sales Rep, Region, Product, and Sales Amount. Describe how you'd create a pivot table to show total sales by region, with sales reps as rows within each region.",
            "expected_answer": "Insert > PivotTable. Drag Region to Rows (top level), Sales Rep to Rows (nested below Region), Sales Amount to Values (sum). This creates a hierarchical view with regions expandable to show individual reps.",
            "validation_rules": ["mentions_pivot_creation", "describes_field_placement", "explains_hierarchy", "mentions_sum_aggregation"]
        },
        {
            "skill": "filtering",
            "category": "data_ops", 
            "difficulty": 2,
            "question_text": "How would you filter a dataset to show only records where the 'Department' column contains 'Sales' AND the 'Salary' column is greater than 50000?",
            "expected_answer": "Apply AutoFilter to headers. Use Department dropdown to filter for 'Sales'. Use Salary dropdown > Number Filters > Greater Than > 50000. Both filters work together (AND logic).",
            "validation_rules": ["mentions_autofilter", "describes_text_filter", "describes_number_filter", "understands_and_logic"]
        },
        {
            "skill": "data_validation",
            "category": "data_ops",
            "difficulty": 2,
            "question_text": "How would you create a dropdown list in Excel that only allows users to select from the values: 'High', 'Medium', 'Low'?",
            "expected_answer": "Select the cell(s), Data > Data Validation, Allow: List, Source: High,Medium,Low (or reference a range with these values).",
            "validation_rules": ["mentions_data_validation", "selects_list_type", "provides_source_values", "describes_process"]
        },
        
        # === ANALYSIS (Tier 3) ===
        {
            "skill": "statistics",
            "category": "analysis",
            "difficulty": 3,
            "question_text": "What Excel functions would you use to calculate the median, standard deviation, and correlation between two datasets?",
            "expected_answer": "MEDIAN() for median, STDEV.S() or STDEV.P() for standard deviation, CORREL() for correlation coefficient between two ranges.",
            "validation_rules": ["mentions_median", "mentions_stdev", "mentions_correl", "shows_function_understanding"]
        },
        {
            "skill": "case_analysis",
            "category": "analysis", 
            "difficulty": 3,
            "question_text": "You're analyzing monthly sales data and need to: 1) Find the top 3 performing months, 2) Calculate year-over-year growth, 3) Identify months that are 20% above average. Describe your approach using Excel functions.",
            "expected_answer": "1) Use LARGE() function or sort data descending. 2) Use formulas like (This Year - Last Year)/Last Year for growth %. 3) Use IF with condition: Month > AVERAGE(range)*1.2 to identify above-average months.",
            "validation_rules": ["addresses_top_performers", "explains_growth_calculation", "uses_average_comparison", "shows_systematic_approach"]
        },
        
        # === CHARTS (Tier 2) ===
        {
            "skill": "charts",
            "category": "charts", 
            "difficulty": 2,
            "question_text": "You need to show monthly revenue trends over 3 years. What chart type would you choose and why? How would you make it automatically update when new data is added?",
            "expected_answer": "Line chart - best for showing trends over time, easy to spot patterns. To auto-update: convert data to Excel Table (Ctrl+T) or use dynamic named ranges with OFFSET/COUNTA functions.",
            "validation_rules": ["chooses_line_chart", "explains_trend_reasoning", "mentions_auto_update_method", "shows_chart_understanding"]
        }
    ]
    
    print(f"Seeding {len(questions)} questions...")
    
    for question_data in questions:
        question = repo.create_question(**question_data)
        print(f"Created question: {question.skill} (difficulty {question.difficulty}) - {question.question_text[:50]}...")

def main():
    """Main seeding function with comprehensive Excel interview content"""
    print("=== Excel Interview Database Seeder ===")
    print("Creating comprehensive rubrics and questions for Excel skill assessment...")
    
    # Create tables if they don't exist
    create_tables()
    print("✓ Database tables created/verified")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Clear existing data
        print("\n🧹 Clearing existing data...")
        
        # Seed rubrics and questions
        print("\n📋 Seeding rubrics...")
        seed_rubrics(db)
        
        print("\n❓ Seeding questions...")  
        seed_questions(db)
        
        print("\n✅ Database seeding completed successfully!")
        print("="*50)
        print("📊 SUMMARY:")
        print("  • Foundation skills (references, formulas, ranges)")
        print("  • Function mastery (IF, VLOOKUP, INDEX/MATCH, SUMIF, COUNTIF)")
        print("  • Data operations (pivot tables, filtering, validation)")
        print("  • Analysis skills (statistics, what-if analysis, case studies)")
        print("  • Visualization (charts and best practices)")
        print("="*50)
        print("🚀 Ready for interview system to conduct comprehensive Excel assessments!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed Excel interview database")
    parser.add_argument("--force", action="store_true", help="Skip confirmation prompt")
    args = parser.parse_args()
    
    if not args.force:
        response = input("\n⚠️  This will overwrite existing rubrics and questions. Continue? (y/N): ")
        if not response.lower().startswith('y'):
            print("❌ Seeding cancelled.")
            exit(0)
    
    main()
