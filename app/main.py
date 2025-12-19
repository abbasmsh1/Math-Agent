import logging
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import secrets

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

def validate_config_on_demand(request: Request):
    """Validate configuration when first needed, checking session first"""
    global _config_validated
    session_key = request.session.get("mistral_api_key")
    
    try:
        Config.validate(session_key)
        _config_validated = True
    except ValueError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail=f"API key not configured. Please set your Mistral API key in settings."
        )

def get_api_key_from_session(request: Request) -> Optional[str]:
    """Get API key from session"""
    return request.session.get("mistral_api_key")

# Initialize FastAPI app
app = FastAPI(title="Math Agent System")

# Add session middleware for secure API key storage
app.add_middleware(
    SessionMiddleware,
    secret_key=secrets.token_urlsafe(32),
    max_age=86400,  # 24 hours
    same_site="lax"
)

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

# Initialize services
pdf_processor = PDFProcessor()
text_processor = TextProcessor()
# Agents will be created per-request with session API keys

# Request models
class TextInputRequest(BaseModel):
    text: str
    problem_type: Optional[str] = None

class ApiKeyRequest(BaseModel):
    api_key: str

@app.post("/api/set-api-key")
async def set_api_key(request: Request, api_key_request: ApiKeyRequest):
    """Set or update the Mistral API key in the session"""
    try:
        # Validate the API key by trying to create a client
        from mistralai import Mistral
        
        # Try a simple validation - just store it if it's not empty
        if api_key_request.api_key and len(api_key_request.api_key.strip()) > 0:
            request.session["mistral_api_key"] = api_key_request.api_key.strip()
            logger.info("API key set in session")
            return {
                "status": "success",
                "message": "API key saved successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="API key cannot be empty")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting API key: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Invalid API key: {str(e)}")

@app.get("/api/check-api-key")
async def check_api_key(request: Request):
    """Check if API key is configured"""
    session_key = get_api_key_from_session(request)
    env_key = Config.MISTRAL_API_KEY
    
    has_key = bool(session_key or env_key)
    
    return {
        "configured": has_key,
        "source": "session" if session_key else ("environment" if env_key else "none")
    }

@app.post("/upload")
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    validate_config_on_demand(request)
    
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
async def solve_text_equation(request: Request, text_request: TextInputRequest):
    """Solve a math problem or equation from text input"""
    validate_config_on_demand(request)
    api_key = get_api_key_from_session(request)
    
    try:
        logger.info(f"Processing text input: {text_request.text[:100]}...")
        
        # Process the text input
        problem = text_processor.process_text(text_request.text, text_request.problem_type)
        
        logger.info(f"Detected problem type: {problem.type.value}")
        
        # Create agents with session API key
        prob_agent = ProbabilityAgent(api_key=api_key)
        gen_agent = GeneralAgent(api_key=api_key)
        
        # Select appropriate agent based on problem type
        if problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]:
            solution = await prob_agent.solve(problem)
        else:
            # Use general agent for all other problem types
            logger.info(f"Using GeneralAgent for problem type: {problem.type.value}")
            solution = await gen_agent.solve(problem)
        
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
async def solve_problem(request: Request, problem: Problem):
    """Solve a math problem (from Problem object)"""
    validate_config_on_demand(request)
    api_key = get_api_key_from_session(request)
    
    try:
        logger.info(f"Solving problem of type: {problem.type.value}")
        
        # Create agents with session API key
        prob_agent = ProbabilityAgent(api_key=api_key)
        gen_agent = GeneralAgent(api_key=api_key)
        
        # Select appropriate agent based on problem type
        if problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]:
            solution = await prob_agent.solve(problem)
        else:
            # Use general agent for all other problem types
            logger.info(f"Using GeneralAgent for problem type: {problem.type.value}")
            solution = await gen_agent.solve(problem)
        
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