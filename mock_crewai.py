"""
Mock implementation of CrewAI tools for testing purposes.
This file provides simplified versions of the CrewAI tools to work around
the compatibility issue with Python 3.10.
"""

class BaseTool:
    """Mock implementation of CrewAI BaseTool."""
    
    def __init__(self, name, description, func):
        self.name = name
        self.description = description
        self.func = func
    
    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)
