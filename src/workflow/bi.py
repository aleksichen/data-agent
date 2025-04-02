from typing import Dict, Iterator, List, Optional
import json
import time
import random
from datetime import datetime
from enum import Enum

from agno.utils.log import logger
from agno.run.response import RunResponse, RunEvent, RunResponseExtraData
from agno.models.message import Message, Citations, MessageReferences
from agno.reasoning.step import ReasoningStep
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow
from src.agents.finance import finance_agent
from src.agents.analysis_agent import data_analysis_agent

# from src.agents.python import python_agent


class BIWorkflow(Workflow):
    """
    提取数据
    分析数据
    计算数据
    可视化图表
    编写报告
    """

    def run(self, message: str) -> Iterator[RunResponse]:
        logger.info(f"开始执行")

        # 定义随机延迟的范围（秒）

        # yield from data_analysis_agent.run(message, stream=True)

        # delay = random.uniform(min_delay, max_delay)
        # time.sleep(delay)
        # chart_config = {
        #     "type": "line",
        #     "data": [],
        #     "dimensions": [{"field": "month", "name": "月份"}],
        #     "measures": [{"field": "sales", "name": "销售额"}],
        #     "series": {"field": "category", "name": "类别"},
        #     "config": {
        #         "title": "月度销售趋势",
        #         "height": 350,
        #         "colors": ["#4e79a7", "#f28e2c"]
        #     }
        # }
        # yield RunResponse(
        #     content=json.dumps(chart_config),
        #     content_type="chart",
        #     event=RunEvent.run_response.value,
        #     run_id=self.run_id,
        #     agent_id="data_viz_agent",
        #     session_id=self.session_id,
        #     workflow_id=self.workflow_id,
        # )

        # 第四步延迟
        min_delay = 0.0
        max_delay = 2.0
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
        chart_config2 = {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Sales Person", "Amount"],
            },
            "type": "bar",
            "dimensions": [{"field": "Sales Person", "name": "销售人员"}],
            "measures": [{"field": "Amount", "name": "销售额", "aggregation": "sum"}],
            "config": {
                "title": "销售人员业绩比较",
                "xAxis": {"title": "销售人员"},
                "yAxis": {"title": "总销售额"},
            },
        }
        yield RunResponse(
            content=json.dumps(chart_config2),
            content_type="chart",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_viz_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )


# if __name__ == "__main__":
# workflow = BIAnalyze(
#   session_id="BIAnalyze"
# )

# Run workflow with caching
# responses = workflow.run()
# pprint_run_response(responses, markdown=True)
# logger.info("Workflow completed successfully!")
