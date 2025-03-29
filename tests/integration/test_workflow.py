import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

@pytest.mark.integration
@patch("src.graph.nodes.get_llm_by_type")
@patch("src.graph.nodes.research_agent")
@patch("src.graph.nodes.coder_agent")
@patch("src.graph.nodes.browser_agent")
@patch("src.graph.nodes.apply_prompt_template")
def test_coordinator_to_planner_flow(
    mock_apply_template, 
    mock_browser, 
    mock_coder, 
    mock_researcher, 
    mock_get_llm
):
    """测试从协调员到规划员的基本流程"""
    from src.graph.builder import build_graph
    
    # 设置模拟
    class MockLLM:
        def __init__(self, response_content):
            self.response_content = response_content
        
        def invoke(self, messages):
            class MockResponse:
                def __init__(self, content):
                    self.content = content
            return MockResponse(self.response_content)
            
        def stream(self, messages):
            return [type('obj', (object,), {'content': self.response_content})]
            
        def with_structured_output(self, schema, method=None):
            return self
    
    # 模拟协调员返回请求规划的响应
    mock_apply_template.return_value = [HumanMessage(content="请处理用户请求")]
    mock_get_llm.side_effect = [
        # 协调员的响应
        MockLLM("这需要深入分析。handoff_to_planner"),
        # 规划员的响应
        MockLLM('{"steps": [{"type": "research", "description": "市场研究"}]}'),
        # 主管的响应
        MockLLM(type('obj', (object,), {'next': 'FINISH'}))
    ]
    
    # 构建图
    graph = build_graph()
    
    # 执行流程
    result = graph.invoke({
        "messages": [HumanMessage(content="分析2023年销售数据")],
        "next": "",
        "full_plan": "",
        "deep_thinking_mode": True,
        "search_before_planning": False
    })
    
    # 验证流程
    assert "messages" in result
    assert "full_plan" in result
    
    # 应该至少调用了一次get_llm_by_type
    assert mock_get_llm.call_count >= 1


@pytest.mark.integration
def test_supervisor_routing():
    """测试主管正确路由到专业智能体"""
    from src.graph.types import State
    from src.graph.nodes import supervisor_node
    
    # 此测试需要高度模拟，以验证路由逻辑
    # 在实际实现中完成
    pass


@pytest.mark.integration
@patch("src.graph.builder.research_node")
@patch("src.graph.builder.code_node")
@patch("src.graph.builder.supervisor_node")
@patch("src.graph.builder.planner_node")
@patch("src.graph.builder.coordinator_node")
def test_end_to_end_workflow(
    mock_coordinator, 
    mock_planner, 
    mock_supervisor, 
    mock_code, 
    mock_research
):
    """测试端到端的完整工作流"""
    from src.graph.builder import build_graph
    from src.graph.types import State
    from langgraph.types import Command
    
    # 设置模拟序列：协调员->规划员->主管->研究员->主管->编码员->主管->结束
    mock_coordinator.side_effect = lambda state: Command(goto="planner")
    mock_planner.side_effect = lambda state: Command(
        goto="supervisor",
        update={"full_plan": '{"steps":[{"type":"research"},{"type":"code"}]}'}
    )
    
    # 主管首先路由到研究员，然后到编码员，最后结束
    supervisor_calls = 0
    def supervisor_sequence(state):
        nonlocal supervisor_calls
        supervisor_calls += 1
        if supervisor_calls == 1:
            return Command(goto="researcher")
        elif supervisor_calls == 2:
            return Command(goto="coder")
        else:
            return Command(goto="__end__")
    
    mock_supervisor.side_effect = supervisor_sequence
    
    # 专业智能体返回到主管
    mock_research.side_effect = lambda state: Command(
        goto="supervisor",
        update={"messages": [HumanMessage(content="研究结果", name="researcher")]}
    )
    mock_code.side_effect = lambda state: Command(
        goto="supervisor",
        update={"messages": [HumanMessage(content="代码结果", name="coder")]}
    )
    
    # 构建图
    graph = build_graph()
    
    # 执行完整流程
    result = graph.invoke({
        "messages": [HumanMessage(content="分析数据")],
        "next": "",
        "full_plan": "",
        "deep_thinking_mode": False,
        "search_before_planning": False
    })
    
    # 验证完整流程执行
    assert supervisor_calls == 3
    assert mock_coordinator.call_count == 1
    assert mock_planner.call_count == 1
    assert mock_research.call_count == 1
    assert mock_code.call_count == 1
