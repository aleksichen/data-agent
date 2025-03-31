from typing import Dict, Iterator, List, Optional
import json
import time
from datetime import datetime
from enum import Enum

from agno.utils.log import logger
from agno.run.response import RunResponse, RunEvent, RunResponseExtraData
from agno.models.message import Message, Citations, MessageReferences
from agno.reasoning.step import ReasoningStep
from agno.utils.pprint import pprint_run_response
from agno.workflow import Workflow

class BIWorkflow(Workflow):
    """
    提取数据
    分析数据
    计算数据
    可视化图表
    编写报告
    """
        
    def run(self, message: str) -> Iterator[RunResponse]:
        print(message)
        # 1. 工作流开始
        yield RunResponse(
            content="BI分析工作流启动",
            content_type="str",
            event=RunEvent.workflow_started.value,
            run_id=self.run_id,
            agent_id="asdasd",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 2. 数据提取阶段
        # 2.1 提取阶段开始
        yield RunResponse(
            content="开始数据提取",
            content_type="str",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_extraction_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 2.2 工具调用开始 - 模拟SQL查询工具
        yield RunResponse(
            content="正在连接数据库...",
            content_type="str",
            event=RunEvent.tool_call_started.value,
            run_id=self.run_id,
            agent_id="data_extraction_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            tools=[{
                "name": "SQLQueryTool",
                "description": "执行SQL查询",
                "parameters": {
                    "query": "SELECT date, sales, customers FROM sales_data WHERE date BETWEEN '2023-01-01' AND '2023-12-31'"
                }
            }]
        )
        
        # 2.3 工具调用完成
        yield RunResponse(
            content="查询完成，已获取数据",
            content_type="str",
            event=RunEvent.tool_call_completed.value,
            run_id=self.run_id,
            agent_id="data_extraction_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            formatted_tool_calls=["SQL查询执行成功: 返回365条销售记录"],
        )
        
        # 2.4 数据提取完成，展示表格
        markdown_table = """
## 数据提取结果示例

| 日期 | 销售额 | 客户数 |
|------|--------|--------|
| 2023-01-01 | 12,450 | 278 |
| 2023-01-02 | 10,890 | 245 |
| 2023-01-03 | 14,230 | 301 |
| ... | ... | ... |
| 2023-12-31 | 18,670 | 412 |

**总计:** 365行数据已提取
        """
        
        yield RunResponse(
            content=markdown_table,
            content_type="markdown",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_extraction_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 3. 数据分析阶段
        # 3.1 分析开始
        yield RunResponse(
            content="开始分析数据",
            content_type="str",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 3.2 启动思考过程
        yield RunResponse(
            content="启动分析思考过程",
            content_type="str",
            event=RunEvent.reasoning_started.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 3.3 思考步骤1
        reasoning_step1 = ReasoningStep(
            id="reasoning_step_1",
            content="首先，我需要分析年度销售趋势。月度销售额有明显的季节性波动，需要进一步分析。",
            type="thinking"
        )
        
        yield RunResponse(
            content="正在分析年度销售趋势...",
            content_type="str",
            event=RunEvent.reasoning_step.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            extra_data=RunResponseExtraData(
                reasoning_steps=[reasoning_step1]
            )
        )
        
        # 3.4 思考步骤2
        reasoning_step2 = ReasoningStep(
            id="reasoning_step_2",
            content="其次，我需要分析客户数量与销售额的相关性。通过计算皮尔逊相关系数，发现相关系数为0.86，表明强相关性。",
            type="thinking"
        )
        
        yield RunResponse(
            content="正在分析客户数量与销售额相关性...",
            content_type="str",
            event=RunEvent.reasoning_step.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            extra_data=RunResponseExtraData(
                reasoning_steps=[reasoning_step1, reasoning_step2]
            )
        )
        
        # 3.5 思考步骤3
        reasoning_step3 = ReasoningStep(
            id="reasoning_step_3",
            content="最后，计算关键业务指标：平均客单价、月环比增长率、季度同比增长率等。",
            type="thinking"
        )
        
        yield RunResponse(
            content="计算关键业务指标...",
            content_type="str",
            event=RunEvent.reasoning_step.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            extra_data=RunResponseExtraData(
                reasoning_steps=[reasoning_step1, reasoning_step2, reasoning_step3]
            )
        )
        
        # 3.6 思考完成
        yield RunResponse(
            content="分析思考完成",
            content_type="str",
            event=RunEvent.reasoning_completed.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            thinking="我已完成数据分析，发现以下关键点：\n1. 销售额在Q4季度达到全年最高\n2. 客户数量与销售额高度相关\n3. 客单价在节假日期间明显上升\n4. 周二至周四是销售旺日",
        )
        
        # 3.7 分析结果
        analysis_result = """
## 数据分析结果

### 关键发现
- **年销售额**: ¥5,840,300
- **同比增长**: 23.5%
- **平均客单价**: ¥45.60
- **客单价环比增长**: 5.2%
- **销售额与客户数相关系数**: 0.86 (强相关)

### 季节性模式
- Q4季度销售额占全年的32%，是最强劲的季度
- 周二至周四是每周销售高峰
- 节假日期间客单价上涨约15%
        """
        
        yield RunResponse(
            content=analysis_result,
            content_type="markdown",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_analysis_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 4. 数据可视化阶段
        # 4.1 可视化开始
        yield RunResponse(
            content="开始数据可视化",
            content_type="str",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_viz_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 4.2 准备图表数据 - 销售趋势图
        sales_chart_data = {
            "type": "line",
            "data": {
                "labels": ["1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"],
                "datasets": [
                    {
                        "label": "月度销售额 (万元)",
                        "data": [38.5, 35.2, 42.1, 45.6, 48.9, 51.2, 49.8, 52.3, 55.1, 58.7, 62.4, 68.9],
                        "borderColor": "rgba(75, 192, 192, 1)",
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "fill": True
                    }
                ]
            },
            "options": {
                "responsive": True,
                "title": {
                    "display": True,
                    "text": "2023年月度销售趋势"
                },
                "scales": {
                    "y": {
                        "beginAtZero": False
                    }
                }
            }
        }
        
        # 4.3 返回图表配置
        yield RunResponse(
            content=sales_chart_data,
            content_type="chart_config",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_viz_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 4.4 客户数与销售额散点图
        correlation_chart_data = {
            "type": "scatter",
            "data": {
                "datasets": [
                    {
                        "label": "客户数 vs 销售额",
                        "data": [
                            {"x": 278, "y": 124.5},
                            {"x": 245, "y": 108.9},
                            {"x": 301, "y": 142.3},
                            {"x": 320, "y": 150.6},
                            {"x": 310, "y": 147.2},
                            {"x": 350, "y": 164.5},
                            {"x": 330, "y": 156.8},
                            {"x": 360, "y": 170.2},
                            {"x": 380, "y": 178.5},
                            {"x": 390, "y": 183.6},
                            {"x": 405, "y": 192.4},
                            {"x": 412, "y": 186.7}
                        ],
                        "backgroundColor": "rgba(255, 99, 132, 0.5)"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "title": {
                    "display": True,
                    "text": "客户数量与销售额相关性 (r=0.86)"
                },
                "scales": {
                    "x": {
                        "title": {
                            "display": True,
                            "text": "客户数"
                        }
                    },
                    "y": {
                        "title": {
                            "display": True,
                            "text": "销售额 (千元)"
                        }
                    }
                }
            }
        }
        
        # 4.5 返回散点图配置
        yield RunResponse(
            content=correlation_chart_data,
            content_type="chart_config",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_viz_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 4.6 季度销售分布饼图
        pie_chart_data = {
            "type": "pie",
            "data": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [
                    {
                        "data": [21, 23, 24, 32],
                        "backgroundColor": [
                            "rgba(255, 99, 132, 0.6)",
                            "rgba(54, 162, 235, 0.6)",
                            "rgba(255, 206, 86, 0.6)",
                            "rgba(75, 192, 192, 0.6)"
                        ]
                    }
                ]
            },
            "options": {
                "responsive": True,
                "title": {
                    "display": True,
                    "text": "季度销售额分布 (%)"
                }
            }
        }
        
        # 4.7 返回饼图配置
        yield RunResponse(
            content=pie_chart_data,
            content_type="chart_config",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="data_viz_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 5. 报告生成阶段
        # 5.1 报告开始
        yield RunResponse(
            content="开始生成最终报告",
            content_type="str",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="report_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 5.2 生成报告
        report_content = """
# 2023年度销售业绩分析报告

## 摘要
本报告对2023年全年销售数据进行了分析，总结了关键业务指标、销售趋势以及影响因素，并提出了针对性建议。

## 1. 业务表现概述

### 1.1 核心指标
- **年销售总额**: ¥5,840,300
- **同比增长率**: 23.5%
- **客户总数**: 124,865
- **平均客单价**: ¥45.60

### 1.2 季度表现
2023年第四季度是全年业绩最强的季度，贡献了32%的销售额。这主要得益于节日促销活动和年终购物季的推动。

### 1.3 关键业绩驱动因素
- 客户数量与销售额高度相关(r=0.86)
- 新产品线贡献了约20%的销售增长
- 线上渠道销售占比提升至62%

## 2. 趋势分析

### 2.1 销售趋势
销售额呈现稳定增长趋势，第四季度增长尤为显著。夏季促销活动带来了7-8月的小幅增长高峰。

### 2.2 客户行为分析
- 周中(周二至周四)是销售高峰期
- 节假日期间客单价上升约15%
- 复购率同比提升8.3%

## 3. 建议与展望

### 3.1 策略建议
1. **加强季节性促销**: 针对Q1和Q3的相对低谷期设计更有吸引力的促销活动
2. **提升客单价**: 通过交叉销售和向上销售策略提高平均客单价
3. **客户留存**: 实施会员忠诚度计划，提高客户复购率

### 3.2 2024年展望
基于当前趋势和市场环境，预计2024年销售额有望实现18-20%的增长，重点关注以下方面：
- 新市场拓展
- 产品线扩充
- 客户体验优化

## 4. 结论
2023年销售业绩表现强劲，增长势头良好。通过针对性策略优化，2024年有望实现更好的业绩表现。

---

*报告生成日期: 2024年1月15日*
*数据来源: 公司销售管理系统*
        """
        
        # 5.3 返回最终报告
        yield RunResponse(
            content=report_content,
            content_type="markdown",
            event=RunEvent.run_response.value,
            run_id=self.run_id,
            agent_id="report_agent",
            session_id=self.session_id,
            workflow_id=self.workflow_id,
        )
        
        # 添加引用文献
        citations = Citations(
            items=[
                {
                    "text": "销售数据分析方法论",
                    "source": "内部销售分析手册 (2023版)"
                },
                {
                    "text": "行业基准数据",
                    "source": "市场研究报告 #B-2023-42"
                }
            ]
        )
        
        # 5.4 工作流完成
        yield RunResponse(
            content="BI分析工作流完成",
            content_type="str",
            event=RunEvent.workflow_completed.value,
            run_id=self.run_id,
            agent_id=self.agent_id,
            session_id=self.session_id,
            workflow_id=self.workflow_id,
            citations=citations
        )

# if __name__ == "__main__":
  # workflow = BIAnalyze(
  #   session_id="BIAnalyze"
  # )
  
  # Run workflow with caching
  # responses = workflow.run()
  # pprint_run_response(responses, markdown=True)
  # logger.info("Workflow completed successfully!")