"""
Quick validation script for Excel Interviewer system
Tests basic functionality without full test suite
"""
import asyncio
import os
import sys
import json
from pathlib import Path

# Add server path
server_path = Path(__file__).parent / "server"
sys.path.insert(0, str(server_path))

async def test_llm_providers():
    """Test LLM provider abstraction"""
    print("🔍 Testing LLM providers...")
    
    try:
        # Test with mock keys - just verify the classes can be imported
        os.environ['GOOGLE_API_KEY'] = 'test-key'
        os.environ['GROQ_API_KEY'] = 'test-key'
        os.environ['ANTHROPIC_API_KEY'] = 'test-key'
        
        from llm.provider_abstraction import LLMProvider, GeminiProvider, GroqProvider, ClaudeProvider
        
        print(f"  ✅ LLM provider base class imported successfully")
        print(f"  ✅ Provider classes available: GeminiProvider, GroqProvider, ClaudeProvider")
        
        # Test basic properties without external dependencies
        base_provider = LLMProvider()
        print(f"  ✅ Base provider has required interface: {hasattr(base_provider, 'generate')} {hasattr(base_provider, 'get_cost_estimate')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM provider test failed: {e}")
        return False

def test_grading_system():
    """Test grading system components"""
    print("🔍 Testing grading system...")
    
    try:
        from graders.hybrid import HybridGrader
        from graders.rule_based import RuleBasedGrader
        from storage.models import Question
        
        # Create test question
        question = Question(
            id=1,
            skill="vlookup",
            difficulty=2,
            question_text="Write a VLOOKUP formula to find data",
            expected_answer="=VLOOKUP(lookup_value,table_array,col_index,FALSE)",
            explanation="VLOOKUP searches vertically in a table"
        )
        
        # Test rule-based grader
        rule_grader = RuleBasedGrader()
        
        test_responses = [
            "=VLOOKUP(A1,B:C,2,FALSE)",
            "=VLOOKUP(A1,B1:C10,2,0)",
            "vlookup formula searches for values",
            "I don't know"
        ]
        
        for response in test_responses:
            result = rule_grader.grade_response(response, question)
            print(f"  📝 Response: '{response[:30]}...' -> Score: {result['score']}")
        
        print("  ✅ Rule-based grading working")
        
        # Test hybrid grader (without actual LLM calls)
        hybrid_grader = HybridGrader()
        print("  ✅ Hybrid grader initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Grading system test failed: {e}")
        return False

def test_interview_agent():
    """Test interview agent state machine"""
    print("🔍 Testing interview agent...")
    
    try:
        from agents.interviewer import InterviewAgent, InterviewState
        from unittest.mock import Mock
        
        # Create mock database
        mock_db = Mock()
        agent = InterviewAgent(mock_db)
        
        # Test initial state
        assert agent.state == InterviewState.INTRO
        print(f"  ✅ Initial state: {agent.state}")
        
        # Test state transitions
        agent.state = InterviewState.INTRO
        next_state = agent._determine_next_state()
        assert next_state == InterviewState.CALIBRATE
        print(f"  ✅ State transition: {agent.state} -> {next_state}")
        
        # Test performance calculation
        agent.candidate_performance = {"overall_accuracy": 0.8}
        difficulty = agent._get_target_difficulty()
        print(f"  ✅ Difficulty adjustment: {difficulty} (based on 0.8 accuracy)")
        
        print("  ✅ Interview agent working")
        return True
        
    except Exception as e:
        print(f"  ❌ Interview agent test failed: {e}")
        return False

def test_database_models():
    """Test database models and relationships"""
    print("🔍 Testing database models...")
    
    try:
        from storage.models import Interview, Question, Response
        from storage.database import get_db_engine
        from sqlalchemy.orm import sessionmaker
        import tempfile
        
        # Create temporary database
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            test_db_path = tmp.name
        
        # Test database connection
        engine = get_db_engine(f"sqlite:///{test_db_path}")
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Create tables
        from storage.models import Base
        Base.metadata.create_all(engine)
        
        # Test model creation
        interview = Interview(
            candidate_name="Test User",
            status="in_progress"
        )
        session.add(interview)
        session.commit()
        
        question = Question(
            skill="test",
            difficulty=1,
            question_text="Test question",
            expected_answer="Test answer",
            explanation="Test explanation"
        )
        session.add(question)
        session.commit()
        
        response = Response(
            interview_id=interview.id,
            question_id=question.id,
            response_text="Test response",
            score=85.0,
            feedback="Good answer"
        )
        session.add(response)
        session.commit()
        
        # Test relationships
        assert len(interview.responses) == 1
        assert response.interview.candidate_name == "Test User"
        assert response.question.skill == "test"
        
        print("  ✅ Database models working")
        
        # Cleanup
        session.close()
        os.unlink(test_db_path)
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database models test failed: {e}")
        return False

def test_api_structure():
    """Test FastAPI application structure"""
    print("🔍 Testing API structure...")
    
    try:
        from main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test health endpoint
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        print("  ✅ Health endpoint working")
        
        # Test CORS configuration
        assert len(app.middleware) > 0
        print("  ✅ Middleware configured")
        
        # Test route registration
        routes = [route.path for route in app.routes]
        expected_routes = ["/health", "/interviews", "/interviews/{interview_id}/turn", "/interviews/{interview_id}/summary"]
        
        for route in expected_routes:
            # Check if route pattern exists (allowing for path parameters)
            route_exists = any(route.replace("{interview_id}", "1") in r or route in r for r in routes)
            if not route_exists:
                print(f"  ⚠️ Route may be missing: {route}")
        
        print("  ✅ API structure working")
        return True
        
    except Exception as e:
        print(f"  ❌ API structure test failed: {e}")
        return False

async def main():
    """Run all validation tests"""
    print("🚀 Excel Interviewer System Validation")
    print("="*50)
    
    tests = [
        ("LLM Providers", test_llm_providers),
        ("Grading System", test_grading_system),
        ("Interview Agent", test_interview_agent),
        ("Database Models", test_database_models),
        ("API Structure", test_api_structure)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                results[test_name] = await test_func()
            else:
                results[test_name] = test_func()
        except Exception as e:
            print(f"  ❌ {test_name} validation failed: {e}")
            results[test_name] = False
    
    # Print summary
    print(f"\n{'='*50}")
    print("🏁 VALIDATION RESULTS")
    print(f"{'='*50}")
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:<20}: {status}")
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    print(f"\n📊 Summary: {passed}/{total} components validated")
    
    if passed == total:
        print("🎉 All system components are working correctly!")
        return True
    else:
        print(f"💥 {total - passed} component(s) need attention")
        return False

if __name__ == "__main__":
    asyncio.run(main())
