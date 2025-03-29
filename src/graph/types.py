from typing import Literal
from typing_extensions import TypedDict
from langgraph.graph import MessagesState

from src.config import TEAM_MEMBERS

# 定义路由选项
OPTIONS = TEAM_MEMBERS + ["FINISH"]


class Router(TypedDict):
    """决定下一步路由到哪个智能体，如果不需要智能体，则路由到FINISH。"""

    next: Literal[*OPTIONS]


class State(MessagesState):
    """智能体系统的状态，继承MessagesState并添加next字段。"""

    # 常量
    TEAM_MEMBERS: list[str]

    # 运行时变量
    next: str
    full_plan: str
