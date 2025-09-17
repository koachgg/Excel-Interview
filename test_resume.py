import requests
import base64
import json

# Test the resume upload endpoint
def test_resume_upload():
    url = "http://127.0.0.1:8000/api/upload-resume-simple"
    
    # Create a simple test PDF content (base64 encoded)
    test_content = "Sample resume content for testing"
    test_base64 = base64.b64encode(test_content.encode()).decode()
    
    payload = {
        "filename": "test_resume.pdf",
        "content": test_base64
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Resume upload endpoint is working!")
        else:
            print("❌ Resume upload endpoint has issues")
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")

if __name__ == "__main__":
    test_resume_upload()
