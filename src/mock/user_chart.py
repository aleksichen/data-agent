user_charts = [
    {
        "case": "不同产品的销售比较",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Product", "Amount", "Boxes Shipped"],
            },
            "type": "bar",
            "dimensions": [{"field": "Product", "name": "产品"}],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
                {"field": "Boxes Shipped", "name": "发货箱数", "aggregation": "sum"},
            ],
            "config": {
                "title": "产品销售情况",
                "xAxis": {"title": "产品"},
                "yAxis": {"title": "数量"},
            },
        },
    },
    {
        "case": "销售团队绩效分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Sales Person", "Amount"],
            },
            "type": "bar",
            "dimensions": [{"field": "Sales Person", "name": "销售人员"}],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
            ],
            "config": {
                "title": "销售人员业绩排名",
                "xAxis": {"title": "销售人员"},
                "yAxis": {"title": "销售额"},
                "sort": {"field": "Amount", "order": "desc"},
            },
        },
    },
    {
        "case": "国际市场拓展分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Country", "Amount"],
            },
            "type": "pie",
            "dimensions": [{"field": "Country", "name": "国家"}],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
            ],
            "config": {
                "title": "各国家销售份额",
                "legend": {"position": "right"},
                "tooltip": {"formatter": "{b}: {c} ({d}%)"},
            },
        },
    },
    {
        "case": "销售趋势监控",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Date", "Amount"],
            },
            "type": "line",
            "dimensions": [{"field": "Date", "name": "日期"}],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
            ],
            "config": {
                "title": "销售额趋势",
                "xAxis": {"title": "日期"},
                "yAxis": {"title": "销售额"},
                "tooltip": {"trigger": "axis"},
            },
        },
    },
    {
        "case": "产品性价比分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Product", "Amount", "Boxes Shipped"],
            },
            "type": "bar",
            "dimensions": [{"field": "Product", "name": "产品"}],
            "measures": [
                {
                    "field": "Amount/Boxes Shipped",
                    "name": "箱均价值",
                    "aggregation": "custom",
                    "formula": "sum(Amount)/sum(`Boxes Shipped`)",
                },
            ],
            "config": {
                "title": "产品箱均价值",
                "xAxis": {"title": "产品"},
                "yAxis": {"title": "箱均价值"},
                "tooltip": {"formatter": "{b}: {c}"},
            },
        },
    },
    {
        "case": "销售与发货关系分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Product", "Amount", "Boxes Shipped"],
            },
            "type": "scatter",
            "dimensions": [{"field": "Product", "name": "产品"}],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
                {"field": "Boxes Shipped", "name": "发货箱数", "aggregation": "sum"},
            ],
            "config": {
                "title": "销售额与发货量关系",
                "xAxis": {"title": "销售额"},
                "yAxis": {"title": "发货箱数"},
                "tooltip": {"formatter": "{a}: {c}"},
            },
        },
    },
    {
        "case": "顶级市场双指标分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Country", "Amount", "Boxes Shipped"],
            },
            "type": "dual",
            "dimensions": [{"field": "Country", "name": "国家"}],
            "measures": [
                {
                    "field": "Amount",
                    "name": "销售额",
                    "aggregation": "sum",
                    "yAxisIndex": 0,
                },
                {
                    "field": "Boxes Shipped",
                    "name": "发货箱数",
                    "aggregation": "sum",
                    "yAxisIndex": 1,
                },
            ],
            "config": {
                "title": "主要国家销售额与发货量",
                "xAxis": {"title": "国家"},
                "yAxis": [
                    {"title": "销售额", "position": "left"},
                    {"title": "发货箱数", "position": "right"},
                ],
                "tooltip": {"trigger": "axis"},
            },
        },
    },
    {
        "case": "销售热度地图",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Sales Person", "Country", "Amount"],
            },
            "type": "heatmap",
            "dimensions": [
                {"field": "Sales Person", "name": "销售人员"},
                {"field": "Country", "name": "国家"},
            ],
            "measures": [
                {"field": "Amount", "name": "销售额", "aggregation": "sum"},
            ],
            "config": {
                "title": "销售人员各国家业绩热力图",
                "xAxis": {"title": "国家"},
                "yAxis": {"title": "销售人员"},
                "visualMap": {
                    "show": True,
                    "calculable": True,
                    "orient": "horizontal",
                    "left": "center",
                    "bottom": "5%",
                },
            },
        },
    },
    {
        "case": "销售时段分析",
        "chart_config": {
            "dataSource": {
                "table": "wedata.chocolate_sales",
                "fields": ["Date", "Amount"],
            },
            "type": "column",
            "dimensions": [{"field": "Date", "name": "日期", "group": "month"}],
            "measures": [
                {"field": "Amount", "name": "月度销售额", "aggregation": "sum"},
            ],
            "config": {
                "title": "月度销售额分析",
                "xAxis": {"title": "月份"},
                "yAxis": {"title": "销售额"},
                "tooltip": {"trigger": "axis"},
            },
        },
    },
]
