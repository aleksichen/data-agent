"""
测试特定消息格式的LLM调用
"""

import os
import sys
import json
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 确保src目录在Python路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.llm import get_llm_by_type
from src.llm.handlers.deepseek import DeepSeekHandler

def test_messages():
    """测试消息格式转换和传递"""
    
    # 检查是否设置了API密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("警告: 未设置DEEPSEEK_API_KEY环境变量")
        print("请设置环境变量: export DEEPSEEK_API_KEY=your_api_key_here")
        return
    
    # 创建简单的消息列表
    messages = [
        SystemMessage(content="你是一个友好的AI助手。"),
        HumanMessage(content="你好！"),
        AIMessage(content="你好！有什么可以帮助你的吗？"),
        HumanMessage(content="解释一下什么是人工智能。")
    ]
    
    # 直接使用DeepSeek处理器进行测试
    print("\n===== 直接使用DeepSeek处理器测试消息格式 =====")
    config = {
        "api_key": api_key,
        "model_name": "deepseek-chat"
    }
    
    handler = DeepSeekHandler(config)
    
    # 提取系统提示和用户消息
    system_prompt = messages[0].content
    user_messages = []
    
    for msg in messages[1:]:
        if isinstance(msg, HumanMessage):
            user_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            user_messages.append({"role": "assistant", "content": msg.content})
    
    print(f"系统提示: {system_prompt}")
    print(f"用户消息: {json.dumps(user_messages, ensure_ascii=False, indent=2)}")
    
    # 使用get_llm_by_type函数测试
    print("\n===== 使用get_llm_by_type函数测试 =====")
    llm = get_llm_by_type("basic")
    
    print("调用LLM...")
    response = llm.invoke(messages)
    print(f"响应:\n{response.content}")

if __name__ == "__main__":
    test_messages()
