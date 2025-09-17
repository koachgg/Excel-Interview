#!/usr/bin/env python3
"""
Test script to verify API providers are working
"""
import os
import sys
import asyncio

# Add server directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

async def test_gemini():
    """Test Gemini API connection"""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("❌ GEMINI_API_KEY not found in environment")
            return False
            
        print(f"🔑 Using Gemini API key: {api_key[:8]}...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        response = model.generate_content("Hello, respond with just 'Working'")
        print(f"✅ Gemini response: {response.text}")
        return True
        
    except ImportError as e:
        print(f"❌ Gemini package not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Gemini API error: {e}")
        return False

async def test_groq():
    """Test Groq API connection"""
    try:
        import httpx
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("❌ GROQ_API_KEY not found in environment")
            return False
            
        print(f"🔑 Using Groq API key: {api_key[:8]}...")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "llama-3.1-70b-versatile",
            "messages": [{"role": "user", "content": "Hello, respond with just 'Working'"}],
            "max_tokens": 50,
            "temperature": 0.1
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30.0
            )
            
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Groq response: {content}")
            return True
        else:
            print(f"❌ Groq API error: {response.status_code} - {response.text}")
            return False
            
    except ImportError as e:
        print(f"❌ httpx package not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return False

async def test_provider_manager():
    """Test the provider manager"""
    try:
        from llm.provider_abstraction import LLMProviderManager
        
        provider = os.getenv("PROVIDER", "gemini")
        print(f"🔧 Testing provider manager with provider: {provider}")
        
        manager = LLMProviderManager()
        print(f"📊 Provider: {manager.provider}, Model: {manager.model_name}")
        
        # Test simple generation
        result = await manager.generate_interview_question("Create a simple Excel question about SUM functions", temperature=0.7)
        print(f"✅ Provider Manager response: {result[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Provider Manager error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("🧪 Testing AI Provider Configuration")
    print("=" * 50)
    
    # Test individual providers
    gemini_works = await test_gemini()
    print()
    groq_works = await test_groq()
    print()
    
    # Test provider manager
    manager_works = await test_provider_manager()
    
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"Gemini API: {'✅ Working' if gemini_works else '❌ Failed'}")
    print(f"Groq API: {'✅ Working' if groq_works else '❌ Failed'}")
    print(f"Provider Manager: {'✅ Working' if manager_works else '❌ Failed'}")
    
    if not any([gemini_works, groq_works]):
        print("\n❌ No API providers are working. Check your API keys and internet connection.")
    elif manager_works:
        print("\n🎉 System is ready to use real AI providers!")
    else:
        print("\n⚠️ API providers work individually but provider manager has issues.")

if __name__ == "__main__":
    asyncio.run(main())
