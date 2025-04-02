from agno.agent import Agent
from agno.tools.python import PythonTools
from agno.models.deepseek import DeepSeek
from agno.tools.thinking import ThinkingTools
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.agent import Agent, AgentMemory
from agno.memory.db.postgres import PgMemoryDb
from agno.memory.summarizer import MemorySummarizer
from agno.memory.classifier import MemoryClassifier
from agno.memory.manager import MemoryManager

from src.tools.doris import DorisTools

db_url = "postgresql+psycopg://wedata:wedata@192.168.50.97:30036/wedata"

storage = PostgresAgentStorage(
    table_name="agent_sessions", db_url=db_url, auto_upgrade_schema=True
)

agent_storage = PostgresAgentStorage(
    table_name="personalized_agent_sessions", db_url=db_url, auto_upgrade_schema=True
)

doris_tools = DorisTools(
    host="192.168.50.97",
    port=30930,
    user="root",
    password="",
    database="wedata",
    read_only=False,  # 设置为 True 禁用数据修改功能
)

deepseek = DeepSeek()

memory_classifier = MemoryClassifier(model=deepseek)

memory_summarizer = MemorySummarizer(model=deepseek)

manager = MemoryManager(model=deepseek)

python_agent = Agent(
    name="python执行能力",
    model=deepseek,
    tools=[ThinkingTools(think=True), PythonTools(), doris_tools],
    memory=AgentMemory(
        db=PgMemoryDb(table_name="agent_memory", db_url=db_url),
        create_user_memories=True,
        update_user_memories_after_run=True,
        create_session_summary=True,
        update_session_summary_after_run=True,
        summarizer=memory_summarizer,
        classifier=memory_classifier,
        manager=manager,
    ),
    storage=agent_storage,
    show_tool_calls=True,
    markdown=True,
    debug_mode=True,
)

# python_agent.print_response(
#     """
#   我下载了chocolate-sales的销售数据到本地, 路径如下
#  1. /Users/aleksichen/.cache/kagglehub/datasets/atharvasoundankar/chocolate-sales/versions/4/Chocolate Sales.csv
#  2. 读取数据将数据转成dataframe保存到doris中 注意
#   """,
#     stream=True,
# )
