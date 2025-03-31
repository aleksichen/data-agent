import asyncio
from agno.agent import Agent
from agno.models.deepseek import DeepSeek
from agno.tools.financial_datasets import FinancialDatasetsTools

from src.tools.stock_tools import StockTools
# https://www.financialdatasets.ai/
# fb571114-4396-42a5-ba11-c098d061f106

finance_agent = Agent(
  name="金融数据查询",
  model=DeepSeek(),
  tools=[StockTools()],
  instructions=[
    "When given a financial query:",
        "1. Use appropriate Financial Datasets methods based on the query type",
        "2. Format financial data clearly and highlight key metrics",
        "3. For financial statements, compare important metrics with previous periods when relevant",
        "4. Calculate growth rates and trends when appropriate",
        "5. Handle errors gracefully and provide meaningful feedback",
  ],
  markdown=True,
  show_tool_calls=True,
)

if __name__ == "__main__":
  asyncio.run(finance_agent.aprint_response("东方财富近一年股价走势怎么样", stream=True))
