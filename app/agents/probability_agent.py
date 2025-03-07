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
            {"role": "system", "content": """You are a probability and statistics expert. Your task is to solve math problems step by step.
            For each problem, provide:
            1. A clear explanation of the problem and approach
            2. Step-by-step solution with clear mathematical reasoning
            3. MATLAB code to solve or simulate the problem
            4. Mathematical formulas in LaTeX format
            
            Format your response as follows:
            - Start with a clear explanation
            - Number each step clearly
            - Put MATLAB code between ```matlab and ``` markers
            - Put LaTeX formulas between $ markers
            
            Use proper statistical terminology and methods."""},
            {"role": "user", "content": f"Please solve this probability/statistics problem:\n{problem.text}"}
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
            confidence=0.85  # Slightly lower confidence with Deepseek model
        )
    
    def _parse_solution(self, response: str) -> tuple[str, List[str], str]:
        """Parse the LLM response into components"""
        parts = response.split("```")
        
        # Extract MATLAB code
        matlab_code = ""
        for i in range(len(parts)):
            if i > 0 and "matlab" in parts[i-1].lower():
                matlab_code = parts[i].strip()
                parts[i] = ""  # Remove the code from parts
        
        # Clean up the remaining text
        text = " ".join(p for p in parts if p.strip())
        
        # Split into explanation and steps
        lines = text.split("\n")
        explanation = []
        current_step = []
        steps = []
        
        in_explanation = True
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Step") or line[0].isdigit() and "." in line[:5]:
                in_explanation = False
                if current_step:
                    steps.append(" ".join(current_step))
                current_step = [line]
            elif in_explanation:
                explanation.append(line)
            else:
                current_step.append(line)
        
        if current_step:
            steps.append(" ".join(current_step))
        
        return " ".join(explanation), steps, matlab_code
    
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