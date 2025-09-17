import httpx
from typing import Dict, Any, Optional
import json
import asyncio
from llm.provider_abstraction import BaseLLMClient, LLMResponse

class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Model configurations
        self.model_configs = {
            "llama-3.1-70b-versatile": {"max_tokens": 32768, "context_window": 32768},
            "llama-3.1-8b-instant": {"max_tokens": 8192, "context_window": 32768},
            "llama-3.3-70b-versatile": {"max_tokens": 32768, "context_window": 32768},
            "mixtral-8x7b-32768": {"max_tokens": 32768, "context_window": 32768},
            "qwen2.5-72b-instruct": {"max_tokens": 8192, "context_window": 32768}
        }
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 1000, json_mode: bool = False) -> LLMResponse:
        """Generate completion using Groq"""
        try:
            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": [
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                "temperature": temperature,
                "max_tokens": min(max_tokens, self.model_configs.get(self.model_name, {}).get("max_tokens", 8192)),
                "stream": False
            }
            
            # Add JSON mode if requested and supported
            if json_mode:
                payload["response_format"] = {"type": "json_object"}
                payload["messages"].insert(0, {
                    "role": "system",
                    "content": "You are a helpful assistant. Always respond with valid JSON."
                })
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                    timeout=30.0
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract usage information
                usage = data.get("usage", {})
                usage_dict = {
                    "prompt_tokens": usage.get("prompt_tokens", 0),
                    "completion_tokens": usage.get("completion_tokens", 0),
                    "total_tokens": usage.get("total_tokens", 0)
                }
                
                return LLMResponse(
                    content=data["choices"][0]["message"]["content"],
                    usage=usage_dict,
                    model=self.model_name
                )
                
        except httpx.HTTPError as e:
            raise Exception(f"Groq API HTTP error: {str(e)}")
        except Exception as e:
            raise Exception(f"Groq API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Groq model information"""
        model_info = self.model_configs.get(self.model_name, {})
        
        # Cost information (approximate, as Groq has free tier)
        cost_per_1k = {
            "llama-3.1-70b-versatile": {"input": 0.0006, "output": 0.0008},
            "llama-3.1-8b-instant": {"input": 0.0001, "output": 0.0002},
            "llama-3.3-70b-versatile": {"input": 0.0006, "output": 0.0008},
            "mixtral-8x7b-32768": {"input": 0.0003, "output": 0.0006},
            "qwen2.5-72b-instruct": {"input": 0.0006, "output": 0.0008}
        }
        
        return {
            "provider": "Groq",
            "model": self.model_name,
            "context_window": model_info.get("context_window", 32768),
            "max_output_tokens": model_info.get("max_tokens", 8192),
            "supports_json": True,
            "cost_per_1k_tokens": cost_per_1k.get(self.model_name, {"input": 0.0006, "output": 0.0008}),
            "speed": "Very Fast (up to 750 tokens/sec)"
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
    
    async def check_rate_limit(self) -> Dict[str, Any]:
        """Check current rate limit status"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                )
                return {
                    "status": "healthy" if response.status_code == 200 else "error",
                    "rate_limit_remaining": response.headers.get("x-ratelimit-remaining"),
                    "rate_limit_reset": response.headers.get("x-ratelimit-reset")
                }
        except Exception as e:
            return {"status": "error", "error": str(e)}
