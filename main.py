import sys
import json
import asyncio
from typing import Dict, List, Any, Optional

from src.graph.builder import build_graph
from src.graph.types import State
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def format_message(msg) -> Dict[str, str]:
    """Format a message for SSE output."""
    if hasattr(msg, 'name') and msg.name:
        role = msg.name
    elif isinstance(msg, HumanMessage):
        role = "human"
    elif isinstance(msg, AIMessage):
        role = "ai"
    elif isinstance(msg, SystemMessage):
        role = "system"
    else:
        role = "unknown"
    
    return {
        "role": role,
        "content": msg.content
    }


async def run_workflow_stream(query):
    """Run the LangGraph workflow with a query and stream results."""
    # Create the workflow
    graph = build_graph()
    
    state = State(
      messages=[HumanMessage(content=query)],
      next="",
      full_plan="",
      TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
    )
    
    # Send initial state
    initial_state = {
        "type": "state_update",
        "messages": [format_message(state["messages"][0])],
        "current_node": "starting"
    }
    yield json.dumps(initial_state)
    
    # Execute the workflow with streaming
    previous_messages_count = 1  # Starting with one human message
    
    # Stream each state update
    print("Starting to stream workflow...")
    async for chunk in graph.astream(state):
        # 打印原始块用于调试
        print(f"DEBUG: Received chunk: {list(chunk.keys())}")
        if "messages" in chunk:
            print(f"DEBUG: Messages count: {len(chunk['messages'])}")
        if "next" in chunk:
            print(f"DEBUG: Next node: {chunk['next']}")
        # Get new messages that weren't in the previous state
        if "messages" in chunk:
            current_messages = chunk["messages"]
            
            if len(current_messages) > previous_messages_count:
                new_messages = current_messages[previous_messages_count:]
                for msg in new_messages:
                    message_data = {
                        "type": "message",
                        "message": format_message(msg)
                    }
                    yield json.dumps(message_data)
                    await asyncio.sleep(0.1)  # Small delay for better visualization
                
                previous_messages_count = len(current_messages)
        
        # Send node update if available
        if "next" in chunk and chunk["next"]:
            node_data = {
                "type": "node_update",
                "node": chunk["next"]
            }
            yield json.dumps(node_data)
    
    # Send final state
    if "messages" in chunk:
        final_state = {
            "type": "completion",
            "final_messages": [format_message(msg) for msg in chunk["messages"]]
        }
        yield json.dumps(final_state)


def run_workflow(query):
    """Run the LangGraph workflow with a query (non-streaming version)."""
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

async def main_async(user_query):
    """Async main function for streaming output."""
    # Run the workflow with streaming
    print("\n=== Streaming Workflow Execution ===")
    async for chunk in run_workflow_stream(user_query):
        # Parse the JSON chunk
        data = json.loads(chunk)
        
        # Format output based on chunk type
        if data["type"] == "state_update":
            print(f"Starting workflow with query: {data['messages'][0]['content']}")
            
        elif data["type"] == "message":
            msg = data["message"]
            print(f"[{msg['role']}]: {msg['content']}")
            
        elif data["type"] == "node_update":
            print(f"\nMoving to node: {data['node']}\n")
            
        elif data["type"] == "completion":
            print("\n=== Workflow Complete ===")


def main():
    """Main function entry point."""
    # 只获取一次输入
    if len(sys.argv) > 1:
        user_query = " ".join(sys.argv[1:])
    else:
        user_query = input("Enter your query: ")
    
    print("\n=== User Query ===")
    print(user_query)
    
    # Check if we want streaming mode
    streaming_mode = True  # 默认使用流式模式
    
    if streaming_mode:
        # 运行异步流式模式，传入已经获取的查询
        asyncio.run(main_async(user_query))
    else:
        # 运行非流式模式
        run_workflow(user_query)

if __name__ == "__main__":
    main()
