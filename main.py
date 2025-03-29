import sys
from src.graph import create_agent_workflow

def run_workflow(query):
    """Run the LangGraph workflow with a query."""
    # Create the workflow
    workflow = create_agent_workflow()
    
    # Initialize state with the query
    state = {"query": query, "thoughts": [], "response": None}
    
    # Execute the workflow
    result = workflow.invoke(state)
    
    # Print thoughts
    print("\n=== Workflow Thoughts ===")
    for thought in result.get("thoughts", []):
        print(f"- {thought}")
    
    # Print final response
    response = result.get("response", "No response generated")
    print("\n=== Final Response ===")
    print(response)
    
    return result

def main():
    import sys

    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your query: ")
    
    print("\n=== User Query ===")
    print(user_query)
    
    # Run the workflow
    run_workflow(user_query)

if __name__ == "__main__":
    main()
