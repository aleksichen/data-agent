import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def code_node(state: State) -> Command[Literal["supervisor"]]:
    """编码员节点，执行Python代码。"""
    logger.info("编码员开始执行任务")
    # 待实现: 调用编码智能体
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="代码任务正在实施",
                    name="coder",
                )
            ]
        },
        goto="supervisor",
    )
