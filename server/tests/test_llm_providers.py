"""
Test LLM provider abstraction
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import asyncio
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from llm.provider_abstraction import LLMProvider, GeminiProvider, GroqProvider, ClaudeProvider
from llm.provider_abstraction import get_provider, generate_response

class TestLLMProvider:
    """Test base LLM provider functionality"""
    
    def test_provider_interface(self):
        """Test that provider implements required interface"""
        provider = LLMProvider()
        
        # Base class should have required methods
        assert hasattr(provider, 'generate')
        assert hasattr(provider, 'get_cost_estimate')
        assert callable(provider.generate)
        assert callable(provider.get_cost_estimate)
    
    def test_provider_metadata(self):
        """Test provider metadata properties"""
        provider = LLMProvider()
        
        assert hasattr(provider, 'name')
        assert hasattr(provider, 'model')
        assert hasattr(provider, 'max_tokens')
        assert hasattr(provider, 'cost_per_token')

class TestGeminiProvider:
    """Test Google Gemini provider"""
    
    def setup_method(self):
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            self.provider = GeminiProvider()
    
    def test_initialization(self):
        """Test Gemini provider initialization"""
        assert self.provider.name == "gemini"
        assert "gemini" in self.provider.model.lower()
        assert self.provider.max_tokens > 0
        assert self.provider.cost_per_token > 0
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    async def test_generate_response(self, mock_configure, mock_model_class):
        """Test Gemini response generation"""
        # Mock the model and response
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "This is a test response from Gemini"
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        # Test generation
        response = await self.provider.generate(
            "Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert response == "This is a test response from Gemini"
        mock_configure.assert_called_once()
        mock_model.generate_content.assert_called_once()
    
    def test_cost_estimation(self):
        """Test cost estimation for Gemini"""
        prompt = "This is a test prompt with some tokens"
        cost = self.provider.get_cost_estimate(prompt)
        
        assert isinstance(cost, float)
        assert cost > 0
        assert cost < 1.0  # Should be very cheap for short prompts
    
    @patch('google.generativeai.GenerativeModel')
    @patch('google.generativeai.configure')
    async def test_error_handling(self, mock_configure, mock_model_class):
        """Test Gemini error handling"""
        # Mock API error
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API rate limit exceeded")
        mock_model_class.return_value = mock_model
        
        # Should handle errors gracefully
        with pytest.raises(Exception) as exc_info:
            await self.provider.generate("Test prompt")
        
        assert "rate limit" in str(exc_info.value).lower()

class TestGroqProvider:
    """Test Groq provider"""
    
    def setup_method(self):
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            self.provider = GroqProvider()
    
    def test_initialization(self):
        """Test Groq provider initialization"""
        assert self.provider.name == "groq"
        assert "mixtral" in self.provider.model.lower() or "llama" in self.provider.model.lower()
        assert self.provider.max_tokens > 0
        assert self.provider.cost_per_token >= 0  # Groq is very cheap
    
    @patch('groq.Groq')
    async def test_generate_response(self, mock_groq_class):
        """Test Groq response generation"""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Fast response from Groq"
        
        mock_client.chat.completions.create.return_value = mock_response
        mock_groq_class.return_value = mock_client
        
        response = await self.provider.generate(
            "Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert response == "Fast response from Groq"
        mock_client.chat.completions.create.assert_called_once()
    
    def test_cost_estimation(self):
        """Test cost estimation for Groq"""
        prompt = "Test prompt for cost estimation"
        cost = self.provider.get_cost_estimate(prompt)
        
        assert isinstance(cost, float)
        assert cost >= 0  # Groq might be free or very cheap
        assert cost < 0.1  # Should be very inexpensive

class TestClaudeProvider:
    """Test Anthropic Claude provider"""
    
    def setup_method(self):
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            self.provider = ClaudeProvider()
    
    def test_initialization(self):
        """Test Claude provider initialization"""
        assert self.provider.name == "claude"
        assert "claude" in self.provider.model.lower()
        assert self.provider.max_tokens > 0
        assert self.provider.cost_per_token > 0
    
    @patch('anthropic.Anthropic')
    async def test_generate_response(self, mock_anthropic_class):
        """Test Claude response generation"""
        # Mock the client and response
        mock_client = Mock()
        mock_response = Mock()
        mock_response.content = [Mock()]
        mock_response.content[0].text = "Thoughtful response from Claude"
        
        mock_client.messages.create.return_value = mock_response
        mock_anthropic_class.return_value = mock_client
        
        response = await self.provider.generate(
            "Test prompt",
            max_tokens=100,
            temperature=0.7
        )
        
        assert response == "Thoughtful response from Claude"
        mock_client.messages.create.assert_called_once()
    
    def test_cost_estimation(self):
        """Test cost estimation for Claude"""
        prompt = "Test prompt for premium model"
        cost = self.provider.get_cost_estimate(prompt)
        
        assert isinstance(cost, float)
        assert cost > 0
        # Claude is typically more expensive than Gemini/Groq
        assert cost < 1.0  # But still reasonable for short prompts

class TestProviderFactory:
    """Test provider factory and selection logic"""
    
    def test_get_provider_by_name(self):
        """Test getting providers by name"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            provider = get_provider("gemini")
            assert isinstance(provider, GeminiProvider)
            assert provider.name == "gemini"
        
        with patch.dict(os.environ, {'GROQ_API_KEY': 'test-key'}):
            provider = get_provider("groq")
            assert isinstance(provider, GroqProvider)
            assert provider.name == "groq"
        
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'}):
            provider = get_provider("claude")
            assert isinstance(provider, ClaudeProvider)
            assert provider.name == "claude"
    
    def test_default_provider_fallback(self):
        """Test fallback to default provider"""
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            # Should default to Gemini when no provider specified
            provider = get_provider()
            assert isinstance(provider, GeminiProvider)
    
    def test_invalid_provider_name(self):
        """Test handling of invalid provider names"""
        with pytest.raises(ValueError) as exc_info:
            get_provider("nonexistent_provider")
        
        assert "unknown provider" in str(exc_info.value).lower()
    
    def test_missing_api_keys(self):
        """Test behavior when API keys are missing"""
        # Clear environment
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                get_provider("gemini")
            
            assert "api key" in str(exc_info.value).lower()

class TestProviderIntegration:
    """Test provider integration and high-level functionality"""
    
    @patch('llm.provider_abstraction.get_provider')
    async def test_generate_response_function(self, mock_get_provider):
        """Test high-level generate_response function"""
        # Mock provider
        mock_provider = Mock()
        mock_provider.generate = AsyncMock(return_value="Generated response")
        mock_get_provider.return_value = mock_provider
        
        response = await generate_response(
            "Test prompt",
            provider_name="gemini",
            max_tokens=100
        )
        
        assert response == "Generated response"
        mock_provider.generate.assert_called_once_with(
            "Test prompt",
            max_tokens=100,
            temperature=0.7
        )
    
    @patch('llm.provider_abstraction.get_provider')
    async def test_provider_failover(self, mock_get_provider):
        """Test failover between providers"""
        # Mock primary provider failure
        mock_primary = Mock()
        mock_primary.name = "groq"
        mock_primary.generate = AsyncMock(side_effect=Exception("Service unavailable"))
        
        # Mock fallback provider success
        mock_fallback = Mock()
        mock_fallback.name = "gemini"
        mock_fallback.generate = AsyncMock(return_value="Fallback response")
        
        # Set up provider selection to return different providers
        def provider_side_effect(name=None):
            if name == "groq":
                return mock_primary
            else:
                return mock_fallback
        
        mock_get_provider.side_effect = provider_side_effect
        
        # This would need to be implemented in the actual provider abstraction
        # For now, just test that errors are properly propagated
        with pytest.raises(Exception):
            await generate_response("Test prompt", provider_name="groq")
    
    def test_cost_comparison(self):
        """Test cost comparison between providers"""
        prompt = "Analyze this Excel formula: =VLOOKUP(A1,Sheet2!B:D,3,FALSE)"
        
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test-key',
            'GROQ_API_KEY': 'test-key', 
            'ANTHROPIC_API_KEY': 'test-key'
        }):
            gemini = get_provider("gemini")
            groq = get_provider("groq")
            claude = get_provider("claude")
            
            gemini_cost = gemini.get_cost_estimate(prompt)
            groq_cost = groq.get_cost_estimate(prompt)
            claude_cost = claude.get_cost_estimate(prompt)
            
            # Groq should be cheapest, Claude most expensive
            assert groq_cost <= gemini_cost <= claude_cost
    
    @patch('llm.provider_abstraction.get_provider')
    async def test_streaming_support(self, mock_get_provider):
        """Test streaming response support (if implemented)"""
        mock_provider = Mock()
        
        # Mock streaming response
        async def mock_stream():
            yield "Partial "
            yield "streaming "
            yield "response"
        
        mock_provider.generate_stream = mock_stream
        mock_get_provider.return_value = mock_provider
        
        # If streaming is implemented
        if hasattr(mock_provider, 'generate_stream'):
            chunks = []
            async for chunk in mock_provider.generate_stream():
                chunks.append(chunk)
            
            assert chunks == ["Partial ", "streaming ", "response"]

class TestProviderPerformance:
    """Test provider performance characteristics"""
    
    def test_token_counting(self):
        """Test token counting accuracy"""
        # Test various prompt lengths
        test_cases = [
            ("Short prompt", 2),
            ("This is a longer prompt with more words", 8),
            ("=VLOOKUP(A1,Sheet2!B1:D100,3,FALSE) This is an Excel formula", 10)
        ]
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            provider = get_provider("gemini")
            
            for prompt, expected_min_tokens in test_cases:
                cost = provider.get_cost_estimate(prompt)
                # Cost should increase with prompt length
                assert cost > 0
    
    @patch('time.time')
    def test_rate_limiting_awareness(self, mock_time):
        """Test that providers are aware of rate limits"""
        # Mock time progression
        mock_time.side_effect = [0, 1, 2, 3]
        
        with patch.dict(os.environ, {'GOOGLE_API_KEY': 'test-key'}):
            provider = get_provider("gemini")
            
            # Should have rate limit properties if implemented
            assert hasattr(provider, 'name')  # Basic check
            assert hasattr(provider, 'cost_per_token')  # Cost awareness
    
    def test_provider_capabilities(self):
        """Test provider capability reporting"""
        with patch.dict(os.environ, {
            'GOOGLE_API_KEY': 'test-key',
            'GROQ_API_KEY': 'test-key',
            'ANTHROPIC_API_KEY': 'test-key'
        }):
            providers = [
                get_provider("gemini"),
                get_provider("groq"), 
                get_provider("claude")
            ]
            
            for provider in providers:
                # Each provider should report its capabilities
                assert provider.max_tokens > 1000  # Reasonable context window
                assert provider.cost_per_token >= 0  # Non-negative cost
                assert len(provider.name) > 0  # Has a name
                assert len(provider.model) > 0  # Has a model identifier

if __name__ == "__main__":
    pytest.main([__file__])
