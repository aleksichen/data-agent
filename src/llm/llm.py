"""
LLM client management module.
"""
import os
from typing import Optional, Any, Dict

from src.llm.handlers.factory import create_api_handler
from src.llm.handlers.deepseek import DeepSeekHandler

# LLM 类型到具体模型的映射
LLM_TYPE_MODEL_MAP = {
    "basic": "deepseek-chat",     # 普通任务用 deepseek-chat
    "reasoning": "deepseek-reasoner"  # 推理任务用 deepseek-reasoner
}

def get_llm_by_type(llm_type: str, mock_llm: Optional[Any] = None):
    """
    根据类型获取LLM实例，支持在测试时注入模拟LLM。
    
    Args:
        llm_type: LLM类型，例如 "basic"、"reasoning" 等
        mock_llm: 用于测试的模拟LLM实例
        
    Returns:
        LLM实例
    """
    # 如果提供了模拟LLM，直接返回它（用于测试）
    if mock_llm:
        return mock_llm
    
    # 从环境变量获取API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    # 如果没有API密钥，返回模拟LLM
    if not api_key:
        print("警告: 未设置DEEPSEEK_API_KEY环境变量，使用模拟LLM")
        return _get_mock_llm()
    
    # 根据llm_type获取对应的模型名称
    model_name = LLM_TYPE_MODEL_MAP.get(llm_type, "deepseek-chat")
    
    # 创建配置
    config = {
        "api_provider": "deepseek",
        "api_key": api_key,
        "model_name": model_name
    }
    
    # 创建API处理器
    handler = create_api_handler(config)
    
    # 包装API处理器为LangChain兼容的LLM客户端
    return LangChainCompatibleLLM(handler)


class LangChainCompatibleLLM:
    """
    包装API处理器为LangChain兼容的LLM客户端。
    """
    
    def __init__(self, handler):
        """
        初始化LLM客户端。
        
        Args:
            handler: API处理器实例
        """
        self.handler = handler
    
    def invoke(self, messages):
        """
        同步调用LLM。
        
        Args:
            messages: 消息列表，包含系统提示和用户消息
            
        Returns:
            AIMessage: LLM响应
        """
        import asyncio
        from langchain_core.messages import AIMessage, SystemMessage
        
        # 提取系统提示
        system_prompt = ""
        user_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_prompt = msg.content
            else:
                # 转换为处理器可以理解的格式
                role = "user"  # 默认角色
                if hasattr(msg, "type"):
                    # 转换LangChain消息类型为DeepSeek可接受的role值
                    if msg.type == "human":
                        role = "user"
                    elif msg.type == "ai":
                        role = "assistant"
                    else:
                        role = msg.type  # 可能是tool或其他DeepSeek支持的类型
                elif hasattr(msg, "name") and msg.name == "assistant":
                    role = "assistant"
                
                user_messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        # 如果没有找到系统提示，使用第一条消息作为系统提示
        if not system_prompt and user_messages:
            system_prompt = user_messages[0]["content"]
            user_messages = user_messages[1:]
        
        # 创建异步任务并运行
        async def _async_invoke():
            stream = await self.handler.create_message(system_prompt, user_messages)
            
            # 收集完整响应
            full_response = ""
            async for chunk in stream:
                if "delta" in chunk:
                    full_response += chunk["delta"]
            
            return full_response
        
        # 运行异步任务
        try:
            # 先尝试创建新的事件循环
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                response_text = new_loop.run_until_complete(_async_invoke())
            finally:
                new_loop.close()
        except Exception as e:
            print(f"警告: 异步调用错误: {e}")
            # 如果发生错误，尝试使用简单的asyncio.run()
            response_text = asyncio.run(_async_invoke())
        
        # 返回AIMessage
        return AIMessage(content=response_text)
    
    def stream(self, messages):
        """
        流式调用LLM。
        
        Args:
            messages: 消息列表，包含系统提示和用户消息
            
        Returns:
            生成器，产生响应块
        """
        import asyncio
        from langchain_core.messages import SystemMessage
        
        # 提取系统提示
        system_prompt = ""
        user_messages = []
        
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_prompt = msg.content
            else:
                # 转换为处理器可以理解的格式
                role = "user"  # 默认角色
                if hasattr(msg, "type"):
                    # 转换LangChain消息类型为DeepSeek可接受的role值
                    if msg.type == "human":
                        role = "user"
                    elif msg.type == "ai":
                        role = "assistant"
                    else:
                        role = msg.type  # 可能是tool或其他DeepSeek支持的类型
                elif hasattr(msg, "name") and msg.name == "assistant":
                    role = "assistant"
                
                user_messages.append({
                    "role": role,
                    "content": msg.content
                })
        
        # 如果没有找到系统提示，使用第一条消息作为系统提示
        if not system_prompt and user_messages:
            system_prompt = user_messages[0]["content"]
            user_messages = user_messages[1:]
        
        # 创建异步任务
        async def _async_stream():
            stream = await self.handler.create_message(system_prompt, user_messages)
            
            async for chunk in stream:
                if "delta" in chunk:
                    yield type('obj', (object,), {'content': chunk["delta"]})
        
        # 返回一个同步生成器包装
        def _sync_stream():
            try:
                # 创建新的事件循环
                new_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(new_loop)
                try:
                    chunks = new_loop.run_until_complete(_async_stream_collect())
                    for chunk in chunks:
                        yield chunk
                finally:
                    new_loop.close()
            except Exception as e:
                print(f"流式调用错误: {e}")
                yield type('obj', (object,), {'content': f"错误: {str(e)}"})
        
        # 辅助函数：收集所有块
        async def _async_stream_collect():
            chunks = []
            try:
                async for chunk in _async_stream():
                    chunks.append(chunk)
            except Exception as e:
                print(f"收集流式数据错误: {e}")
                chunks.append(type('obj', (object,), {'content': f"错误: {str(e)}"}))  
            return chunks
        
        return _sync_stream()
    
    def with_structured_output(self, schema, method=None):
        """
        配置LLM以生成结构化输出。
        
        Args:
            schema: 输出的JSON模式
            method: 结构化输出方法
            
        Returns:
            self: 配置了结构化输出的LLM实例
        """
        # 这里简单地返回自身，实际应用中可能需要更复杂的处理
        return self


def _get_mock_llm():
    """
    返回一个简单的模拟LLM实例。
    
    Returns:
        模拟的LLM对象
    """
    class DefaultLLM:
        def invoke(self, messages):
            from langchain_core.messages import AIMessage
            return AIMessage(content="这是默认LLM响应（未配置API密钥）")
            
        def stream(self, messages):
            return [type('obj', (object,), {'content': "这是默认LLM流式响应（未配置API密钥）"})]
            
        def with_structured_output(self, schema, method=None):
            return self
    
    return DefaultLLM()
