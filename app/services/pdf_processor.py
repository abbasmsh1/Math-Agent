import io
from typing import List, Tuple
import PyPDF2
from PIL import Image
import pytesseract
import re
from ..core.types import Problem, ProblemType, ProcessedPDF

class PDFProcessor:
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
            r"distribution"
        ]
    
    async def process_pdf(self, pdf_content: bytes) -> ProcessedPDF:
        """Process a PDF file and extract problems"""
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
        
        text = ""
        images = []
        
        # Extract text and images from each page
        for page in pdf_reader.pages:
            # Extract text
            text += page.extract_text() + "\n"
            
            # Extract images
            if "/XObject" in page["/Resources"]:
                for obj in page["/Resources"]["/XObject"].get_object():
                    if page["/Resources"]["/XObject"][obj]["/Subtype"] == "/Image":
                        image = page["/Resources"]["/XObject"][obj]
                        if "/Filter" in image:
                            if image["/Filter"] == "/DCTDecode":
                                img_data = image._data
                                images.append(img_data)
        
        # Process text to identify problems
        problems = self._extract_problems(text)
        
        # Create metadata
        metadata = {
            "num_pages": len(pdf_reader.pages),
            "num_problems": len(problems),
            "num_images": len(images)
        }
        
        return ProcessedPDF(
            text=text,
            images=images,
            problems=problems,
            metadata=metadata
        )
    
    def _extract_problems(self, text: str) -> List[Problem]:
        """Extract math problems from text"""
        problems = []
        
        # Split text into paragraphs
        paragraphs = text.split("\n\n")
        
        for paragraph in paragraphs:
            # Skip empty paragraphs
            if not paragraph.strip():
                continue
            
            # Check if paragraph contains problem indicators
            is_problem = any(re.search(indicator, paragraph.lower()) 
                           for indicator in self.problem_indicators)
            
            if is_problem:
                # Determine problem type
                problem_type = self._determine_problem_type(paragraph)
                
                # Extract LaTeX if present (between $ signs)
                latex = None
                latex_matches = re.findall(r'\$(.*?)\$', paragraph)
                if latex_matches:
                    latex = " ".join(latex_matches)
                
                problems.append(Problem(
                    text=paragraph.strip(),
                    type=problem_type,
                    latex=latex
                ))
        
        return problems
    
    def _determine_problem_type(self, text: str) -> ProblemType:
        """Determine the type of math problem"""
        text = text.lower()
        
        # Check for probability and statistics indicators
        if any(word in text for word in ["probability", "random", "distribution", 
                                        "expected value", "variance", "standard deviation"]):
            return ProblemType.PROBABILITY
        elif any(word in text for word in ["mean", "median", "mode", "hypothesis", 
                                         "confidence interval", "regression"]):
            return ProblemType.STATISTICS
        elif any(word in text for word in ["derivative", "integral", "limit"]):
            return ProblemType.CALCULUS
        elif any(word in text for word in ["matrix", "vector", "eigenvalue"]):
            return ProblemType.LINEAR_ALGEBRA
        elif any(word in text for word in ["solve", "equation", "simplify"]):
            return ProblemType.ALGEBRA
        else:
            return ProblemType.GENERAL 