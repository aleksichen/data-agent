import logging
from typing import Literal
from datetime import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.types import Command

from src.graph.types import State
from src.config.agents import AGENT_LLM_MAP
from src.llm.llm import get_llm_by_type
from src.prompts.template import get_prompt_template

logger = logging.getLogger(__name__)

def coordinator_node(state: State) -> Command[Literal["planner", "__end__"]]:
    """
    协调员节点，处理用户请求。
    职责:
    - 处理简单任务(如问候、闲聊)
    - 将复杂任务转交给规划员
    
    Returns:
        Command: 下一步操作指令，可以是处理简单任务后结束，或转交给规划员
    """
    logger.info("协调员正在分析用户请求")
    
    # 获取最新用户消息
    messages = state["messages"]
    user_message = None
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            user_message = message.content
            break
    
    if not user_message:
        logger.warning("未找到用户消息")
        return Command(goto="__end__")
    
    # 加载协调员提示模板
    prompt_template = get_prompt_template("coordinator")
    
    # 准备LLM调用参数
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_prompt = prompt_template.replace("{ { CURRENT_TIME } }", current_time)
    
    # 获取协调员LLM
    llm = get_llm_by_type(AGENT_LLM_MAP["coordinator"])
    
    # 构建消息
    prompt_message = [
        SystemMessage(content=formatted_prompt),
        HumanMessage(content=user_message)
    ]
    
    # 调用LLM
    response = llm.invoke(prompt_message)
    response_content = response.content
    
    logger.info(f"协调员响应: {response_content}")
    
    # 判断是简单任务还是复杂任务
    if "handoff_to_planner()" in response_content:
        # 复杂任务，转交给规划员
        logger.info("复杂任务，转交给规划员")
        return Command(
            update={
                "messages": messages + [AIMessage(content="我会为您处理这个问题。", name="coordinator")]
            },
            goto="planner"
        )
    else:
        # 简单任务，直接回复用户
        logger.info("简单任务，直接回复")
        return Command(
            update={
                "messages": messages + [AIMessage(content=response_content, name="coordinator")]
            },
            goto="__end__"  # 流程结束
        )
