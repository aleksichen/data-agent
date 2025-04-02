from typing import List, Dict, Any, Optional
from agno.tools import Toolkit
from src.mock.user_chart import user_charts


class ChartTools(Toolkit):
    """
    图表分析工具，用于查询现有图表和创建新图表。
    """

    def __init__(self):
        super().__init__(name="图表分析工具")
        # 支持的图表类型
        self.supported_chart_types = [
            "line",
            "bar",
            "pie",
            "scatter",
            "area",
            "heatmap",
            "radar",
            "column",
            "dual",
            "custom",
        ]

    def list_user_charts(self) -> List[Dict[str, Any]]:
        """
        查询用户已经有的图表实例

        Returns:
            List[Dict[str, Any]]: 用户现有的图表配置列表
        """
        # 这里直接返回user_charts全局变量的内容
        return user_charts

    def create_chart(
        self,
        case: str,
        table_name: str,
        chart_type: str,
        dimension_fields: List[Dict[str, str]],
        measure_fields: List[Dict[str, str]],
        title: str,
        axis_config: Optional[Dict[str, Any]] = None,
        extra_config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        创建新的图表配置

        Args:
            case: 图表用例描述
            table_name: 数据表名称，格式为"database.table"
            chart_type: 图表类型，支持line/bar/pie/scatter/area/heatmap/radar/column/dual/custom
            dimension_fields: 维度字段列表，格式为[{"field": "Product", "name": "产品"}]
            measure_fields: 度量字段列表，格式为[{"field": "Amount", "name": "销售额", "aggregation": "sum"}]
            title: 图表标题
            axis_config: 坐标轴配置（可选）
            extra_config: 额外配置（可选）

        Returns:
            Dict[str, Any]: 创建的图表配置
        """
        # 验证图表类型
        if chart_type not in self.supported_chart_types:
            raise ValueError(
                f"不支持的图表类型: {chart_type}，支持的类型有: {', '.join(self.supported_chart_types)}"
            )

        # 构建所有字段列表
        all_fields = [d["field"] for d in dimension_fields] + [
            m["field"] for m in measure_fields
        ]

        # 构建基础配置
        config = {"title": title}

        # 添加坐标轴配置（如果提供）
        if axis_config:
            if "xAxis" in axis_config:
                config["xAxis"] = axis_config["xAxis"]
            if "yAxis" in axis_config:
                config["yAxis"] = axis_config["yAxis"]

        # 添加额外配置（如果提供）
        if extra_config:
            for key, value in extra_config.items():
                if key not in config:  # 避免覆盖已有配置
                    config[key] = value

        # 构建完整的图表配置
        chart_config = {
            "dataSource": {"table": table_name, "fields": all_fields},
            "type": chart_type,
            "dimensions": dimension_fields,
            "measures": measure_fields,
            "config": config,
        }

        # 构建最终的图表案例
        chart_case = {"case": case, "chart_config": chart_config}

        # 将新创建的图表添加到用户图表列表中
        user_charts.append(chart_case)

        return chart_case
