"""
Configuration settings for the AGENTIC InsurTech application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Application settings
APP_NAME = "AGENTIC InsurTech"
APP_VERSION = "0.1.0"
DEBUG = True

# Supabase settings
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# OpenAI settings for vision LLM
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
VISION_MODEL = "gpt-4-vision-preview"  # State-of-the-art vision model

# Agent settings
UNDERWRITING_AGENT_MODEL = "gpt-4"
CLAIMS_AGENT_MODEL = "gpt-4"
CUSTOMER_AGENT_MODEL = "gpt-4"

# Performance targets
UNDERWRITING_SUCCESS_TARGET = 0.75  # 75%
CLAIMS_SUCCESS_TARGET = 0.85  # 85%
CUSTOMER_SUCCESS_TARGET = 0.60  # 60%

UNDERWRITING_TIME_TARGET = 2.1  # seconds
CLAIMS_TIME_TARGET = 1.8  # seconds
CUSTOMER_TIME_TARGET = 3.2  # seconds

# File paths
UPLOAD_FOLDER = "static/uploads"
POLICY_TEMPLATES_FOLDER = "static/templates/policies"
