import google.generativeai as genai
from typing import Dict, Any, Optional
import json
import asyncio
from llm.provider_abstraction import BaseLLMClient, LLMResponse

class GeminiClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        
        # Generation config for different use cases
        self.interview_config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=800,
            response_mime_type="application/json"
        )
        
        self.grading_config = genai.types.GenerationConfig(
            temperature=0.1,
            max_output_tokens=500,
            response_mime_type="application/json"
        )
        
        self.summary_config = genai.types.GenerationConfig(
            temperature=0.3,
            max_output_tokens=1200,
            response_mime_type="text/plain"
        )
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 1000, json_mode: bool = False) -> LLMResponse:
        """Generate completion using Gemini"""
        try:
            # Configure generation settings
            config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
                response_mime_type="application/json" if json_mode else "text/plain"
            )
            
            # Generate response
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=config
            )
            
            # Extract usage information if available
            usage_metadata = getattr(response, 'usage_metadata', None)
            usage = {}
            if usage_metadata:
                usage = {
                    "prompt_tokens": getattr(usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(usage_metadata, 'total_token_count', 0)
                }
            
            return LLMResponse(
                content=response.text,
                usage=usage,
                model=self.model_name
            )
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Gemini model information"""
        return {
            "provider": "Google Gemini",
            "model": self.model_name,
            "context_window": 1000000 if "gemini-2.0" in self.model_name else 128000,
            "max_output_tokens": 8192,
            "supports_json": True,
            "cost_per_1k_tokens": {
                "input": 0.00025 if "2.0" in self.model_name else 0.00015,
                "output": 0.001 if "2.0" in self.model_name else 0.0006
            }
        }
    
    async def generate_with_retry(self, prompt: str, max_retries: int = 3, **kwargs) -> LLMResponse:
        """Generate with exponential backoff retry"""
        for attempt in range(max_retries):
            try:
                return await self.generate(prompt, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                wait_time = 2 ** attempt
                await asyncio.sleep(wait_time)
