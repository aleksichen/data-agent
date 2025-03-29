import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from langgraph.types import Command

from src.graph.types import State

logger = logging.getLogger(__name__)

def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """规划员节点，生成完整计划。"""
    logger.info("规划员正在生成完整计划")
    # 待实现: 调用LLM生成计划
    
    return Command(
        update={
            "messages": [HumanMessage(content="{}", name="planner")],
            "full_plan": "{}",
        },
        goto="supervisor",
    )
