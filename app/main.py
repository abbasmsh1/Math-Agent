import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .services.pdf_processor import PDFProcessor
from .services.text_processor import TextProcessor
from .agents.probability_agent import ProbabilityAgent
from .agents.general_agent import GeneralAgent
from .core.types import Problem, Solution, ProblemType
from .core.config import Config
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy validation - only validate when actually needed (not on import)
# This is important for Vercel serverless functions
_config_validated = False

def validate_config_on_demand():
    """Validate configuration when first needed"""
    global _config_validated
    if not _config_validated:
        try:
            Config.validate()
            _config_validated = True
        except ValueError as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Configuration error: {str(e)}. Please check your environment variables."
            )

# Initialize FastAPI app
app = FastAPI(title="Math Agent System")

# Mount static files (optional - only if directory exists)
import os
static_dir = "app/static"
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
    logger.info("Static files directory mounted")
else:
    logger.info("Static files directory not found, skipping mount")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services and agents
pdf_processor = PDFProcessor()
text_processor = TextProcessor()
probability_agent = ProbabilityAgent()
general_agent = GeneralAgent()

# Request models
class TextInputRequest(BaseModel):
    text: str
    problem_type: Optional[str] = None

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    validate_config_on_demand()
    
    if not file.filename or not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        logger.info(f"Processing PDF file: {file.filename}")
        
        # Read file content
        content = await file.read()
        
        # Process PDF
        processed_pdf = await pdf_processor.process_pdf(content)
        
        logger.info(f"Successfully processed PDF: {processed_pdf.metadata['num_problems']} problems found")
        
        return {
            "message": "PDF processed successfully",
            "num_problems": processed_pdf.metadata["num_problems"],
            "problems": [
                {
                    "text": problem.text,
                    "type": problem.type.value
                }
                for problem in processed_pdf.problems
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@app.post("/solve-text")
async def solve_text_equation(request: TextInputRequest):
    """Solve a math problem or equation from text input"""
    validate_config_on_demand()
    
    try:
        logger.info(f"Processing text input: {request.text[:100]}...")
        
        # Process the text input
        problem = text_processor.process_text(request.text, request.problem_type)
        
        logger.info(f"Detected problem type: {problem.type.value}")
        
        # Select appropriate agent based on problem type
        if problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]:
            solution = await probability_agent.solve(problem)
        else:
            # Use general agent for all other problem types
            logger.info(f"Using GeneralAgent for problem type: {problem.type.value}")
            solution = await general_agent.solve(problem)
        
        logger.info("Problem solved successfully")
        
        return {
            "explanation": solution.explanation,
            "steps": solution.steps,
            "matlab_code": solution.matlab_code,
            "latex_solution": solution.latex_solution,
            "confidence": solution.confidence,
            "problem_type": problem.type.value
        }
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solving problem: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error solving problem: {str(e)}")

@app.post("/solve")
async def solve_problem(problem: Problem):
    """Solve a math problem (from Problem object)"""
    validate_config_on_demand()
    
    try:
        logger.info(f"Solving problem of type: {problem.type.value}")
        
        # Select appropriate agent based on problem type
        if problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]:
            solution = await probability_agent.solve(problem)
        else:
            # Use general agent for all other problem types
            logger.info(f"Using GeneralAgent for problem type: {problem.type.value}")
            solution = await general_agent.solve(problem)
        
        logger.info("Problem solved successfully")
        
        return {
            "explanation": solution.explanation,
            "steps": solution.steps,
            "matlab_code": solution.matlab_code,
            "latex_solution": solution.latex_solution,
            "confidence": solution.confidence
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error solving problem: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error solving problem: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "Math Agent System"
    }

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    ) 