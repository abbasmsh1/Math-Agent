from abc import ABC, abstractmethod
from typing import Dict, Any, List
import openai
from ..core.types import Problem, Solution

class BaseAgent(ABC):
    """Base class for all math agents"""
    
    def __init__(self, model: str = "gpt-4-turbo-preview"):
        self.model = model
        
    @abstractmethod
    def can_handle(self, problem: Problem) -> bool:
        """Determine if this agent can handle the given problem"""
        pass
        
    @abstractmethod
    async def solve(self, problem: Problem) -> Solution:
        """Solve the given problem and return a solution"""
        pass
    
    async def _get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from OpenAI API"""
        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=0.2
        )
        return response.choices[0].message.content
    
    def _format_matlab_code(self, code: str) -> str:
        """Format MATLAB code with proper indentation and comments"""
        # Remove empty lines at start and end
        code = code.strip()
        
        # Add header comment
        if not code.startswith('%'):
            code = f"% MATLAB Solution\n{code}"
            
        return code 