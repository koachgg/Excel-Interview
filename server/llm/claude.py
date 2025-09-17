import anthropic
from typing import Dict, Any, Optional
import json
import asyncio
from llm.provider_abstraction import BaseLLMClient, LLMResponse

class ClaudeClient(BaseLLMClient):
    def __init__(self, api_key: str, model_name: str):
        super().__init__(api_key, model_name)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # Model configurations
        self.model_configs = {
            "claude-3-5-sonnet-20241022": {"max_tokens": 8192, "context_window": 200000},
            "claude-3-5-haiku-20241022": {"max_tokens": 8192, "context_window": 200000},
            "claude-3-opus-20240229": {"max_tokens": 4096, "context_window": 200000},
            "claude-3-sonnet-20240229": {"max_tokens": 4096, "context_window": 200000}
        }
    
    async def generate(self, prompt: str, temperature: float = 0.7, 
                      max_tokens: int = 1000, json_mode: bool = False) -> LLMResponse:
        """Generate completion using Claude"""
        try:
            # Prepare system message for JSON mode
            system_message = ""
            if json_mode:
                system_message = "You are a helpful assistant. Always respond with valid JSON format."
                prompt = f"{prompt}\n\nPlease respond in valid JSON format."
            
            # Get max tokens for this model
            model_max_tokens = self.model_configs.get(self.model_name, {}).get("max_tokens", 4096)
            effective_max_tokens = min(max_tokens, model_max_tokens)
            
            # Generate response
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=effective_max_tokens,
                temperature=temperature,
                system=system_message if system_message else None,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract usage information
            usage = {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            }
            
            return LLMResponse(
                content=response.content[0].text,
                usage=usage,
                model=self.model_name
            )
            
        except anthropic.APIError as e:
            raise Exception(f"Claude API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Claude client error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Claude model information"""
        model_info = self.model_configs.get(self.model_name, {})
        
        # Cost information (as of latest pricing)
        cost_per_1k = {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.00025, "output": 0.00125},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015}
        }
        
        return {
            "provider": "Anthropic Claude",
            "model": self.model_name,
            "context_window": model_info.get("context_window", 200000),
            "max_output_tokens": model_info.get("max_tokens", 4096),
            "supports_json": True,
            "cost_per_1k_tokens": cost_per_1k.get(self.model_name, {"input": 0.003, "output": 0.015}),
            "strengths": ["Reasoning", "Analysis", "Code quality", "Safety"]
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
    
    async def analyze_complexity(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt complexity to determine if Claude is needed"""
        complexity_prompt = f"""
        Analyze this Excel interview prompt for complexity:
        {prompt}
        
        Rate complexity 1-5 where:
        1-2: Basic formulas, simple questions
        3: Intermediate analysis, multiple steps  
        4-5: Complex analysis, edge cases, advanced reasoning
        
        Respond with JSON: {{"complexity": int, "reasoning": "brief explanation"}}
        """
        
        response = await self.generate(
            complexity_prompt,
            temperature=0.1,
            max_tokens=200,
            json_mode=True
        )
        
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"complexity": 3, "reasoning": "Unable to parse complexity analysis"}
