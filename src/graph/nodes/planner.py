import logging
import json
from typing import Literal
from datetime import datetime
import json_repair
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command

from src.graph.types import State
from src.config.agents import AGENT_LLM_MAP
from src.llm.llm import get_llm_by_type
from src.prompts.template import apply_prompt_template, get_prompt_template

logger = logging.getLogger(__name__)

def planner_node(state: State) -> Command[Literal["supervisor", "__end__"]]:
    """规划员节点，生成完整计划。"""
    logger.info("规划员正在生成完整计划")
    
    """构建完整prompt"""
    prompt = apply_prompt_template("planner", state)

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_prompt = prompt.replace("{ { CURRENT_TIME } }", current_time)
    
    """默认使用基础模型"""
    llm = get_llm_by_type("basic")
    
    """开启流式输出"""
    stream = llm.stream(formatted_prompt)

    full_response = ""
    for chunk in stream:
        full_response += chunk.content
        
    logger.debug(f"Planner response: {full_response}")
    
    if full_response.startswith("```json"):
        full_response = full_response.removeprefix("```json")

    if full_response.endswith("```"):
        full_response = full_response.removesuffix("```")
    
    goto = "supervisor"
    """尝试修复JSON"""
    try:
        repaired_response = json_repair.loads(full_response)
        full_response = json.dumps(repaired_response)
    except json.JSONDecodeError:
        logger.warning("Planner response is not a valid JSON")
        goto = "__end__"
    
    return Command(
        update={
            "messages": [HumanMessage(content=full_response, name="planner")],
            "full_plan": full_response,
        },
        goto=goto,
    )
