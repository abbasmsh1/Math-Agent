import io
from typing import List, Tuple
import logging
import PyPDF2
from PIL import Image
import re
from ..core.types import Problem, ProblemType, ProcessedPDF

# Make pytesseract optional (only needed for OCR)
try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False
    logging.warning("pytesseract not available - OCR features will be disabled")

logger = logging.getLogger(__name__)

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
        try:
            logger.info("Starting PDF processing")
            
            # Read PDF content
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            num_pages = len(pdf_reader.pages)
            logger.info(f"PDF has {num_pages} pages")
            
            text = ""
            images = []
            
            # Extract text and images from each page
            for page_num, page in enumerate(pdf_reader.pages, 1):
                try:
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    
                    # Extract images
                    if "/XObject" in page.get("/Resources", {}):
                        resources = page["/Resources"]
                        if "/XObject" in resources:
                            xobjects = resources["/XObject"].get_object()
                            for obj in xobjects:
                                try:
                                    obj_data = xobjects[obj]
                                    if obj_data.get("/Subtype") == "/Image":
                                        image = obj_data
                                        if "/Filter" in image:
                                            if image["/Filter"] == "/DCTDecode":
                                                img_data = image._data
                                                images.append(img_data)
                                except Exception as e:
                                    logger.warning(f"Error extracting image from page {page_num}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Error processing page {page_num}: {str(e)}")
                    continue
            
            # Process text to identify problems
            problems = self._extract_problems(text)
            logger.info(f"Extracted {len(problems)} problems from PDF")
            
            # Create metadata
            metadata = {
                "num_pages": num_pages,
                "num_problems": len(problems),
                "num_images": len(images)
            }
            
            return ProcessedPDF(
                text=text,
                images=images,
                problems=problems,
                metadata=metadata
            )
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
            raise RuntimeError(f"Failed to process PDF: {str(e)}") from e
    
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