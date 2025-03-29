import sys
from src.graph.builder import build_graph
from src.graph.types import State
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def run_workflow(query):
    """Run the LangGraph workflow with a query."""
    # Create the workflow
    graph = build_graph()
    
    state = State(
      messages=[HumanMessage(content=query)],
      next="",
      full_plan="",
      TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
    )
    
    # Execute the workflow
    result = graph.invoke(state)
    
    # Print all messages in the conversation
    print("\n=== Workflow Messages ===")
    for msg in result["messages"]:
        if hasattr(msg, 'name') and msg.name:
            print(f"[{msg.name}]: {msg.content}")
        elif isinstance(msg, HumanMessage):
            print(f"[Human]: {msg.content}")
        elif isinstance(msg, AIMessage):
            print(f"[AI]: {msg.content}")
        elif isinstance(msg, SystemMessage):
            print(f"[System]: {msg.content}")
    
    # Print final response (last AI message)
    print("\n=== Final Response ===")
    last_ai_message = None
    for msg in reversed(result["messages"]):
        if isinstance(msg, AIMessage):
            last_ai_message = msg.content
            break
    print(last_ai_message or "No response generated")
    
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
