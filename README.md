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
- Powered by Mistral AI for high-quality solutions

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
4. Create a `.env` file with your Mistral AI API key:
   ```
   MISTRAL_API_KEY=your_mistral_api_key_here
   MISTRAL_MODEL=mistral-medium-latest
   ```
   
   Optional configuration:
   ```
   MAX_TOKENS=2048
   TEMPERATURE=0.2
   TOP_P=0.95
   DEBUG=False
   ```
   
   To get a Mistral AI API key:
   1. Sign up at [console.mistral.ai](https://console.mistral.ai)
   2. Navigate to your workspace
   3. Go to API keys section and create a new key

5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage
1. Access the web interface at http://localhost:8000
2. Upload a PDF containing math problems
3. Select the type of analysis needed
4. Get detailed solutions with explanations and MATLAB code

## Deployment to Vercel

This application is configured for deployment on Vercel. See [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) for detailed deployment instructions.

Quick steps:
1. Set environment variables in Vercel dashboard (MISTRAL_API_KEY, etc.)
2. Connect your Git repository to Vercel
3. Deploy!

For detailed instructions, see [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md).

## Project Structure
- `/app`: Main application code
  - `/agents`: Specialized math agents
    - `base_agent.py`: Base class for all agents
    - `probability_agent.py`: Agent for probability and statistics problems
  - `/core`: Core functionality and utilities
    - `types.py`: Data models and type definitions
    - `config.py`: Configuration management
  - `/services`: Service layer for PDF processing and math operations
    - `pdf_processor.py`: PDF extraction and problem detection
  - `/templates`: HTML templates
    - `index.html`: Web interface

## Improvements Made
- ✅ Migrated from TogetherAI to Mistral AI
- ✅ Removed hardcoded API keys (now uses environment variables)
- ✅ Added comprehensive logging
- ✅ Improved error handling
- ✅ Added configuration management
- ✅ Fixed type hints
- ✅ Enhanced code quality and maintainability

## License
MIT License 