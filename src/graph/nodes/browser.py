import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def browser_node(state: State) -> Command[Literal["supervisor"]]:
    """浏览器节点，执行网页浏览任务。"""
    logger.info("浏览器开始执行任务")
    # 待实现: 调用浏览器智能体
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="浏览任务正在实施",
                    name="browser",
                )
            ]
        },
        goto="supervisor",
    )
