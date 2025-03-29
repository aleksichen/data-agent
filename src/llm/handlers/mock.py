"""
模拟LLM处理器，用于测试。
"""
from typing import Dict, List, Any, Optional

import logging

logger = logging.getLogger(__name__)

class MockLLMHandler:
    """模拟LLM API处理器，用于测试环境。"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化模拟LLM处理器。
        
        Args:
            config: 配置参数
        """
        self.config = config or {}
        logger.info("初始化模拟LLM处理器")
        print("DEBUG: 使用模拟LLM处理器")
    
    async def create_message(self, system_prompt: str, messages: List[Dict[str, str]]):
        """
        模拟创建消息请求。
        
        Args:
            system_prompt: 系统提示文本
            messages: 消息列表
            
        Returns:
            一个产生模拟响应块的异步生成器
        """
        print(f"DEBUG: 模拟LLM收到系统提示: {system_prompt[:50]}...")
        
        if not messages:
            yield {"delta": "没有收到用户消息"}
            return
        
        # 获取最后一条用户消息
        last_message = messages[-1]
        user_input = last_message.get("content", "")
        
        print(f"DEBUG: 模拟LLM收到用户消息: {user_input}")
        
        # 根据关键词生成不同的响应
        if "你好" in user_input or "hello" in user_input.lower():
            response = "你好！我是DataAgent，一个智能助手。有什么我可以帮到你的吗？"
        elif "帮我" in user_input or "开发" in user_input or "编程" in user_input:
            response = "handoff_to_planner()"
        else:
            response = "我是DataAgent。我可以回答问题，或者将复杂任务转交给专门的规划员处理。"
        
        # 模拟流式返回
        for char in response:
            yield {"delta": char}
            import asyncio
            await asyncio.sleep(0.01)
