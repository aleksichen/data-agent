import logging
import json
from typing import Literal
from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.types import Command

from src.graph.types import State
from src.config.agents import AGENT_LLM_MAP
from src.llm.llm import get_llm_by_type
from src.prompts.template import get_prompt_template

logger = logging.getLogger(__name__)

def reporter_node(state: State) -> Command[Literal["__end__"]]:
    """报告员节点，编写最终报告。"""
    logger.info("报告员正在编写最终报告")
    print("DEBUG: 报告员节点开始执行")
    
    # 获取所有消息和计划
    messages = state["messages"]
    full_plan = state.get("full_plan", "{}")
    
    # 尝试解析计划JSON
    try:
        plan_data = json.loads(full_plan)
        print(f"DEBUG: 报告员收到的计划数据: {plan_data}")
    except json.JSONDecodeError:
        plan_data = {}
        print("DEBUG: 计划数据不是有效的JSON")
    
    # 获取用户原始查询
    user_query = ""
    for message in messages:
        if isinstance(message, HumanMessage):
            user_query = message.content
            break
    
    # 如果没有计划数据，生成一个简单的报告
    if not plan_data or not isinstance(plan_data, dict) or not plan_data.get('steps'):
        report_content = f"""\
# 分析报告

## 任务摘要
您要求的是: "{user_query}"

很抱歉，我们无法生成详细的任务计划。请再次尝试，或提供更多详细信息。
"""
    else:
        # 使用LLM生成更好的报告
        try:
            # 加载报告员提示模板
            prompt_template = get_prompt_template("reporter")
            
            # 准备LLM调用参数
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_prompt = prompt_template.replace("{ { CURRENT_TIME } }", current_time)
            
            # 获取报告员LLM
            llm = get_llm_by_type(AGENT_LLM_MAP.get("reporter", "basic"))
            
            # 构建提示
            plan_str = json.dumps(plan_data, ensure_ascii=False, indent=2)
            prompt_content = f"""\
用户查询: {user_query}

计划数据: {plan_str}

请根据以上信息生成一个完整的报告。报告应该有强调标题、清晰的结构和分析总结。确保使用相同的语言回应（如果用户使用中文，请使用中文响复）。"""
            
            # 构建消息
            prompt_message = [
                SystemMessage(content=formatted_prompt),
                HumanMessage(content=prompt_content)
            ]
            
            print(f"DEBUG: 报告员调用LLM前的消息内容")
            
            # 调用LLM
            response = llm.invoke(prompt_message)
            report_content = response.content
            print(f"DEBUG: 报告员生成的报告: {report_content[:200]}...")
            
        except Exception as e:
            logger.error(f"LLM调用错误: {e}")
            # 使用备用报告
            plan_title = plan_data.get('title', '解决方案')
            steps = plan_data.get('steps', [])
            
            report_content = f"""\
# {plan_title} 实施报告

## 概述
早上好，我已分析了您的请求: "{user_query}"

## 实施步骤
"""
            
            for i, step in enumerate(steps):
                report_content += f"### 步骤 {i+1}: {step.get('title')}\n"
                report_content += f"**负责者**: {step.get('agent_name')}\n\n"
                report_content += f"{step.get('description')}\n\n"
    
    return Command(
        update={
            "messages": messages + [
                AIMessage(
                    content=report_content,
                    name="reporter",
                )
            ]
        },
        goto="__end__",
    )
