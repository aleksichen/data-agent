import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def reporter_node(state: State) -> Command[Literal["__end__"]]:
    """报告员节点，编写最终报告。"""
    logger.info("报告员正在编写最终报告")
    # 待实现: 调用LLM生成报告
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="这是为您制作的React Todo List应用的开发任务规划报告！在实际实现中，这里会生成一个完整的任务规划。",
                    name="reporter",
                )
            ]
        },
        goto="__end__",
    )
