#!/usr/bin/env python3
"""
Entry point for the Job Matching Engine.
Run this from the project root: python run.py
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the main application
if __name__ == "__main__":
    from main import graph
    
    # Example: Create a sample input state and run the pipeline
    sample_input = {
        "candidate": {
            "name": "John Doe",
            "title": "Software Engineer",
            "experience_years": 5,
            "skills": ["Python", "JavaScript", "AWS"],
            "preferences": {
                "role_type": "Backend Engineer",
                "location": "Remote"
            }
        },
        "jobs": [
            {
                "job_id": "1",
                "title": "Senior Backend Engineer",
                "location": "Remote",
                "description": "Build scalable backend systems using Python and AWS",
                "required_skills": ["Python", "AWS", "PostgreSQL"],
                "preferred_skills": ["Docker", "Kubernetes"],
                "experience_required": 3
            }
        ]
    }
    
    # Compile the graph
    compiled_graph = graph.compile()
    
    # Run the pipeline
    print("Starting Job Matching Engine pipeline...")
    result = compiled_graph.invoke(sample_input)
    print("Pipeline completed!")
    print(result)
