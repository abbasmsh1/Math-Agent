from typing import List, Dict, Any
import numpy as np
from scipy import stats
from .base_agent import BaseAgent
from ..core.types import Problem, Solution, ProblemType

class ProbabilityAgent(BaseAgent):
    """Agent specialized in solving probability and statistics problems"""
    
    def can_handle(self, problem: Problem) -> bool:
        return problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]
    
    async def solve(self, problem: Problem) -> Solution:
        # Create a prompt for the problem
        messages = [
            {"role": "system", "content": """You are a probability and statistics expert. 
            Analyze the problem and provide:
            1. A clear explanation
            2. Step-by-step solution
            3. MATLAB code to solve or simulate the problem
            4. Relevant formulas in LaTeX
            Use proper statistical terminology and methods."""},
            {"role": "user", "content": problem.text}
        ]
        
        # Get the solution from the LLM
        response = await self._get_completion(messages)
        
        # Parse the response to extract different components
        explanation, steps, matlab_code = self._parse_solution(response)
        
        # Generate LaTeX solution
        latex_solution = self._generate_latex(steps)
        
        return Solution(
            explanation=explanation,
            steps=steps,
            matlab_code=self._format_matlab_code(matlab_code),
            latex_solution=latex_solution,
            confidence=0.9
        )
    
    def _parse_solution(self, response: str) -> tuple[str, List[str], str]:
        """Parse the LLM response into components"""
        parts = response.split("```")
        
        # Extract MATLAB code
        matlab_code = ""
        for i in range(len(parts)):
            if i > 0 and parts[i-1].strip().lower().endswith("matlab"):
                matlab_code = parts[i].strip()
                parts[i] = ""  # Remove the code from parts
        
        # Clean up the remaining text
        text = " ".join(p for p in parts if p.strip())
        
        # Split into explanation and steps
        sections = text.split("Step")
        explanation = sections[0].strip()
        
        # Process steps
        steps = []
        for section in sections[1:]:
            if ":" in section:
                step_text = section.split(":", 1)[1].strip()
                steps.append(f"Step{section}")
        
        return explanation, steps, matlab_code
    
    def _generate_latex(self, steps: List[str]) -> str:
        """Generate LaTeX representation of the solution"""
        latex = "\\begin{align*}\n"
        for step in steps:
            # Extract any mathematical expressions between $ signs
            parts = step.split("$")
            if len(parts) > 1:
                for i in range(1, len(parts), 2):
                    latex += parts[i] + " \\\\\n"
        latex += "\\end{align*}"
        return latex 