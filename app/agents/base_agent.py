from abc import ABC, abstractmethod
from typing import Dict, Any, List
import together
from ..core.types import Problem, Solution

class BaseAgent(ABC):
    """Base class for all math agents"""
    
    def __init__(self, model: str = "deepseek-ai/deepseek-coder-1.3b-instruct"):
        self.model = model
        # Set Together AI API key
        together.api_key = "daacc8dc45f272f48e8571c2ff9bbccc7169541e632faa75e7efa12900cf2813"
        
    @abstractmethod
    def can_handle(self, problem: Problem) -> bool:
        """Determine if this agent can handle the given problem"""
        pass
        
    @abstractmethod
    async def solve(self, problem: Problem) -> Solution:
        """Solve the given problem and return a solution"""
        pass
    
    async def _get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from Together AI API"""
        # Convert messages to the format expected by Together AI
        prompt = ""
        for message in messages:
            role = message["role"]
            content = message["content"]
            if role == "system":
                prompt += f"<system>{content}</system>\n"
            elif role == "user":
                prompt += f"<human>{content}</human>\n"
            elif role == "assistant":
                prompt += f"<assistant>{content}</assistant>\n"
        prompt += "<assistant>"
        
        # Call Together AI API
        response = together.Complete.create(
            prompt=prompt,
            model=self.model,
            max_tokens=2048,
            temperature=0.2,
            top_p=0.95,
            top_k=50,
            repetition_penalty=1.2,
            stop=["<human>", "</assistant>"]
        )
        
        # Extract the generated text
        return response['output']['choices'][0]['text'].strip()
    
    def _format_matlab_code(self, code: str) -> str:
        """Format MATLAB code with proper indentation and comments"""
        # Remove empty lines at start and end
        code = code.strip()
        
        # Add header comment
        if not code.startswith('%'):
            code = f"% MATLAB Solution\n{code}"
            
        return code 