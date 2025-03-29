"""
测试脚本 - LangGraph工作流测试
此脚本展示如何测试基于LangGraph的完整工作流，重点关注协调员节点功能
"""

import sys
import asyncio
from pathlib import Path
from langchain_core.messages import HumanMessage

# 确保src目录在Python路径中
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.graph.builder import build_graph
from src.graph.types import State


# 测试用户输入
TEST_INPUTS = [
    "你好，我是新用户",  # 简单问候
    "能帮我分析一下这个CSV文件中的销售数据吗？"  # 复杂任务
]


async def run_workflow_test():
    """运行工作流测试"""
    # 构建工作流图
    workflow = build_graph()
    
    # 创建初始状态
    state = State(
        messages=[],
        next="",
        full_plan="",
        deep_thinking_mode=False,
        search_before_planning=False,
        TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
    )
    
    # 依次处理测试输入
    for i, user_input in enumerate(TEST_INPUTS):
        print(f"\n===== 测试输入 {i+1}: {user_input} =====")
        
        # 添加用户消息
        current_state = State(**state)
        current_state["messages"].append(HumanMessage(content=user_input))
        
        # 执行工作流
        async for event, result in workflow.astream(current_state):
            # 只打印节点转换事件
            if event.event_type == "on_chain_start":
                print(f"开始执行节点: {event.name}")
            
            if event.event_type == "on_chain_end":
                # 获取最终状态
                final_state = result
                
                # 打印AI回复
                messages = final_state.get("messages", [])
                for msg in messages:
                    if not isinstance(msg, HumanMessage) and msg not in state.get("messages", []):
                        print(f"AI回复: {msg.content}")
                        print(f"来自: {getattr(msg, 'name', 'unknown')}")
        
        # 更新状态
        state = result


if __name__ == "__main__":
    # 运行测试
    asyncio.run(run_workflow_test())
