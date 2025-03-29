"""
测试模拟LLM的脚本。
"""
import os
import sys
import asyncio
from pathlib import Path

# 将父目录添加到 Python 路径
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

from langchain_core.messages import HumanMessage, SystemMessage
from src.llm.llm import get_llm_by_type

async def main():
    """测试模拟LLM的主函数。"""
    print("=== 测试模拟LLM ===")
    
    # 获取基础LLM
    llm = get_llm_by_type("basic")
    
    # 创建测试消息
    system_prompt = "你是一个友好的人工智能助手。"
    test_messages = [
        {"query": "你好", "expected": "友好的问候"},
        {"query": "帮我开发一个网站", "expected": "转交给规划员"},
        {"query": "今天天气怎么样", "expected": "一般回答"}
    ]
    
    # 执行测试
    for test in test_messages:
        print(f"\n测试查询: {test['query']}")
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=test["query"])
        ]
        
        response = llm.invoke(messages)
        print(f"响应: {response.content}")
        print(f"预期类型: {test['expected']}")

if __name__ == "__main__":
    asyncio.run(main())
