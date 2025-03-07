from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

class ProblemType(Enum):
    GENERAL = "general"
    ALGEBRA = "algebra"
    CALCULUS = "calculus"
    PROBABILITY = "probability"
    STATISTICS = "statistics"
    LINEAR_ALGEBRA = "linear_algebra"

@dataclass
class Problem:
    text: str
    type: ProblemType
    latex: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    images: Optional[List[bytes]] = None

@dataclass
class Solution:
    explanation: str
    steps: List[str]
    matlab_code: Optional[str] = None
    latex_solution: Optional[str] = None
    plots: Optional[List[bytes]] = None
    numerical_result: Optional[Any] = None
    confidence: float = 1.0

@dataclass
class ProcessedPDF:
    text: str
    images: List[bytes]
    problems: List[Problem]
    metadata: Dict[str, Any] 