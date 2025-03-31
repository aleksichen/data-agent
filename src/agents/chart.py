from agno.agent import Agent, RunResponse
from agno.models.deepseek import DeepSeek

chart_agent = Agent(
  name="图表渲染Agent",
  model=DeepSeek(),
  instructions=[
    """
    # 图表渲染Agent指令
    
    你是一个专业的数据可视化图表渲染助手。你的任务是基于提供的数据分析结果，生成前端可渲染的图表配置JSON。
    
    ## 重要：输出格式
    
    你必须严格按照以下JSON格式返回数据，不得有任何偏差：
    
    ```json
    {
      "type": "<图表类型>",
      "dataSource": {
        "table": "<数据源表名>",
        "field": [<字段列表>]
      },
      "dimensions": [
        {
          "field": "<维度字段>",
          "name": "<维度显示名>"
        }
      ],
      "measures": [
        {
          "field": "<度量字段>",
          "name": "<度量显示名>"
        }
      ],
      "series": {
        "field": "<系列字段>",
        "name": "<系列显示名>"
      },
      "config": {
        "title": "<图表标题>",
        // 可选配置项
      }
    }
    ```
    
    ## 支持的图表类型
    
    - `bar`: 柱状图，适用于分类数据比较
    - `line`: 折线图，适用于时间序列数据和趋势分析
    - `pie`: 饼图，适用于占比分析
    - `scatter`: 散点图，适用于相关性分析
    - `area`: 面积图，适用于累计趋势分析
    - `heatmap`: 热力图，适用于多维度数据密度展示
    - `radar`: 雷达图，适用于多维度对比分析
    - `funnel`: 漏斗图，适用于转化率分析
    
    ## 字段说明
    
    - `type`: 必选，图表类型
    - `dataSource`: 必选，数据源信息
      - `table`: 必选，数据表ID或名称
      - `field`: 必选，需要的字段列表
    - `dimensions`: 必选，维度设置（类别轴，通常是X轴）
      - `field`: 必选，维度字段名
      - `name`: 必选，维度显示名称
    - `measures`: 必选，度量设置（数值轴，通常是Y轴）
      - `field`: 必选，度量字段名
      - `name`: 必选，度量显示名称
    - `series`: 可选，系列设置（用于多系列数据）
      - `field`: 必选，系列字段名
      - `name`: 必选，系列显示名称
    - `config`: 必选，图表配置
      - `title`: 必选，图表标题
      - `height`: 可选，图表高度
      - `colors`: 可选，颜色配置
      - `stacked`: 可选，是否堆叠
      - `fillOpacity`: 可选，填充透明度
      - `sizeField`: 可选，大小映射字段（散点图）
    
    ## 图表类型选择指南
    
    1. 时间趋势数据 -> 折线图(line)或面积图(area)
    2. 类别比较数据 -> 柱状图(bar)
    3. 占比分析 -> 饼图(pie)
    4. 相关性分析 -> 散点图(scatter)
    5. 多维度数据密度 -> 热力图(heatmap)
    6. 多指标对比 -> 雷达图(radar)
    7. 转化率/流程数据 -> 漏斗图(funnel)
    
    ## 响应要求
    
    1. 只返回纯JSON对象，不要有任何额外的解释文本
    2. 确保JSON格式正确无误，所有引号必须是双引号
    3. 所有字段名必须使用英文且与模板完全一致
    4. 字段值必须根据实际分析内容填写，且使用合适的数据类型
    5. 对于中文内容的展示名称，需使用双引号包裹
    
    ## 处理流程
    
    1. 分析接收到的数据内容和分析结果
    2. 识别数据的主要模式和关系
    3. 选择最适合的图表类型
    4. 确定合适的维度和度量字段
    5. 构建符合要求的JSON配置
    6. 验证JSON格式的正确性
    7. 返回最终配置
    
    你的输出将直接用于前端图表渲染，任何格式错误都会导致渲染失败，所以必须保证格式的绝对正确性。"""
  ],
  markdown=True
)

# Test Case 1: Monthly Sales Trend by Category
def test_monthly_sales_trend():
    previous_agent_data = """
    我已经完成了销售数据的分析，以下是关键发现：
    
    数据存储在数据库表 sales_quarterly_data 中，包含以下字段:
    - month (月份，字符串格式如"1月"、"2月")
    - category (产品类别)
    - sales (销售额，数值)
    - profit (利润，数值)
    - customers (客户数，数值)
    
    按月份和产品类别的销售额统计结果示例:
    
    | 月份  | 类别     | 销售额  | 利润   | 客户数 |
    |------|----------|--------|--------|-------|
    | 1月  | 电子产品 | 120000 | 34500  | 450   |
    | 1月  | 家居用品 | 85000  | 25000  | 320   |
    | 2月  | 电子产品 | 135000 | 38700  | 470   |
    | 2月  | 家居用品 | 92000  | 27800  | 350   |
    | 3月  | 电子产品 | 142000 | 41180  | 490   |
    | 3月  | 家居用品 | 98000  | 29400  | 380   |
    
    数据显示电子产品在所有月份的销售额和利润都高于家居用品，且两类产品都呈现逐月增长趋势。
    
    请为这个销售趋势数据生成合适的可视化配置。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 2: Product Category Distribution
def test_product_category_distribution():
    previous_agent_data = """
    产品类别销售占比分析完成，数据来源于表 product_sales，表结构如下:
    
    字段说明:
    - category: 产品类别名称
    - total_sales: 销售总额(数值)
    - percentage: 占总销售额的百分比(数值，0-100)
    
    数据示例:
    
    | 产品类别 | 销售总额  | 占比  |
    |---------|----------|------|
    | 电子产品 | 4250000  | 42.5 |
    | 家居用品 | 2830000  | 28.3 |
    | 服装    | 1640000  | 16.4 |
    | 食品    | 860000   | 8.6  |
    | 其他    | 420000   | 4.2  |
    
    可以看出电子产品占据了近一半的销售额，电子产品和家居用品合计超过70%的销售份额。
    请为这个数据提供合适的可视化方式。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 3: Sales vs Profit Correlation Analysis
def test_sales_profit_correlation():
    previous_agent_data = """
    我已分析了各区域销售门店的销售额与利润的相关性，数据源是 store_performance 表。
    
    表结构：
    - store_id: 门店唯一标识符
    - region: 区域名称
    - sales: 销售额(数值)
    - profit: 利润(数值)
    - area: 店面面积(数值，单位平方米)
    - employees: 员工数量(数值)
    
    数据示例:
    
    | 门店ID | 区域  | 销售额  | 利润   | 店面面积 | 员工数 |
    |-------|------|--------|--------|---------|-------|
    | S001  | 北区 | 856000 | 214000 | 320     | 24    |
    | S002  | 北区 | 765000 | 198900 | 280     | 20    |
    | S003  | 南区 | 912000 | 237120 | 350     | 26    |
    | S004  | 南区 | 689000 | 172250 | 260     | 18    |
    | S005  | 东区 | 578000 | 144500 | 220     | 15    |
    | S006  | 东区 | 623000 | 155750 | 240     | 17    |
    | S007  | 西区 | 734000 | 183500 | 270     | 19    |
    | S008  | 西区 | 802000 | 200500 | 300     | 22    |
    
    数据表明销售额与利润存在很强的正相关关系，且门店规模（面积和员工数）也与销售成绩正相关。
    希望能可视化销售额与利润的关系，并以店面面积为参考因素。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 4: Customer Retention Funnel
def test_customer_retention_funnel():
    previous_agent_data = """
    客户转化漏斗分析已完成，基于customer_journey表。
    
    表结构:
    - stage: 客户旅程阶段名称(字符串)
    - customers: 该阶段的客户数量(数值)
    - conversion_rate: 转化率百分比(数值，0-100)
    
    数据示例:
    
    | 阶段       | 客户数 | 转化率 | 
    |-----------|-------|-------|
    | 浏览网站   | 12000 | 100   |
    | 加入购物车 | 3600  | 30    |
    | 开始结账   | 2400  | 20    |
    | 完成支付   | 1440  | 12    |
    | 复购      | 720   | 6     |
    
    数据显示从浏览到最终复购的转化率仅为6%，最大的客户流失发生在浏览到加入购物车的环节。
    请生成一个合适的可视化以便分析这个转化漏斗。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 5: Multi-dimensional Performance Analysis
def test_performance_radar():
    previous_agent_data = """
    各产品线多维度表现评估完成，数据来自product_performance表。
    
    表结构:
    - product_line: 产品线名称
    - sales_score: 销售额得分(0-100数值)
    - profit_score: 利润率得分(0-100数值)
    - satisfaction_score: 客户满意度得分(0-100数值)
    - market_share_score: 市场份额得分(0-100数值)
    - growth_score: 增长率得分(0-100数值)
    
    数据示例:
    
    | 产品线   | 销售额(分) | 利润率(分) | 客户满意度(分) | 市场份额(分) | 增长率(分) |
    |---------|----------|----------|--------------|-----------|----------|
    | A系列    | 85       | 76       | 92           | 65        | 78       |
    | B系列    | 92       | 68       | 84           | 72        | 86       |
    | C系列    | 78       | 82       | 88           | 58        | 65       |
    | D系列    | 67       | 91       | 75           | 46        | 59       |
    
    这是一个基于100分制的多维度评分表，希望能看到各产品线在不同维度上的表现对比。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 6: Monthly Website Traffic Area Chart
def test_website_traffic_area():
    previous_agent_data = """
    网站流量分析完成，数据来源于website_analytics表。
    
    表结构:
    - month: 月份(字符串，如"1月")
    - channel: 流量渠道名称
    - visits: 访问量(数值)
    
    数据示例:
    
    | 月份   | 渠道     | 访问量  | 
    |-------|----------|--------|
    | 1月   | 自然搜索 | 45600  | 
    | 1月   | 社交媒体 | 32400  | 
    | 1月   | 直接访问 | 28700  | 
    | 2月   | 自然搜索 | 48200  | 
    | 2月   | 社交媒体 | 35800  | 
    | 2月   | 直接访问 | 30100  | 
    | 3月   | 自然搜索 | 52400  | 
    | 3月   | 社交媒体 | 38900  | 
    | 3月   | 直接访问 | 32800  |
    | 4月   | 自然搜索 | 58700  |
    | 4月   | 社交媒体 | 42300  |
    | 4月   | 直接访问 | 35400  |
    
    数据显示各渠道流量都在逐月增长，想看到累计和不同渠道的占比变化。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 7: Regional Heat Map
def test_regional_heatmap():
    previous_agent_data = """
    我们已完成各地区销售密度分析，数据存储在regional_sales表中。
    
    表结构:
    - province: 省份名称
    - city: 城市名称
    - sales_density: 每平方公里销售额(数值)
    - store_count: 门店数量(数值)
    
    数据摘要(部分数据):
    
    | 省份 | 城市   | 销售密度 | 门店数 |
    |-----|--------|---------|--------|
    | 广东 | 广州   | 1250    | 35     |
    | 广东 | 深圳   | 1680    | 42     |
    | 广东 | 东莞   | 820     | 18     |
    | 江苏 | 南京   | 980     | 24     |
    | 江苏 | 苏州   | 1120    | 28     |
    | 江苏 | 无锡   | 750     | 15     |
    | 浙江 | 杭州   | 1050    | 26     |
    | 浙江 | 宁波   | 870     | 20     |
    | 浙江 | 温州   | 690     | 16     |
    
    完整数据包含全国各主要城市，我们希望通过热力图直观展示各地区销售密度差异。
    """
    
    return chart_agent.print_response(previous_agent_data)

# Test Case 8: Age Group Analysis
def test_age_group_analysis():
    previous_agent_data = """
    我们分析了不同年龄段客户的消费习惯，数据来源于customer_age_analysis表。
    
    表结构:
    - age_group: 年龄段(字符串，如"18-24岁")
    - average_spend: 平均消费金额(数值)
    - purchase_frequency: 月均购买频次(数值)
    - online_ratio: 线上购买比例(数值，0-100)
    
    数据示例:
    
    | 年龄段   | 平均消费金额 | 月均购买频次 | 线上购买比例 |
    |---------|------------|------------|------------|
    | 18-24岁 | 580        | 4.2        | 78         |
    | 25-34岁 | 920        | 3.8        | 65         |
    | 35-44岁 | 1250       | 2.9        | 42         |
    | 45-54岁 | 980        | 2.3        | 28         |
    | 55-64岁 | 720        | 1.8        | 15         |
    | 65岁以上 | 450        | 1.2        | 8          |
    
    数据显示年轻群体购买频次高且更偏好线上渠道，35-44岁群体平均消费金额最高。
    请为这些数据提供最合适的可视化方式。
    """
    
    return chart_agent.print_response(previous_agent_data)

if __name__ == "__main__":
    # print("\n===== Test Case 1: Monthly Sales Trend =====")
    # test_monthly_sales_trend()
    
    # print("\n===== Test Case 2: Product Category Distribution =====")
    # test_product_category_distribution()
    
    # print("\n===== Test Case 3: Sales vs Profit Correlation =====")
    # test_sales_profit_correlation()
    
    # print("\n===== Test Case 4: Customer Retention Funnel =====")
    # test_customer_retention_funnel()
    
    # print("\n===== Test Case 5: Multi-dimensional Performance Analysis =====")
    # test_performance_radar()
    
    print("\n===== Test Case 6: Website Traffic Area Chart =====")
    test_website_traffic_area()
    
    # print("\n===== Test Case 7: Regional Heat Map =====")
    # test_regional_heatmap()
    
    # print("\n===== Test Case 8: Age Group Analysis =====")
    # test_age_group_analysis()