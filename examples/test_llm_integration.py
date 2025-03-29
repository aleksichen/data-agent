"""
综合测试 LLM 集成
这个脚本测试 LLM 集成的各个方面，包括:
1. 消息格式转换
2. 简单和复杂任务的处理
3. coordinator_node 使用 LLM
"""

import os
import sys
from pathlib import Path
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 确保src目录在Python路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm.llm import get_llm_by_type
from src.config.agents import AGENT_LLM_MAP
from src.graph.nodes.coordinator import coordinator_node
from src.graph.types import State
from src.llm.transform.openai_format import convert_to_openai_messages


def test_format_conversion():
    """测试消息格式转换"""
    print("\n===== 测试消息格式转换 =====")
    
    # 测试 LangChain 消息转换
    messages = [
        SystemMessage(content="你是一个友好的AI助手。"),
        HumanMessage(content="你好！"),
        AIMessage(content="你好！有什么可以帮助你的吗？")
    ]
    
    openai_format = convert_to_openai_messages(messages)
    print("LangChain 消息转换:")
    for msg in openai_format:
        print(f"  角色: {msg['role']}, 内容: {msg['content'][:30]}...")


def test_basic_llm():
    """测试基本LLM调用"""
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("\n⚠️ 未设置DEEPSEEK_API_KEY环境变量，跳过LLM调用测试")
        return
    
    print("\n===== 测试基本LLM调用 =====")
    
    # 获取基本LLM
    llm = get_llm_by_type("basic")
    
    # 准备消息
    messages = [
        SystemMessage(content="你是一个友好的AI助手，提供简洁明了的回答。"),
        HumanMessage(content="用一句话介绍一下自己。")
    ]
    
    # 调用LLM
    print("调用LLM...")
    try:
        response = llm.invoke(messages)
        print(f"响应: {response.content}")
    except Exception as e:
        print(f"调用失败: {e}")


def test_reasoning_llm():
    """测试推理LLM调用"""
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("\n⚠️ 未设置DEEPSEEK_API_KEY环境变量，跳过LLM调用测试")
        return
    
    print("\n===== 测试推理LLM调用 =====")
    
    # 获取推理LLM
    llm = get_llm_by_type("reasoning")
    
    # 准备消息
    messages = [
        SystemMessage(content="你是一个逻辑思考能力很强的AI助手。"),
        HumanMessage(content="如果8个人需要5天完成一项工作，那么4个人需要多少天完成同样的工作？")
    ]
    
    # 调用LLM
    print("调用LLM...")
    try:
        response = llm.invoke(messages)
        print(f"响应: {response.content}")
    except Exception as e:
        print(f"调用失败: {e}")


def test_coordinator_node():
    """测试协调员节点与LLM集成"""
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("\n⚠️ 未设置DEEPSEEK_API_KEY环境变量，跳过协调员测试")
        return
    
    print("\n===== 测试协调员节点与LLM集成 =====")
    
    # 测试简单任务
    print("\n--- 简单任务 ---")
    state = State(
        messages=[HumanMessage(content="你好，请介绍一下自己。")],
        next="",
        full_plan="",
        deep_thinking_mode=False,
        search_before_planning=False,
        TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
    )
    
    # 调用协调员节点
    try:
        result = coordinator_node(state)
        print(f"转到: {result.goto}")
        if 'messages' in result.update:
            for msg in result.update['messages']:
                if not isinstance(msg, HumanMessage):  # 只打印非用户消息
                    print(f"回复: {msg.content}")
    except Exception as e:
        print(f"协调员节点调用失败: {e}")
    
    # 测试复杂任务
    print("\n--- 复杂任务 ---")
    state = State(
        messages=[HumanMessage(content="帮我分析这个CSV文件中的销售趋势并创建一个可视化。")],
        next="",
        full_plan="",
        deep_thinking_mode=False,
        search_before_planning=False,
        TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
    )
    
    # 调用协调员节点
    try:
        result = coordinator_node(state)
        print(f"转到: {result.goto}")
        if 'messages' in result.update:
            for msg in result.update['messages']:
                if not isinstance(msg, HumanMessage):  # 只打印非用户消息
                    print(f"回复: {msg.content}")
    except Exception as e:
        print(f"协调员节点调用失败: {e}")


if __name__ == "__main__":
    # 运行各项测试
    test_format_conversion()
    test_basic_llm()
    test_reasoning_llm()
    test_coordinator_node()
    
    print("\n===== 测试完成 =====")
