from agno.storage.agent.postgres import PostgresAgentStorage
from agno.agent import Agent, AgentMemory
from agno.memory.db.postgres import PgMemoryDb
from agno.memory.summarizer import MemorySummarizer
from agno.memory.classifier import MemoryClassifier
from agno.memory.manager import MemoryManager

from rich.console import Console
from rich.panel import Panel
from rich.json import JSON
import json
from src.llm.qwq import deepseek

db_url = "postgresql+psycopg://wedata:wedata@192.168.50.97:30036/wedata"

agent_storage = PostgresAgentStorage(
  table_name="personalized_agent_sessions",
  db_url=db_url,
  auto_upgrade_schema=True
)

memory_classifier = MemoryClassifier(model=deepseek)

memory_summarizer = MemorySummarizer(model=deepseek)

manager = MemoryManager(model=deepseek)

agent = Agent(
  name="具有会话能力的能力",
  model=deepseek,
  markdown=True,
  add_history_to_messages=True,
  num_history_responses=3,
  storage=agent_storage,
  # memory=AgentMemory(
  #   db=PgMemoryDb(table_name="agent_memory", db_url=db_url),
  #   create_user_memories=True,
  #   update_user_memories_after_run=True,
  #   create_session_summary=True,
  #   update_session_summary_after_run=True,
  #   summarizer=memory_summarizer,
  #   classifier=memory_classifier,
  #   manager=manager
  # ),
  read_chat_history=True,
  debug_mode=True,
)

console = Console()

def print_chat_history(agent):
    # -*- Print history
    console.print(
        Panel(
            JSON(
                json.dumps(
                    [
                        m.model_dump(include={"role", "content"})
                        for m in agent.memory.messages
                    ]
                ),
                indent=4,
            ),
            title=f"Chat History for session_id: {agent.session_id}",
            expand=True,
        )
    )


if __name__ == "__main__":
  agent.print_response("你好吗", stream=True)
  agent.print_response("我喜欢吃冰淇淋, 你呢", stream=True)
  agent.print_response("我喜欢什么", stream=True)
  agent.run()
