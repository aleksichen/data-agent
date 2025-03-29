from langgraph.graph import StateGraph, START

from src.graph.types import State
from src.graph.nodes import (
    supervisor_node,
    research_node,
    code_node,
    coordinator_node,
    browser_node,
    reporter_node,
    planner_node,
)


def build_graph():
    """构建并返回智能体工作流图。"""
    builder = StateGraph(State)
    
    # 添加边和节点
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("planner", planner_node)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("researcher", research_node)
    builder.add_node("coder", code_node)
    builder.add_node("browser", browser_node)
    builder.add_node("reporter", reporter_node)
    
    return builder.compile()
