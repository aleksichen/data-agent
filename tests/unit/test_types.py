import pytest
from typing import get_type_hints, get_args, get_origin

def test_router_type():
    """测试Router类型定义是否正确"""
    from src.graph.types import Router, OPTIONS
    
    # 获取Router类的类型提示
    type_hints = get_type_hints(Router)
    
    # 验证Router类有next字段
    assert "next" in type_hints
    
    # 验证next字段是Literal类型
    next_type = type_hints["next"]
    assert get_origin(next_type).__name__ == "Literal"
    
    # 验证Literal中包含所有团队成员和FINISH
    literal_args = get_args(next_type)
    for option in OPTIONS:
        assert option in literal_args


def test_state_type():
    """测试State类型定义是否正确"""
    from src.graph.types import State
    
    # 获取State类的类型提示
    type_hints = get_type_hints(State)
    
    # 验证State类有必要的字段
    assert "next" in type_hints
    assert "full_plan" in type_hints
    assert "deep_thinking_mode" in type_hints
    assert "search_before_planning" in type_hints
    
    # 验证字段类型
    assert type_hints["next"] == str
    assert type_hints["full_plan"] == str
    assert type_hints["deep_thinking_mode"] == bool
    assert type_hints["search_before_planning"] == bool


def test_state_instantiation():
    """测试State类是否能正确实例化"""
    from src.graph.types import State
    from langchain_core.messages import HumanMessage
    
    # 创建一个State实例
    state = State(
        messages=[HumanMessage(content="测试消息")],
        next="planner",
        full_plan="{}",
        deep_thinking_mode=True,
        search_before_planning=False
    )
    
    # 验证属性是否正确设置
    assert len(state["messages"]) == 1
    assert state["messages"][0].content == "测试消息"
    assert state["next"] == "planner"
    assert state["full_plan"] == "{}"
    assert state["deep_thinking_mode"] is True
    assert state["search_before_planning"] is False
