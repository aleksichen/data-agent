#!/usr/bin/env python
"""
测试脚本：输出完整的 planner 提示内容
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目根目录到 Python 路径
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

from src.config import TEAM_MEMBERS
from langchain_core.messages import HumanMessage, SystemMessage
from src.graph.types import State

# 直接获取提示模板
def get_prompt_template_raw(template_name):
    """获取原始提示模板内容"""
    template_path = os.path.join(project_root, 'src', 'prompts', f'{template_name}.md')
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error loading template {template_name}: {e}"

def main():
    """主函数：获取并显示 planner 提示内容"""
    print("=== 正在生成 Planner 提示内容 ===\n")
    
    # 获取原始提示模板
    raw_template = get_prompt_template_raw('planner')
    
    # 格式化模板中的变量
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_template = raw_template.replace("{{ CURRENT_TIME }}", current_time)
    
    # 手动替换 TEAM_MEMBERS 变量
    team_members_text = ", ".join(TEAM_MEMBERS)
    formatted_template = formatted_template.replace("{{ TEAM_MEMBERS|join(\", \") }}", team_members_text)
    
    # 模拟 planner 节点的状态
    state = State(
        messages=[HumanMessage(content="我想开发一个React Todo List应用，可以帮我做个任务规划吗？")],
        next="",
        full_plan="",
        TEAM_MEMBERS=TEAM_MEMBERS
    )
    
    # 创建完整的提示消息
    messages = [
        SystemMessage(content=formatted_template),
        HumanMessage(content=state["messages"][0].content)
    ]
    
    # 打印完整的提示内容
    print("=== 系统提示 ===")
    print(messages[0].content)
    print("\n=== 用户消息 ===")
    print(messages[1].content)
    
    print("\n=== TEAM_MEMBERS 列表 ===")
    for member in TEAM_MEMBERS:
        print(f"- {member}")
    
    print("\n这个提示内容将用于调用 LLM 生成任务计划。")

if __name__ == "__main__":
    main()
