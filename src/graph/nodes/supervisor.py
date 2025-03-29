import logging
from typing import Literal
from langgraph.types import Command

from src.config import TEAM_MEMBERS
from src.graph.types import State

logger = logging.getLogger(__name__)

def supervisor_node(state: State) -> Command[Literal[*TEAM_MEMBERS, "__end__"]]:
    """主管节点，决定下一步应该执行哪个智能体。"""
    logger.info("主管正在评估下一步行动")
    
    # 获取消息历史，检查是否已经执行过研究员任务
    messages = state["messages"]
    has_researcher_message = any(
        hasattr(msg, 'name') and msg.name == "researcher"
        for msg in messages
    )
    
    # 防止无限循环: 如果已经有研究员消息，则转到 reporter 或结束
    if has_researcher_message:
        next_agent = "reporter"  # 或者直接 "__end__" 用于测试
        logger.info(f"已有研究员结果，进入报告阶段: {next_agent}")
    else:
        # 首次运行，分配给研究员
        next_agent = "researcher"  # 简单默认值，实际应由LLM决定
        logger.info(f"主管将任务分配给: {next_agent}")
    
    if next_agent == "FINISH":
        next_agent = "__end__"
        logger.info("工作流已完成")

    return Command(goto=next_agent, update={"next": next_agent})
