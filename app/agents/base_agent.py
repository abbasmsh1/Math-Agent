from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging
from ..core.types import Problem, Solution
from ..core.config import Config

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all math agents"""
    
    def __init__(self, model: Optional[str] = None):
        self.model = model or Config.MISTRAL_MODEL
        self.client = Config.get_mistral_client()
        logger.info(f"Initialized {self.__class__.__name__} with model: {self.model}")
        
    @abstractmethod
    def can_handle(self, problem: Problem) -> bool:
        """Determine if this agent can handle the given problem"""
        pass
        
    @abstractmethod
    async def solve(self, problem: Problem) -> Solution:
        """Solve the given problem and return a solution"""
        pass
    
    async def _get_completion(self, messages: List[Dict[str, str]]) -> str:
        """Get completion from Mistral AI API"""
        try:
            logger.debug(f"Requesting completion with model: {self.model}")
            
            # Call Mistral AI API
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                max_tokens=Config.MAX_TOKENS,
                temperature=Config.TEMPERATURE,
                top_p=Config.TOP_P,
            )
            
            # Extract the generated text
            content = response.choices[0].message.content
            logger.debug("Successfully received completion from Mistral AI")
            return content.strip()
            
        except Exception as e:
            logger.error(f"Error getting completion from Mistral AI: {str(e)}")
            raise RuntimeError(f"Failed to get completion from Mistral AI: {str(e)}") from e
    
    def _format_matlab_code(self, code: str) -> str:
        """Format MATLAB code with proper indentation and comments"""
        # Remove empty lines at start and end
        code = code.strip()
        
        # Add header comment
        if not code.startswith('%'):
            code = f"% MATLAB Solution\n{code}"
            
        return code 