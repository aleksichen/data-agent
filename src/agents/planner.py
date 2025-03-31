import asyncio
from agno.agent import Agent
from agno.models.deepseek import DeepSeek

planner = Agent(
    name="任务规划Agent",
    model=DeepSeek(),
    reasoning_model=DeepSeek(
        id="deepseek-reasoner", temperature=0, max_tokens=128, top_p=0.95
    ),
    markdown=True,
    show_tool_calls=True,
    stream_intermediate_steps=True
)
if __name__ == "__main__":
  asyncio.run(planner.aprint_response("9.11 and 9.9 -- which is bigger?", stream=True))
