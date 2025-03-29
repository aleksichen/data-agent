import pytest
from unittest.mock import MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from src.graph.nodes.coordinator import coordinator_node
from src.graph.types import State
from src.llm.llm import get_llm_by_type


class TestCoordinatorNode:
    """协调员节点测试类"""

    def test_simple_task_greeting(self, monkeypatch):
        """测试处理简单问候任务"""
        # 模拟LLM响应
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="你好！我是DataAgent，有什么可以帮助你的吗？")
        
        # 模拟get_llm_by_type返回我们的mock
        monkeypatch.setattr("src.graph.nodes.coordinator.get_llm_by_type", lambda _: mock_llm)
        
        # 准备状态
        state = State(
            messages=[HumanMessage(content="你好")],
            next="",
            full_plan="",
            deep_thinking_mode=False,
            search_before_planning=False,
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # 调用协调员节点
        result = coordinator_node(state)
        
        # 验证结果
        assert result.goto == "__end__"  # 应该结束
        assert len(result.update["messages"]) == 2  # 原始消息 + 回复
        assert "你好" in result.update["messages"][0].content
        assert "DataAgent" in result.update["messages"][1].content
        
        # 验证LLM调用
        assert mock_llm.invoke.called

    def test_complex_task_handoff(self, monkeypatch):
        """测试将复杂任务转交给规划员"""
        # 模拟LLM响应
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = AIMessage(content="handoff_to_planner()")
        
        # 模拟get_llm_by_type返回我们的mock
        monkeypatch.setattr("src.graph.nodes.coordinator.get_llm_by_type", lambda _: mock_llm)
        
        # 准备状态
        state = State(
            messages=[HumanMessage(content="帮我分析这个CSV文件中的销售趋势并创建一个可视化")],
            next="",
            full_plan="",
            deep_thinking_mode=False,
            search_before_planning=False,
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # 调用协调员节点
        result = coordinator_node(state)
        
        # 验证结果
        assert result.goto == "planner"  # 应该转到规划员
        assert len(result.update["messages"]) == 2  # 原始消息 + 回复
        assert "我会为您处理这个问题" in result.update["messages"][1].content
        
        # 验证LLM调用
        assert mock_llm.invoke.called

    def test_no_user_message(self):
        """测试没有用户消息的情况"""
        # 准备状态 (空消息)
        state = State(
            messages=[],
            next="",
            full_plan="",
            deep_thinking_mode=False,
            search_before_planning=False,
            TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
        )
        
        # 调用协调员节点
        result = coordinator_node(state)
        
        # 验证结果 - 应该结束
        assert result.goto == "__end__"
