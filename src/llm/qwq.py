from os import getenv
from typing import Optional
from agno.agent import Agent, RunResponse
from agno.models.openai.like import OpenAILike
from dataclasses import dataclass

@dataclass
class QwQDS(OpenAILike):
    id: str = "deepseek-v3"
    api_key="sk-85d6e812912b4b2abc6db5fd4ea20b88",
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Their support for structured outputs is currently broken
    supports_native_structured_outputs: bool = False

@dataclass
class QwQDSR1(OpenAILike):
    id: str = "deepseek-r1"
    api_key="sk-85d6e812912b4b2abc6db5fd4ea20b88",
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # Their support for structured outputs is currently broken
    supports_native_structured_outputs: bool = False


agent = Agent(
    model=QwQDS(),
    debug_mode=True,
    markdown=True,
    reasoning=False
)

if __name__ == "__main__":
  agent.print_response("分享一个两句话的恐怖故事", stream=True)
