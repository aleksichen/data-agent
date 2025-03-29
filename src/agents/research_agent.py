from langchain_core.messages import AIMessage

def invoke(state):
    """
    研究员智能体实现。
    
    Args:
        state: 当前状态
    
    Returns:
        包含响应消息的字典
    """
    # 实际实现中，这里会调用LLM并执行研究任务
    # 当前只是返回一个简单的响应
    return {
        "messages": [
            AIMessage(content="这是研究员的初步发现", name="researcher")
        ]
    }
