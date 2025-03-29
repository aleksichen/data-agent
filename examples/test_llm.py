"""
测试LLM集成脚本
这个脚本用于测试不同类型的LLM调用
"""

import os
import sys
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage

# 确保src目录在Python路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.llm import get_llm_by_type


def test_llm_types():
    """测试不同类型的LLM调用"""
    
    # 检查是否设置了API密钥
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("警告: 未设置DEEPSEEK_API_KEY环境变量，将使用模拟LLM")
        print("请设置环境变量: export DEEPSEEK_API_KEY=your_api_key_here")
    
    # 测试基本LLM (deepseek-chat)
    print("\n===== 测试基本LLM (deepseek-chat) =====")
    basic_llm = get_llm_by_type("basic")
    
    messages = [
        SystemMessage(content="你是一个友好的AI助手，提供简洁明了的回答。"),
        HumanMessage(content="你好，介绍一下自己。")
    ]
    
    print("调用LLM...")
    response = basic_llm.invoke(messages)
    print(f"基本LLM响应:\n{response.content}\n")
    
    # 测试推理LLM (deepseek-reasoner)
    print("\n===== 测试推理LLM (deepseek-reasoner) =====")
    reasoning_llm = get_llm_by_type("reasoning")
    
    messages = [
        SystemMessage(content="你是一个善于逻辑思考的AI助手，分步骤解决问题。"),
        HumanMessage(content="解释一下如何计算斐波那契数列的第10个数字。")
    ]
    
    print("调用LLM...")
    response = reasoning_llm.invoke(messages)
    print(f"推理LLM响应:\n{response.content}\n")
    
    # 测试流式调用
    print("\n===== 测试流式调用 =====")
    messages = [
        SystemMessage(content="你是一个友好的AI助手。"),
        HumanMessage(content="用三句话描述量子计算。")
    ]
    
    print("流式调用LLM...")
    for chunk in basic_llm.stream(messages):
        print(chunk.content, end="", flush=True)
    print("\n")
    
    print("===== 测试完成 =====")


if __name__ == "__main__":
    test_llm_types()
