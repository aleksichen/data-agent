import asyncio
import json
import logging
import time
import uuid
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

from src.graph import create_agent_workflow
from src.api.app import MessageType, Message

logger = logging.getLogger(__name__)

router = APIRouter()

class LangGraphRequest(BaseModel):
    messages: List[Message]
    stream: bool = True

@router.post("/langgraph/chat")
async def langgraph_chat(request: Request, chat_request: LangGraphRequest):
    """LangGraph-based chat API."""
    
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
        workflow = create_agent_workflow()
        
        # 1. Send thinking process
        yield {
            "event": MessageType.THINKING, 
            "data": json.dumps({
                "session_id": session_id,
                "content": "Analyzing your question with LangGraph workflow...",
                "timestamp": time.time()
            })
        }
        
        # 2. Run the workflow
        try:
            # Initialize state with the query
            state = {"query": query, "thoughts": [], "response": None}
            
            # Execute the workflow
            result = workflow.invoke(state)
            
            # Get thoughts for streaming
            thoughts = result.get("thoughts", [])
            for thought in thoughts:
                await asyncio.sleep(0.5)  # Simulate thinking delay
                yield {
                    "event": MessageType.THINKING,
                    "data": json.dumps({
                        "session_id": session_id,
                        "content": thought,
                        "timestamp": time.time()
                    })
                }
            
            # 3. Final answer
            final_response = result.get("response", "No response generated")
            
            # Stream the final answer
            yield {
                "event": MessageType.FINAL_ANSWER,
                "data": json.dumps({
                    "session_id": session_id,
                    "content": final_response,
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
