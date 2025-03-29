import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from langgraph.prebuilt.chat_agent_executor import AgentState

# Initialize Jinja2 environment
env = Environment(
    loader=FileSystemLoader(os.path.dirname(__file__)),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def get_prompt_template(prompt_name: str) -> str:
    """
    Load and return a prompt template using Jinja2.

    Args:
        prompt_name: Name of the prompt template file (without .md extension)

    Returns:
        The template string with proper variable substitution syntax
    """
    try:
        template = env.get_template(f"{prompt_name}.md")
        return template.render()
    except Exception as e:
        raise ValueError(f"Error loading template {prompt_name}: {e}")


def apply_prompt_template(prompt_name: str, state: AgentState) -> list:
    """
    Apply template variables to a prompt template and return formatted messages.

    Args:
        prompt_name: Name of the prompt template to use
        state: Current agent state containing variables to substitute

    Returns:
        List of messages with the system prompt as the first message
    """
    state_vars = {
        "CURRENT_TIME": datetime.now().strftime("%a %b %d %Y %H:%M:%S %z"),
        **state,
    }

    try:
        template = env.get_template(f"{prompt_name}.md")
        system_prompt = template.render(**state_vars)
        print('system_prompt', system_prompt)
        return [{"role": "system", "content": system_prompt}] + state["messages"]
    except Exception as e:
        raise ValueError(f"Error applying template {prompt_name}: {e}")

if __name__ == "__main__":
    # 示例：组装一个planner的示例状态并输出完整的提示
    from src.config import TEAM_MEMBERS
    
    # 创建一个模拟state对象
    state = {
        "messages": [
            {"role": "user", "content": "我想开发一个React Todo List应用，可以帮我做个任务规划吗？"}
        ],
        "TEAM_MEMBERS": TEAM_MEMBERS
    }
    
    # 获取planner的完整提示
    try:
        # 方法1：使用apply_prompt_template获取格式化的提示列表
        messages = apply_prompt_template('planner', state)
        # print("\n=== 方法1: apply_prompt_template 输出 ===")
        # print(messages)

    except Exception as e:
        print(f"错误: {e}")
