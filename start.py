#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Create necessary directories
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("static/templates/policies", exist_ok=True)

# Launch the application
from app.ui.app import launch_app

if __name__ == "__main__":
    print("Starting AGENTIC InsurTech Application...")
    launch_app()
