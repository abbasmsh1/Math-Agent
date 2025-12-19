"""
Vercel serverless function entry point for Math Agent System
"""
import sys
from pathlib import Path

# Add the project root to the Python path
# This ensures imports work correctly in Vercel's serverless environment
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import the FastAPI app
# This import happens when the serverless function is invoked
from app.main import app
app = app

# Export the app for Vercel
# Vercel will automatically handle the ASGI app and route requests to it
__all__ = ["app"]

