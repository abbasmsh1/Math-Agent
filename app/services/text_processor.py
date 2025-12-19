"""
Text processor for extracting and processing math problems from text input
"""
import re
import logging
from typing import List, Optional
from ..core.types import Problem, ProblemType

logger = logging.getLogger(__name__)


class TextProcessor:
    """Process text input to extract math problems and equations"""
    
    def __init__(self):
        self.problem_indicators = [
            r"solve",
            r"find",
            r"calculate",
            r"compute",
            r"determine",
            r"evaluate",
            r"prove",
            r"show that",
            r"what is",
            r"probability",
            r"expected value",
            r"variance",
            r"distribution",
            r"equation",
            r"integral",
            r"derivative",
            r"limit"
        ]
    
    def process_text(self, text: str, problem_type: Optional[str] = None) -> Problem:
        """
        Process text input and create a Problem object
        
        Args:
            text: The text input containing the math problem or equation
            problem_type: Optional problem type override (e.g., "probability", "algebra")
        
        Returns:
            Problem object with extracted information
        """
        text = text.strip()
        
        if not text:
            raise ValueError("Text input cannot be empty")
        
        # Determine problem type if not provided
        if problem_type:
            try:
                detected_type = ProblemType(problem_type.lower())
            except ValueError:
                logger.warning(f"Invalid problem type '{problem_type}', auto-detecting...")
                detected_type = self._determine_problem_type(text)
        else:
            detected_type = self._determine_problem_type(text)
        
        # Extract LaTeX if present (between $ signs)
        latex = None
        latex_matches = re.findall(r'\$(.*?)\$', text)
        if latex_matches:
            latex = " ".join(latex_matches)
        
        # Extract equations (common patterns)
        equations = self._extract_equations(text)
        
        logger.info(f"Processed text input: type={detected_type.value}, has_latex={latex is not None}, equations={len(equations)}")
        
        return Problem(
            text=text,
            type=detected_type,
            latex=latex,
            context={"equations": equations} if equations else None
        )
    
    def _extract_equations(self, text: str) -> List[str]:
        """Extract mathematical equations from text"""
        equations = []
        
        # Pattern for common equation formats:
        # - "x = ..." or "y = ..."
        # - "f(x) = ..."
        # - "∫ ..." or "∫ ... dx"
        # - "d/dx ..." or "∂/∂x ..."
        
        # Simple equations: variable = expression
        eq_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)\s*=\s*([^=]+?)(?=\s*(?:,|\.|$|and|or))'
        matches = re.finditer(eq_pattern, text)
        for match in matches:
            equations.append(match.group(0))
        
        # Function definitions: f(x) = ...
        func_pattern = r'\b([a-zA-Z][a-zA-Z0-9]*)\s*\([^)]+\)\s*=\s*[^=]+'
        func_matches = re.finditer(func_pattern, text)
        for match in func_matches:
            if match.group(0) not in equations:
                equations.append(match.group(0))
        
        # Integrals: ∫ ... or ∫ ... dx
        integral_pattern = r'∫[^∫]+(?:dx|dy|dz|dt)'
        integral_matches = re.finditer(integral_pattern, text)
        for match in integral_matches:
            if match.group(0) not in equations:
                equations.append(match.group(0))
        
        return equations
    
    def _determine_problem_type(self, text: str) -> ProblemType:
        """Determine the type of math problem from text"""
        text_lower = text.lower()
        
        # Check for probability and statistics indicators
        if any(word in text_lower for word in ["probability", "random", "distribution", 
                                              "expected value", "variance", "standard deviation",
                                              "binomial", "normal", "poisson", "bernoulli"]):
            return ProblemType.PROBABILITY
        elif any(word in text_lower for word in ["mean", "median", "mode", "hypothesis", 
                                                "confidence interval", "regression", "correlation",
                                                "t-test", "chi-square"]):
            return ProblemType.STATISTICS
        elif any(word in text_lower for word in ["derivative", "integral", "limit", "differentiate",
                                                "integrate", "calculus", "d/dx", "∂/∂x"]):
            return ProblemType.CALCULUS
        elif any(word in text_lower for word in ["matrix", "vector", "eigenvalue", "determinant",
                                                "linear transformation", "basis", "span"]):
            return ProblemType.LINEAR_ALGEBRA
        elif any(word in text_lower for word in ["solve", "equation", "simplify", "factor",
                                                "quadratic", "polynomial", "root", "zero"]):
            return ProblemType.ALGEBRA
        else:
            return ProblemType.GENERAL

