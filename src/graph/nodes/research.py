import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def research_node(state: State) -> Command[Literal["supervisor"]]:
    """研究员节点，执行研究任务。"""
    logger.info("研究员开始执行任务")
    # 待实现: 调用研究智能体
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="研究任务正在实施",
                    name="researcher",
                )
            ]
        },
        goto="supervisor",
    )
