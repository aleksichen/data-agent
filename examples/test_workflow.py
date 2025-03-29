"""
Simple example to test the LangGraph workflow.
"""

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.graph import create_agent_workflow

def test_workflow():
    """Test the LangGraph workflow with a few example queries."""
    
    test_queries = [
        "What is the weather like today?",
        "Can you research the history of artificial intelligence?",
        "Tell me about LangGraph"
    ]
    
    for query in test_queries:
        print("\n" + "="*50)
        print(f"Testing query: {query}")
        print("="*50)
        
        # Create the workflow
        workflow = create_agent_workflow()
        
        # Initialize state with the query
        state = {"query": query, "thoughts": [], "response": None}
        
        # Execute the workflow
        result = workflow.invoke(state)
        
        # Print thoughts
        print("\nWorkflow Thoughts:")
        for thought in result.get("thoughts", []):
            print(f"- {thought}")
        
        # Print final response
        response = result.get("response", "No response generated")
        print("\nFinal Response:")
        print(response)

if __name__ == "__main__":
    test_workflow()
