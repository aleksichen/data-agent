import asyncio
from agno.agent import Agent, RunResponse
from agno.models.deepseek import DeepSeek
from agno.tools.calculator import CalculatorTools

"""
一个图表分析的agent, 接受给定的数据, 和预期图表, 由agent返回图表可视化图表

返回的结构一定要遵循以下JSON格式:
{
  "type": "bar",
  "dataSource": {
    "table": "sale_data_id",
    "field": ["month", "profit", "category"],
  },
  "dimensions": [{ "field": "month", name: "月份" }],
  "measures": [{ "field": "profit", name: "利润" }],
  "series": { "field": "category", name: "类别" },
  "config": {
    "title": "月度利润对比",
  },
}
"""
data_visual = Agent(
  name="图表渲染",
  model=DeepSeek(),
  tools=[],
  instructions=[
    # 这里是agent system prompt指令的编写区域
  ],
  markdown=True,
  show_tool_calls=True,
  stream=True
)

if __name__ == "__main__":
  asyncio.run(data_visual.aprint_response("", stream=True))
