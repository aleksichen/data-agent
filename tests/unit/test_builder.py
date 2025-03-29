import pytest
from unittest.mock import ANY, patch, MagicMock

import logging
logger = logging.getLogger(__name__)

def test_build_graph_structure():
    """测试图构建的结构是否正确"""
    from src.graph.builder import build_graph
    
    # 构建图
    graph = build_graph()
    
    # 验证图是否已编译
    assert hasattr(graph, "invoke"), "图应该是已编译的状态图"
    logger.info(graph)


@patch("src.graph.builder.StateGraph")
def test_graph_nodes_and_edges(mock_state_graph):
    """测试图中是否包含所有必要的节点和边"""
    from src.graph.builder import build_graph
    from src.config import TEAM_MEMBERS
    
    # 设置模拟
    mock_builder = MagicMock()
    mock_state_graph.return_value = mock_builder
    mock_builder.compile.return_value = "compiled_graph"
    
    # 构建图
    result = build_graph()
    
    # 验证结果
    assert result == "compiled_graph"
    
    # 验证添加了起始边
    mock_builder.add_edge.assert_any_call("__start__", "coordinator")
    
    # # 验证添加了所有节点
    node_names = [
        "coordinator",
        "planner",
        "supervisor",
        "researcher",
        "coder", 
        "browser",
        "reporter"
    ]
    
    for node in node_names:
        mock_builder.add_node.assert_any_call(node, ANY)