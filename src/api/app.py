import asyncio
from enum import Enum
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional, Union
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette import EventSourceResponse

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import and include LangGraph routes
from src.api.langgraph_routes import router as langgraph_router
app.include_router(langgraph_router, prefix="/api")

class MessageType(str, Enum):
    THINKING = "thinking"           # 思考过程
    TOOL_CALL = "tool_call"         # 工具调用
    TOOL_RESULT = "tool_result"     # 工具调用结果
    FINAL_ANSWER = "final_answer"   # 最终答案
    ERROR = "error"                 # 错误信息

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = True
    tools: Optional[List[Dict[str, Any]]] = None
    temperature: Optional[float] = 0.7

class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]

# 模拟的知识库工具
async def knowledge_base_tool(query: str):
    await asyncio.sleep(1.5)  # 模拟网络延迟
    return {
        "documents": [
            {"title": "产品文档", "content": f"这是关于'{query}'的产品信息..."},
            {"title": "用户指南", "content": f"如何使用'{query}'的详细说明..."}
        ],
        "total_results": 2
    }

# 模拟的搜索工具
async def search_tool(query: str, limit: int = 3):
    await asyncio.sleep(2)  # 模拟网络延迟
    return {
        "results": [
            {"title": f"搜索结果 1 - {query}", "url": "https://example.com/1"},
            {"title": f"搜索结果 2 - {query}", "url": "https://example.com/2"},
            {"title": f"搜索结果 3 - {query}", "url": "https://example.com/3"}
        ][:limit],
        "total_results": limit
    }

# 模拟的计算工具
async def calculator_tool(expression: str):
    await asyncio.sleep(0.5)  # 模拟计算延迟
    try:
        result = eval(expression)
        return {"result": result}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    """模拟的聊天流式响应API"""
    
    async def event_generator():
        session_id = str(uuid.uuid4())
        
        # 获取用户的最后一条消息
        if not chat_request.messages:
            yield {"event": MessageType.ERROR, "data": json.dumps({"error": "没有提供消息"})}
            return
            
        last_message = chat_request.messages[-1]
        if last_message.role != "user":
            yield {"event": MessageType.ERROR, "data": json.dumps({"error": "最后一条消息不是用户消息"})}
            return
        
        query = last_message.content
        
        # 1. 发送思考过程
        await asyncio.sleep(0.8)
        yield {
            "event": MessageType.THINKING, 
            "data": json.dumps({
                "session_id": session_id,
                "content": "我正在分析您的问题...",
                "timestamp": time.time()
            })
        }
        
        # 根据查询内容决定使用什么工具
        if "搜索" in query or "查找" in query:
            # 2. 发送工具调用信息 - 搜索
            tool_name = "search"
            tool_params = {"query": query, "limit": 3}
            await asyncio.sleep(0.5)
            yield {
                "event": MessageType.TOOL_CALL,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "params": tool_params,
                    "timestamp": time.time()
                })
            }
            
            # 3. 执行工具调用并发送结果
            tool_result = await search_tool(**tool_params)
            yield {
                "event": MessageType.TOOL_RESULT,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "result": tool_result,
                    "timestamp": time.time()
                })
            }
            
        elif "计算" in query or any(op in query for op in ["+", "-", "*", "/"]):
            # 尝试提取表达式
            import re
            expression_match = re.search(r'(\d+[\+\-\*\/\d\s\(\)\.]+\d+)', query)
            expression = expression_match.group(1) if expression_match else "1+2"
            
            # 调用计算工具
            tool_name = "calculator"
            tool_params = {"expression": expression}
            await asyncio.sleep(0.5)
            yield {
                "event": MessageType.TOOL_CALL,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "params": tool_params,
                    "timestamp": time.time()
                })
            }
            
            # 执行计算并返回结果
            tool_result = await calculator_tool(**tool_params)
            yield {
                "event": MessageType.TOOL_RESULT,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "result": tool_result,
                    "timestamp": time.time()
                })
            }
            
        else:
            # 默认使用知识库查询
            tool_name = "knowledge_base"
            tool_params = {"query": query}
            await asyncio.sleep(0.5)
            yield {
                "event": MessageType.TOOL_CALL,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "params": tool_params,
                    "timestamp": time.time()
                })
            }
            
            # 查询知识库并返回结果
            tool_result = await knowledge_base_tool(**tool_params)
            yield {
                "event": MessageType.TOOL_RESULT,
                "data": json.dumps({
                    "session_id": session_id,
                    "tool": tool_name,
                    "result": tool_result,
                    "timestamp": time.time()
                })
            }
        
        # 4. 再次思考（基于工具结果）
        await asyncio.sleep(1)
        yield {
            "event": MessageType.THINKING,
            "data": json.dumps({
                "session_id": session_id,
                "content": "我已经获取到相关信息，正在整理答案...",
                "timestamp": time.time()
            })
        }
        
        # 5. 最终答案 - 模拟生成流式文本，一个词一个词地返回
        answer_parts = [
            "根据我查询到的信息，",
            "您的问题的答案是：",
            "这是一个模拟的回复，",
            "展示了Agent的工作过程。",
            "实际的回答会基于工具调用的结果，",
            "并提供更有价值的信息。"
        ]
        
        final_answer = {
            "session_id": session_id,
            "content": "",
            "timestamp": time.time(),
            "finished": False
        }
        
        for part in answer_parts:
            final_answer["content"] += part
            final_answer["finished"] = False
            yield {
                "event": MessageType.FINAL_ANSWER,
                "data": json.dumps(final_answer)
            }
            await asyncio.sleep(0.3)  # 模拟思考和打字的延迟
        
        # 标记回答完成
        final_answer["finished"] = True
        yield {
            "event": MessageType.FINAL_ANSWER,
            "data": json.dumps(final_answer)
        }
    
    return EventSourceResponse(event_generator())
