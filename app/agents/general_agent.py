from typing import List, Dict, Any, Tuple
import logging
from .base_agent import BaseAgent
from ..core.types import Problem, Solution, ProblemType

logger = logging.getLogger(__name__)


class GeneralAgent(BaseAgent):
    """Agent specialized in solving general mathematics problems"""
    
    def can_handle(self, problem: Problem) -> bool:
        """General agent can handle any problem type"""
        return True
    
    async def solve(self, problem: Problem) -> Solution:
        """Solve a general math problem"""
        logger.info(f"Solving {problem.type.value} problem with GeneralAgent")
        
        # Create a prompt for the problem
        messages = [
            {"role": "system", "content": """You are a mathematics expert. Your task is to solve math problems step by step.
            For each problem, provide:
            1. A clear explanation of the problem and approach
            2. Step-by-step solution with clear mathematical reasoning
            3. MATLAB code to solve or simulate the problem (if applicable)
            4. Mathematical formulas in LaTeX format
            
            Format your response as follows:
            - Start with a clear explanation
            - Number each step clearly
            - Put MATLAB code between ```matlab and ``` markers (if applicable)
            - Put LaTeX formulas between $ markers
            
            Use proper mathematical terminology and methods. Be thorough and accurate."""},
            {"role": "user", "content": f"Please solve this mathematics problem:\n{problem.text}"}
        ]
        
        # Get the solution from the LLM
        response = await self._get_completion(messages)
        
        # Parse the response to extract different components
        explanation, steps, matlab_code = self._parse_solution(response)
        
        # Generate LaTeX solution
        latex_solution = self._generate_latex(steps)
        
        logger.info(f"Successfully solved {problem.type.value} problem")
        
        return Solution(
            explanation=explanation,
            steps=steps,
            matlab_code=self._format_matlab_code(matlab_code) if matlab_code else None,
            latex_solution=latex_solution,
            confidence=0.85  # Slightly lower confidence for general problems
        )
    
    def _parse_solution(self, response: str) -> Tuple[str, List[str], str]:
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
                
            # Check for step indicators
            if (line.startswith("Step") or 
                (line[0].isdigit() and "." in line[:5]) or
                line.startswith("1.") or line.startswith("2.") or
                line.startswith("3.") or line.startswith("4.") or
                line.startswith("5.")):
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
        
        # If no steps were found, use the entire response as explanation
        if not steps and explanation:
            steps = explanation[1:] if len(explanation) > 1 else []
            explanation = explanation[0] if explanation else ""
        elif not explanation:
            explanation = "Solution provided below."
        
        return " ".join(explanation) if isinstance(explanation, list) else explanation, steps, matlab_code
    
    def _generate_latex(self, steps: List[str]) -> str:
        """Generate LaTeX representation of the solution"""
        latex = "\\begin{align*}\n"
        found_latex = False
        
        for step in steps:
            # Extract any mathematical expressions between $ signs
            parts = step.split("$")
            if len(parts) > 1:
                found_latex = True
                for i in range(1, len(parts), 2):
                    latex += parts[i] + " \\\\\n"
        
        if not found_latex:
            # Try to extract equations from the text
            for step in steps:
                # Look for common equation patterns
                if "=" in step:
                    # Try to extract the equation part
                    eq_parts = step.split("=")
                    if len(eq_parts) >= 2:
                        left = eq_parts[0].strip()
                        right = eq_parts[1].strip()
                        # Simple LaTeX conversion
                        left = left.replace("^", "^{").replace(" ", "} ") + "}"
                        latex += f"{left} = {right} \\\\\n"
                        found_latex = True
        
        if not found_latex:
            latex = "\\text{Solution steps provided in text format.}\n"
        
        latex += "\\end{align*}"
        return latex

