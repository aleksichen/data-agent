from agno.agent import Agent, RunResponse
from agno.models.deepseek import DeepSeek
from agno.tools.postgres import PostgresTools
import psycopg2

db_url = "postgresql://wedata:wedata@192.168.50.97:30036/wedata"

DB_HOST = "192.168.50.97"
DB_PORT = 30036
DB_NAME = "wedata"
DB_USER = "wedata"
DB_PASSWORD = "wedata"

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

# 手动设置schema为ai
# cursor = conn.cursor()
# cursor.execute("SET search_path TO ai")


data_catalog = Agent(
  name="数据视图查询",
  tools=[PostgresTools(
    connection=conn,
    table_schema="ai"
  )],
  model=DeepSeek(),
  markdown=True,
  debug_mode=True,
)

if __name__ == "__main__":
  data_catalog.print_response("看看我的数据库都有哪些表, 分别查看每个表都是什么结构 然后对agent_sessions表做个数据分析")
