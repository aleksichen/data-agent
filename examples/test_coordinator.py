"""
测试脚本 - 协调员智能体功能
此脚本展示如何独立测试协调员节点功能
"""

import sys
import asyncio
import json
from pathlib import Path
from unittest.mock import MagicMock
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 确保src目录在Python路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.nodes.coordinator import coordinator_node
from src.graph.types import State
from src.llm.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP

# 示例用户输入
TEST_INPUTS = [
    "你好，我是新用户",
    "今天天气怎么样？",
    "能帮我分析一下这个CSV文件中的销售数据吗？我需要了解销售趋势和预测。",
    "写一个Python程序来处理图像分类任务",
]


def create_mock_llm(is_complex_task):
    """创建模拟LLM响应"""
    mock_llm = MagicMock()
    
    if is_complex_task:
        mock_llm.invoke.return_value = AIMessage(content="handoff_to_planner()")
    else:
        mock_llm.invoke.return_value = AIMessage(
            content="你好！我是DataAgent，很高兴为您服务。有什么我可以帮助您的吗？"
        )
    
    return mock_llm


def test_coordinator_with_mock():
    """使用模拟LLM测试协调员智能体"""
    for i, user_input in enumerate(TEST_INPUTS):
        print(f"\n===== 测试输入 {i+1}: {user_input} =====")
        
        # 根据输入类型决定是否为复杂任务
        is_complex = i >= 2  # 前两个是简单任务，后两个是复杂任务
        mock_llm = create_mock_llm(is_complex)
        
        # 创建状态
        state = State(
            messages=[HumanMessage(content=user_input)],
            next="",
            full_plan="",
            deep_thinking_mode=False,
            search_before_planning=False,
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # 替换get_llm_by_type函数返回我们的mock
        original_get_llm = get_llm_by_type
        try:
            # 注入模拟LLM
            globals()["get_llm_by_type"] = lambda _: mock_llm
            
            # 调用协调员节点
            result = coordinator_node(state)
            
            # 打印结果
            print(f"转到: {result.goto}")
            if 'messages' in result.update:
                for msg in result.update['messages']:
                    if not isinstance(msg, HumanMessage):  # 只打印非用户消息
                        print(f"回复: {msg.content}")
            
        finally:
            # 恢复原始函数
            globals()["get_llm_by_type"] = original_get_llm


def test_coordinator_real():
    """使用真实LLM测试协调员智能体"""
    for i, user_input in enumerate(TEST_INPUTS):
        print(f"\n===== 测试输入 {i+1}: {user_input} =====")
        
        # 创建状态
        state = State(
            messages=[HumanMessage(content=user_input)],
            next="",
            full_plan="",
            deep_thinking_mode=False,
            search_before_planning=False,
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # 调用协调员节点
        result = coordinator_node(state)
        
        # 打印结果
        print(f"转到: {result.goto}")
        if 'messages' in result.update:
            for msg in result.update['messages']:
                if not isinstance(msg, HumanMessage):  # 只打印非用户消息
                    print(f"回复: {msg.content}")


if __name__ == "__main__":
    # print("=== 使用模拟LLM测试协调员 ===")
    # test_coordinator_with_mock()
    
    print("\n\n=== 使用真实LLM测试协调员 ===")
    try:
        test_coordinator_real()
    except Exception as e:
        print(f"真实LLM测试失败: {e}")
