from textwrap import dedent

from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.thinking import ThinkingTools

"""验证推理模型和思考工具"""

reasoning_agent = Agent(
    model=DeepSeek(),
    tools=[
        ThinkingTools(think=True),
    ],
    # reasoning=True,
    markdown=True,
    # debug_mode=True,
    show_tool_calls=True,
    instructions=dedent("""\
    ## Using the think tool
    Before taking any action or responding to the user after receiving tool results, use the think tool as a scratchpad to:
    - List the specific rules that apply to the current request
    - Check if all required information is collected
    - Verify that the planned action complies with all policies
    - Iterate over tool results for correctness

    ## Rules
    - Its expected that you will use the think tool generously to jot down thoughts and ideas.
    - Use tables where possible\
    - reasoning in chinese, and response with chinese
    """),
)

if __name__ == "__main__":
  reasoning_agent.print_response(
    "一道酸菜鱼应该怎么做",
    stream=True,
    show_full_reasoning=True,
)

