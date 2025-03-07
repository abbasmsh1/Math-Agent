# Math Agent System

A sophisticated system of AI agents designed to solve various mathematical problems from PDF documents. The system specializes in:
- General mathematics
- Probability and statistics
- MATLAB code generation
- Step-by-step problem solving

## Features
- PDF document processing with OCR capabilities
- Multiple specialized math agents for different problem types
- LaTeX math expression parsing
- MATLAB code generation for numerical solutions
- Web interface for easy interaction
- Detailed step-by-step explanations

## Setup
1. Install Python 3.9 or higher
2. Install Tesseract OCR:
   - Windows: Download and install from https://github.com/UB-Mannheim/tesseract/wiki
   - Linux: `sudo apt-get install tesseract-ocr`
   - Mac: `brew install tesseract`
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a .env file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
1. Access the web interface at http://localhost:8000
2. Upload a PDF containing math problems
3. Select the type of analysis needed
4. Get detailed solutions with explanations and MATLAB code

## Project Structure
- `/app`: Main application code
  - `/agents`: Specialized math agents
  - `/core`: Core functionality and utilities
  - `/api`: API endpoints
  - `/services`: Service layer for PDF processing and math operations
  - `/templates`: HTML templates
  - `/static`: Static files (CSS, JS)

## License
MIT License 