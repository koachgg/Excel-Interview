from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import os
from enum import Enum

# Load environment variables if not already loaded
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")  # Load from parent directory
except ImportError:
    pass  # dotenv not available, assume env vars are set

class LLMProvider(Enum):
    GEMINI = "gemini"
    GROQ = "groq"
    CLAUDE = "claude"

class LLMResponse:
    def __init__(self, content: str, usage: Dict[str, int] = None, model: str = None):
        self.content = content
        self.usage = usage or {}
        self.model = model

class BaseLLMClient(ABC):
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 1000, json_mode: bool = False) -> LLMResponse:
        """Generate completion from the model"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities"""
        pass

class MockLLMClient(BaseLLMClient):
    """Mock LLM client for development when real providers aren't available"""
    
    def __init__(self):
        super().__init__("mock-key", "mock-model")
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 1000, json_mode: bool = False) -> LLMResponse:
        """Generate a mock response"""
        # Simple mock response based on prompt content
        if "question" in prompt.lower():
            mock_content = '{"question": "What is the VLOOKUP function?", "difficulty": 2, "skill": "vlookup"}'
        elif "grade" in prompt.lower() or "score" in prompt.lower():
            mock_content = '{"score": 75, "feedback": "Good understanding with room for improvement", "reasoning": "Shows basic knowledge"}'
        else:
            mock_content = "This is a mock response for development purposes."
        
        return LLMResponse(content=mock_content, model="mock-model")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information"""
        return {
            "name": "mock-model",
            "provider": "mock",
            "max_tokens": 1000,
            "capabilities": ["text-generation", "json-mode"]
        }

class LLMProviderManager:
    """Manages LLM provider selection and unified interface"""
    
    def __init__(self):
        self.provider = os.getenv("PROVIDER", "gemini").lower()
        self.model_name = os.getenv("MODEL_NAME", self._get_default_model())
        self.client = None  # Initialize lazily
        self._client_initialized = False
    
    def _get_default_model(self) -> str:
        """Get default model name for current provider"""
        defaults = {
            "gemini": "gemini-2.0-flash-exp",
            "groq": "llama-3.1-70b-versatile", 
            "claude": "claude-3-5-sonnet-20241022"
        }
        return defaults.get(self.provider, "gemini-2.0-flash-exp")
    
    def _initialize_client(self) -> BaseLLMClient:
        """Initialize the appropriate LLM client"""
        print(f"DEBUG: self.provider = '{self.provider}' (type: {type(self.provider)})")
        try:
            if self.provider == "gemini":
                print("DEBUG: Matched gemini provider")
                from llm.gemini import GeminiClient
                api_key = os.getenv("GEMINI_API_KEY")
                if not api_key:
                    raise ValueError("GEMINI_API_KEY environment variable required")
                return GeminiClient(api_key, self.model_name)
            
            elif self.provider == "groq":
                print("DEBUG: Matched groq provider")
                from llm.groq import GroqClient
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key:
                    raise ValueError("GROQ_API_KEY environment variable required")
                return GroqClient(api_key, self.model_name)
            
            elif self.provider == "claude":
                print("DEBUG: Matched claude provider")
                from llm.claude import ClaudeClient
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY environment variable required")
                return ClaudeClient(api_key, self.model_name)
            
            else:
                print(f"DEBUG: No match found for provider '{self.provider}'")
                raise ValueError(f"Unsupported provider: {self.provider}")
        
        except ImportError as e:
            # If we can't import the required packages, this will be caught by _get_client
            raise e
    
    def _get_client(self) -> BaseLLMClient:
        """Get client with lazy initialization"""
        if not self._client_initialized:
            try:
                print(f"Initializing {self.provider} client...")
                self.client = self._initialize_client()
                print(f"Successfully initialized {self.provider} client!")
                self._client_initialized = True
            except ImportError as e:
                # Fallback to a simple mock client for development
                print(f"Warning: Could not initialize {self.provider} client due to ImportError: {e}")
                print("Using mock client for development purposes")
                self.client = MockLLMClient()
                self._client_initialized = True
            except Exception as e:
                print(f"Warning: Could not initialize {self.provider} client due to error: {e}")
                print("Using mock client for development purposes")
                self.client = MockLLMClient()
                self._client_initialized = True
                self._client_initialized = True
        return self.client
    
    async def generate_interview_question(self, prompt: str, temperature: float = 0.7) -> str:
        """Generate interview question with appropriate temperature"""
        client = self._get_client()
        response = await client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=800,
            json_mode=True
        )
        return response.content
    
    async def grade_answer(self, prompt: str, temperature: float = 0.1) -> str:
        """Grade answer with low temperature for consistency"""
        client = self._get_client()
        response = await client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=500,
            json_mode=True
        )
        return response.content
    
    async def generate_summary(self, prompt: str, temperature: float = 0.3) -> str:
        """Generate summary report with moderate creativity"""
        client = self._get_client()
        response = await client.generate(
            prompt=prompt,
            temperature=temperature,
            max_tokens=1200,
            json_mode=False
        )
        return response.content
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get current provider and model information"""
        client = self._get_client()
        return {
            "provider": self.provider,
            "model": self.model_name,
            "model_info": client.get_model_info()
        }
    
    def switch_provider(self, provider: str, model_name: str = None):
        """Switch to different provider/model (useful for escalation)"""
        original_provider = self.provider
        original_model = self.model_name
        
        try:
            self.provider = provider.lower()
            self.model_name = model_name or self._get_default_model()
            self._client_initialized = False  # Force reinitialization
            self.client = None
        except Exception as e:
            # Rollback on failure
            self.provider = original_provider
            self.model_name = original_model
            self._client_initialized = False
            self.client = None
            raise e

# Global provider manager instance
provider_manager = LLMProviderManager()
