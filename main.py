"""
Main application entry point for AGENTIC InsurTech.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app.ui.app import launch_app

if __name__ == "__main__":
    # Create necessary directories
    os.makedirs("static/uploads", exist_ok=True)
    os.makedirs("static/templates/policies", exist_ok=True)
    
    # Launch the Gradio application
    launch_app()
