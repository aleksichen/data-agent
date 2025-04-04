# 基于 Agno 的智能数据分析系统设计

设计了一个综合性的数据分析系统，能够处理各种数据分析场景，与 Doris 数据仓库交互，并提供可视化和报告功能。下面是详细的设计方案：

## 系统架构和 Agent 设计

### 需要的 Agent（共 7 个）

1. **意图分析 Agent (IntentAnalysisAgent)**

   - **功能**：理解用户请求，确定任务类型，提取关键信息
   - **工具**：无需外部工具，主要依靠 LLM 理解能力
   - **输出**：请求类型、需要的数据表、时间范围等结构化信息

2. **数据库模式 Agent (DatabaseSchemaAgent)**

   - **功能**：获取和理解数据库结构，包括表结构和数据示例
   - **工具**：DorisQueryTool（执行 SQL 查询）
   - **输出**：表结构信息，包括列名、数据类型和示例数据

3. **查询生成 Agent (QueryGenerationAgent)**

   - **功能**：生成高效的 SQL 查询以获取所需数据
   - **工具**：DorisQueryTool（验证查询）
   - **输出**：SQL 查询语句及其目的解释

4. **数据清洗 Agent (DataCleaningAgent)**

   - **功能**：识别和解决数据质量问题
   - **工具**：DorisQueryTool（SQL 查询）、PythonExecutionTool（执行 Python 代码）
   - **输出**：数据清洗计划和执行 SQL

5. **数据分析 Agent (DataAnalysisAgent)**

   - **功能**：分析数据，提取洞察和趋势
   - **工具**：DorisQueryTool、PythonExecutionTool
   - **输出**：分析结果，包括关键洞察、指标和趋势

6. **可视化 Agent (VisualizationAgent)**

   - **功能**：创建数据可视化
   - **工具**：ChartRenderingTool（生成图表配置）
   - **输出**：图表配置（类型、维度、度量等）

7. **报告生成 Agent (ReportGenerationAgent)**
   - **功能**：创建综合报告
   - **工具**：无需外部工具，整合分析结果和可视化
   - **输出**：结构化的分析报告

### 工具定义

1. **DorisQueryTool**：执行 SQL 查询并返回结果
2. **PythonExecutionTool**：执行 Python 代码
3. **ChartRenderingTool**：渲染数据可视化图表

## Agent 协作流程

系统采用一个灵活的工作流程，可以根据请求类型动态选择执行路径：

### 通用流程：

1. **意图分析**：首先通过 IntentAnalysisAgent 理解用户请求
2. **路径选择**：根据识别的请求类型（销售报告、数据清洗、业务分析等）选择后续流程
3. **数据获取**：根据需要获取表结构和执行查询
4. **处理与分析**：执行特定的处理和分析
5. **报告生成**：最终生成可视化报告

### 特定场景流程：

#### 场景 1：销售数据报告

1. 意图分析 → 确定为 sales_report 类型
2. 获取 sales 表结构 → 生成 SQL 查询 → 执行查询获取销售数据
3. 分析销售趋势和模式 → 创建销售数据可视化
4. 生成销售分析报告

#### 场景 2：数据清洗

1. 意图分析 → 确定为 data_cleaning 类型
2. 获取目标表结构和样本数据 → 识别数据问题
3. 生成清洗计划 → 执行清洗 SQL
4. 生成清洗报告

#### 场景 3：部门业绩分析

1. 意图分析 → 确定为 business_analysis 类型
2. 获取 departments 和 sales 表结构 → 生成跨表分析 SQL
3. 执行查询 → 分析部门盈利能力
4. 创建业绩可视化 → 生成包含裁员建议的业绩分析报告

## 状态流转控制

Agno 框架提供了灵活的状态流转控制能力：

1. **工作流状态管理**：通过工作流的`run()`方法中的条件逻辑控制流程
2. **事件通知**：使用`RunEvent`枚举类型（如`workflow_step_started`、`workflow_completed`等）进行状态通知
3. **缓存机制**：通过`session_state`保存中间结果，实现状态持久化

## 实现亮点

1. **模块化设计**：每个 Agent 负责特定任务，便于维护和扩展
2. **自适应流程**：根据请求类型动态选择执行路径
3. **缓存优化**：可以缓存查询结果和报告，提高效率
4. **进度反馈**：通过事件通知提供实时进度反馈
5. **错误处理**：每个步骤都有错误捕获和处理

## 总结

这个设计可以很好地支持您提出的三个场景，并且具有良好的扩展性。系统通过多个专业化的 Agent 协作完成复杂的数据分析任务，每个 Agent 专注于自己的领域，并通过工作流进行协调。与 LangGraph 类似，它提供了完全的状态流转控制能力，并且通过纯 Python 实现，更加灵活和直观。
