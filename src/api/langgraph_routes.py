import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette import EventSourceResponse
from langchain_core.messages import HumanMessage

from src.graph.builder import build_graph
from src.graph.types import State
from src.api.app import MessageType, Message

logger = logging.getLogger(__name__)

router = APIRouter()

class LangGraphRequest(BaseModel):
    messages: List[Message]
    stream: bool = True

@router.post("/langgraph/chat")
async def langgraph_chat(request: Request, chat_request: LangGraphRequest):
    """LangGraph-based chat API with streaming."""
    
    async def event_generator():
        session_id = str(uuid.uuid4())
        
        # Get the user's last message
        if not chat_request.messages:
            yield {"event": MessageType.ERROR, "data": json.dumps({"error": "No messages provided"})}
            return
            
        last_message = chat_request.messages[-1]
        if last_message.role != "user":
            yield {"event": MessageType.ERROR, "data": json.dumps({"error": "Last message is not from user"})}
            return
        
        query = last_message.content
        
        # Create the workflow
        graph = build_graph()
        
        # Initialize state
        state = State(
            messages=[HumanMessage(content=query)],
            next="",
            full_plan="",
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # Send initial state
        yield {
            "event": MessageType.THINKING, 
            "data": json.dumps({
                "session_id": session_id,
                "content": "开始处理您的请求...",
                "timestamp": time.time()
            })
        }
        
        # Track message index to detect new messages
        prev_msg_count = 1  # Start with one human message
        current_node = "coordinator"
        
        try:
            # Stream the workflow execution
            async for chunk in graph.astream(state):
                # Process new messages
                if "messages" in chunk and len(chunk["messages"]) > prev_msg_count:
                    # Get only new messages
                    new_messages = chunk["messages"][prev_msg_count:]
                    for msg in new_messages:
                        # Format the message for streaming
                        if hasattr(msg, 'name') and msg.name:
                            role = msg.name
                        else:
                            role = msg.__class__.__name__.replace('Message', '')
                        
                        # Send the message
                        yield {
                            "event": MessageType.THINKING,
                            "data": json.dumps({
                                "session_id": session_id,
                                "content": f"[{role}]: {msg.content}",
                                "timestamp": time.time()
                            })
                        }
                        await asyncio.sleep(0.3)  # Small delay for better visualization
                    
                    prev_msg_count = len(chunk["messages"])
                
                # Track node transitions
                if "next" in chunk and chunk["next"] and chunk["next"] != current_node:
                    current_node = chunk["next"]
                    yield {
                        "event": "node_update",
                        "data": json.dumps({
                            "session_id": session_id,
                            "node": current_node,
                            "timestamp": time.time()
                        })
                    }
            
            # Send final response - last AI message
            last_ai_message = None
            for msg in reversed(chunk["messages"]):
                if hasattr(msg, 'name') and msg.name:
                    last_ai_message = msg.content
                    last_role = msg.name
                    break
            
            if not last_ai_message:
                last_ai_message = "处理完成，但没有生成响应。"
                last_role = "system"
            
            # Final answer
            yield {
                "event": MessageType.FINAL_ANSWER,
                "data": json.dumps({
                    "session_id": session_id,
                    "content": last_ai_message,
                    "role": last_role,
                    "timestamp": time.time(),
                    "finished": True
                })
            }
            
        except Exception as e:
            logger.error(f"Error in LangGraph workflow: {str(e)}")
            yield {
                "event": MessageType.ERROR,
                "data": json.dumps({
                    "error": f"Error in workflow execution: {str(e)}",
                    "timestamp": time.time()
                })
            }
    
    return EventSourceResponse(event_generator())
