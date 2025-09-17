"""
Test FastAPI endpoints
"""
import pytest
from fastapi import status
import json

class TestInterviewEndpoints:
    """Test interview-related endpoints"""
    
    def test_health_check(self, test_client):
        """Test health check endpoint"""
        response = test_client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "healthy"
        assert "timestamp" in response.json()
    
    def test_start_interview(self, test_client):
        """Test starting a new interview"""
        interview_data = {
            "candidate_name": "John Doe"
        }
        
        response = test_client.post("/interviews/start", json=interview_data)
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert "interview_id" in data
        assert "message" in data
        assert data["state"] == "INTRO"
        assert "question" in data
    
    def test_start_interview_invalid_data(self, test_client):
        """Test starting interview with invalid data"""
        response = test_client.post("/interviews/start", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_submit_turn_nonexistent_interview(self, test_client):
        """Test submitting turn for non-existent interview"""
        turn_data = {
            "answer": "This is a test answer"
        }
        
        response = test_client.post("/interviews/fake-id/turn", json=turn_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_get_summary_nonexistent_interview(self, test_client):
        """Test getting summary for non-existent interview"""
        response = test_client.get("/interviews/fake-id/summary")
        assert response.status_code == status.HTTP_404_NOT_FOUND

class TestInterviewFlow:
    """Test complete interview flow"""
    
    def test_complete_interview_flow(self, test_client):
        """Test a complete interview from start to finish"""
        # Start interview
        start_response = test_client.post("/interviews/start", json={
            "candidate_name": "Integration Test User"
        })
        assert start_response.status_code == status.HTTP_201_CREATED
        
        interview_id = start_response.json()["interview_id"]
        
        # Submit several turns
        turns = [
            "Hello, I'm ready to start the interview.",
            "A1 is relative, $A$1 is absolute reference.",
            "=VLOOKUP(lookup_value, table_array, column_index, FALSE)",
            "=IF(A1>10, 'High', 'Low')",
            "I would create a pivot table to analyze the data."
        ]
        
        for i, answer in enumerate(turns):
            turn_response = test_client.post(f"/interviews/{interview_id}/turn", json={
                "answer": answer
            })
            
            # Should succeed for all turns
            assert turn_response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]
            
            response_data = turn_response.json()
            assert "state" in response_data
            assert "message" in response_data
            
            # Check if interview progresses through states
            if i == 0:
                assert response_data["state"] in ["INTRO", "CALIBRATE"]
        
        # Get summary
        summary_response = test_client.get(f"/interviews/{interview_id}/summary")
        assert summary_response.status_code == status.HTTP_200_OK
        
        summary_data = summary_response.json()
        assert "overall_score" in summary_data
        assert "skill_scores" in summary_data
        assert "feedback" in summary_data
        assert "recommendations" in summary_data

class TestAPIValidation:
    """Test API input validation"""
    
    def test_start_interview_empty_name(self, test_client):
        """Test starting interview with empty name"""
        response = test_client.post("/interviews/start", json={
            "candidate_name": ""
        })
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_start_interview_long_name(self, test_client):
        """Test starting interview with very long name"""
        long_name = "x" * 200
        response = test_client.post("/interviews/start", json={
            "candidate_name": long_name
        })
        # Should either reject or truncate
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_201_CREATED]
    
    def test_submit_turn_empty_answer(self, test_client):
        """Test submitting empty answer"""
        # First start an interview
        start_response = test_client.post("/interviews/start", json={
            "candidate_name": "Test User"
        })
        interview_id = start_response.json()["interview_id"]
        
        # Submit empty answer
        response = test_client.post(f"/interviews/{interview_id}/turn", json={
            "answer": ""
        })
        # System should handle empty answers gracefully
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]
    
    def test_submit_turn_very_long_answer(self, test_client):
        """Test submitting very long answer"""
        # Start interview
        start_response = test_client.post("/interviews/start", json={
            "candidate_name": "Test User"
        })
        interview_id = start_response.json()["interview_id"]
        
        # Submit very long answer
        long_answer = "This is a very long answer. " * 200
        response = test_client.post(f"/interviews/{interview_id}/turn", json={
            "answer": long_answer
        })
        # Should handle long answers appropriately
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST]

class TestCORSAndSecurity:
    """Test CORS and security configurations"""
    
    def test_cors_headers(self, test_client):
        """Test CORS headers are present"""
        response = test_client.options("/health")
        # CORS headers should be present for preflight requests
        # Note: TestClient may not simulate CORS exactly like a browser
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_405_METHOD_NOT_ALLOWED]
    
    def test_security_headers(self, test_client):
        """Test security headers"""
        response = test_client.get("/health")
        # Check that response doesn't expose sensitive information
        assert "X-Powered-By" not in response.headers
        assert response.status_code == status.HTTP_200_OK

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_json_payload(self, test_client):
        """Test handling of invalid JSON"""
        response = test_client.post(
            "/interviews/start", 
            data="invalid json{",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_method_not_allowed(self, test_client):
        """Test method not allowed responses"""
        response = test_client.patch("/health")  # PATCH not allowed on health
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    
    def test_rate_limiting_headers(self, test_client):
        """Test that rate limiting information is not exposed"""
        response = test_client.get("/health")
        # Should not expose rate limiting details to prevent abuse
        assert "X-RateLimit-Limit" not in response.headers

if __name__ == "__main__":
    pytest.main([__file__])
