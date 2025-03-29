import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

from src.graph.types import State, Router
from src.config import TEAM_MEMBERS
import logging
logger = logging.getLogger(__name__)

@pytest.mark.parametrize("node_name", [
    "coordinator_node",
    "planner_node", 
    "supervisor_node",
    "research_node",
    "code_node",
    "browser_node",
    "reporter_node"
])
def test_node_imports(node_name):
    """测试所有节点函数是否正确定义和可导入"""
    try:
        # 动态导入节点函数
        from importlib import import_module
        node_module = import_module("src.graph.nodes")
        node_func = getattr(node_module, node_name)
        logger
        
        assert callable(node_func), f"{node_name} 不是可调用函数"
    except ImportError as e:
        pytest.fail(f"导入 {node_name} 失败: {e}")
    except AttributeError:
        pytest.fail(f"{node_name} 未在 src.graph.nodes 中定义")


@patch("src.llm.llm.get_llm_by_type")
def test_supervisor_node(mock_get_llm, mock_llm):
    """测试主管节点的决策功能"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始测试主管节点")
    from src.graph.nodes import supervisor_node
    
    # 设置模拟LLM返回
    logger.debug("设置模拟LLM返回值")
    mock_get_llm.return_value = mock_llm({
        "研究": {"next": "researcher"},
        "代码": {"next": "coder"},
        "浏览": {"next": "browser"},
        "完成": {"next": "FINISH"}
    })
    
    # 测试主管分配到研究员
    logger.info("测试场景1: 分配到研究员")
    state = State(
        messages=[
            HumanMessage(content="需要进行市场研究", name="user"),
            HumanMessage(content="执行市场研究任务", name="planner")
        ],
        next=""
    )
    logger.debug(f"输入状态: {state}")
    result = supervisor_node(state)
    logger.info(f"返回结果: goto={result.goto}")
    assert result.goto == "researcher"
    
    # 测试主管分配到编码员
    logger.info("测试场景2: 分配到编码员")
    state = State(
        messages=[
            HumanMessage(content="需要分析数据", name="user"),
            HumanMessage(content="编写代码分析数据", name="planner")
        ],
        next=""
    )
    logger.debug(f"输入状态: {state}")
    result = supervisor_node(state)
    logger.info(f"返回结果: goto={result.goto}")
    # assert result.goto == "coder"
    
    # # 测试任务完成
    # logger.info("测试场景3: 任务完成")
    # state = State(
    #     messages=[
    #         HumanMessage(content="总结所有发现", name="user"),
    #         HumanMessage(content="任务完成", name="reporter")
    #     ],
    #     next=""
    # )
    # logger.debug(f"输入状态: {state}")
    # result = supervisor_node(state)
    # logger.info(f"返回结果: goto={result.goto}")
    # assert result.goto == "__end__"


@patch("src.graph.nodes.research_agent")
def test_research_node(mock_agent):
    """测试研究员节点功能"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("开始测试研究员节点")
    from src.graph.nodes import research_node
    
    # 模拟研究员返回
    logger.debug("设置模拟研究员返回值")
    mock_agent.invoke.return_value = {
        "messages": [HumanMessage(content="研究结果：XYZ公司市场份额为25%", name="researcher")]
    }
    logger.debug(f"模拟返回值: {mock_agent.invoke.return_value}")
    
    # 测试研究节点
    state = State(
        messages=[HumanMessage(content="研究XYZ公司的市场份额")],
        next=""
    )
    logger.debug(f"输入状态: {state}")
    
    # 执行节点函数
    logger.info("执行研究节点函数")
    result = research_node(state)
    logger.debug(f"研究节点函数返回结果: {result}")
    
    # 验证结果
    logger.info("验证结果")
    assert result.goto == "supervisor", f"预期转到supervisor，实际转到{result.goto}"
    assert len(result.update.get("messages", [])) == 1
    assert result.update["messages"][0].name == "researcher"


@patch("src.graph.nodes.coder_agent")
def test_code_node(mock_agent):
    """测试编码员节点功能"""
    from src.graph.nodes import code_node
    
    # 模拟编码员返回
    mock_agent.invoke.return_value = {
        "messages": [HumanMessage(content="代码执行结果：数据分析完成，平均值为42", name="coder")]
    }
    
    # 测试编码节点
    state = State(
        messages=[HumanMessage(content="分析这些数据并计算平均值")],
        next=""
    )
    result = code_node(state)
    
    # 验证结果
    assert result.goto == "supervisor"
    assert len(result.update.get("messages", [])) == 1
    assert result.update["messages"][0].name == "coder"


@patch("src.llm.llm.get_llm_by_type")
@patch("src.graph.nodes.apply_prompt_template")
def test_planner_node(mock_apply_template, mock_get_llm, mock_llm):
    """测试规划员节点功能"""
    from src.graph.nodes import planner_node
    
    # 设置模拟
    mock_apply_template.return_value = [HumanMessage(content="请规划如何分析销售数据")]
    mock_get_llm.return_value = mock_llm({
        "default": '{"steps": [{"type": "research", "description": "查找市场数据"}, {"type": "code", "description": "分析销售趋势"}]}'
    })
    
    # 测试规划节点
    state = State(
        messages=[HumanMessage(content="分析2023年销售数据")],
        next="",
        deep_thinking_mode=True
    )
    result = planner_node(state)
    
    # 验证结果
    assert result.goto == "supervisor"
    assert "full_plan" in result.update
    assert "messages" in result.update


@patch("src.llm.llm.get_llm_by_type")
@patch("src.graph.nodes.apply_prompt_template")
def test_coordinator_node(mock_apply_template, mock_get_llm, mock_llm):
    """测试协调员节点功能"""
    from src.graph.nodes import coordinator_node
    
    # 设置模拟
    mock_apply_template.return_value = [HumanMessage(content="请处理用户请求")]
    
    class MockResponse:
        def __init__(self, content):
            self.content = content
    
    # 测试需要规划的情况
    mock_get_llm.return_value = mock_llm({
        "default": MockResponse("这个任务需要深入分析。handoff_to_planner")
    })
    
    state = State(
        messages=[HumanMessage(content="帮我分析这些复杂数据")],
        next=""
    )
    result = coordinator_node(state)
    
    # 验证结果：应该转到规划员
    assert result.goto == "planner"
    
    # 测试简单响应的情况
    mock_get_llm.return_value = mock_llm({
        "default": MockResponse("这是一个简单的回答，不需要深入分析。")
    })
    
    state = State(
        messages=[HumanMessage(content="今天天气如何？")],
        next=""
    )
    result = coordinator_node(state)
    
    # 验证结果：应该结束
    assert result.goto == "__end__"
