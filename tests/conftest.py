import pytest
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

# 定义全局测试夹具
@pytest.fixture
def mock_llm():
    """模拟LLM响应的夹具"""
    class MockLLM:
        def __init__(self, responses=None):
            self.responses = responses or {"default": "这是一个模拟的LLM响应"}
            self.invocations = []
        
        def invoke(self, messages):
            self.invocations.append(messages)
            key = "default"
            if isinstance(messages, list) and messages and hasattr(messages[-1], "content"):
                # 尝试基于最后一条消息内容选择响应
                content = messages[-1].content
                for k in self.responses:
                    if k in content:
                        key = k
                        break
            
            from langchain_core.messages import AIMessage
            return AIMessage(content=self.responses.get(key, self.responses["default"]))
            
        def with_structured_output(self, schema, method=None):
            return self
    
    return MockLLM

@pytest.fixture
def sample_state():
    """提供用于测试的示例状态"""
    from langchain_core.messages import HumanMessage
    from src.graph.types import State
    
    return State(
        messages=[HumanMessage(content="分析这些数据")],
        next="",
        full_plan="",
        deep_thinking_mode=False,
        search_before_planning=False
    )
