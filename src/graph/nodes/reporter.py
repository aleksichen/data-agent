import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def reporter_node(state: State) -> Command[Literal["supervisor"]]:
    """报告员节点，编写最终报告。"""
    logger.info("报告员正在编写最终报告")
    # 待实现: 调用LLM生成报告
    
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="报告编写中...",
                    name="reporter",
                )
            ]
        },
        goto="supervisor",
    )
