import logging
from typing import Literal
from langgraph.types import Command

from src.config import TEAM_MEMBERS
from src.graph.types import State

logger = logging.getLogger(__name__)

def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """主管节点，决定下一步应该执行哪个智能体。"""
    logger.info("主管正在评估下一步行动")
    # 待实现: 调用LLM决定下一步
    next_agent = "researcher"  # 简单默认值，实际应由LLM决定
    
    if next_agent == "FINISH":
        next_agent = "__end__"
        logger.info("工作流已完成")
    else:
        logger.info(f"主管将任务分配给: {next_agent}")

    return Command(goto=next_agent, update={"next": next_agent})
