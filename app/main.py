import os
from typing import List
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from .services.pdf_processor import PDFProcessor
from .agents.probability_agent import ProbabilityAgent
from .core.types import Problem, Solution, ProblemType

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Math Agent System")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Initialize templates
templates = Jinja2Templates(directory="app/templates")

# Initialize services and agents
pdf_processor = PDFProcessor()
probability_agent = ProbabilityAgent()

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Read file content
        content = await file.read()
        
        # Process PDF
        processed_pdf = await pdf_processor.process_pdf(content)
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/solve")
async def solve_problem(problem: Problem):
    """Solve a math problem"""
    try:
        # Select appropriate agent based on problem type
        if problem.type in [ProblemType.PROBABILITY, ProblemType.STATISTICS]:
            solution = await probability_agent.solve(problem)
        else:
            raise HTTPException(
                status_code=400, 
                detail=f"No agent available for problem type: {problem.type}"
            )
        
        return {
            "explanation": solution.explanation,
            "steps": solution.steps,
            "matlab_code": solution.matlab_code,
            "latex_solution": solution.latex_solution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def home(request):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    ) 