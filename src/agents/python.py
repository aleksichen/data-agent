from agno.agent import Agent
from agno.tools.python import PythonTools
from agno.models.deepseek import DeepSeek

agent = Agent(
    model=DeepSeek(),
    tools=[PythonTools()],
    show_tool_calls=True,
    markdown=True,
)
agent.print_response("帮我用python生成一些atharvasoundankar/chocolate-sales的销售数据, 200行,左右 返回dataframe结构数据")