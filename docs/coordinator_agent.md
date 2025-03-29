# 协调员智能体 (Coordinator Agent)

协调员智能体是多智能体系统中的第一个接触点，负责用户交互和任务分类。它是用户与智能体系统之间的主要接口，能够处理简单任务并将复杂任务委派给规划员。

## 功能概述

协调员智能体有以下主要功能：

1. **任务分类**：
   - 识别并处理简单任务（如问候、闲聊）
   - 将复杂任务转交给规划员智能体

2. **用户交互**：
   - 介绍自己（作为DataAgent）
   - 响应问候和闲聊
   - 委婉拒绝不适当或有害的请求

3. **流程控制**：
   - 简单任务：直接处理并结束流程
   - 复杂任务：委派给规划员并继续流程

## 实现细节

协调员节点实现在 `src/graph/nodes/coordinator.py` 中，核心工作流程如下：

1. 从当前状态中获取最新的用户消息
2. 加载协调员提示模板
3. 调用LLM以分析用户请求
4. 根据LLM的响应决定：
   - 如果包含 `handoff_to_planner()`：转交给规划员
   - 否则：直接回复用户并结束流程

## 使用的提示模板

协调员使用 `coordinator.md` 作为提示模板，该模板指导LLM如何分类任务并生成适当的响应。

## 测试与验证

协调员智能体可通过以下方式进行测试：

1. **单元测试**：
   - 使用模拟LLM测试简单任务处理
   - 测试复杂任务委派逻辑
   - 测试边缘情况（如空消息）

2. **独立脚本测试**：
   - 使用 `examples/test_coordinator.py` 测试单独的协调员功能
   - 支持使用模拟LLM或真实LLM进行测试

3. **整合工作流测试**：
   - 使用 `examples/test_langgraph_workflow.py` 测试在完整工作流中的表现
   - 验证与其他节点的交互

## 使用示例

以下是使用协调员的简单示例：

```python
from langchain_core.messages import HumanMessage
from src.graph.types import State
from src.graph.nodes.coordinator import coordinator_node

# 创建状态
state = State(
    messages=[HumanMessage(content="你好，我是新用户")],
    next="",
    full_plan="",
    deep_thinking_mode=False,
    search_before_planning=False,
    TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
)

# 调用协调员节点
result = coordinator_node(state)

# 检查结果
if result.goto == "__end__":
    print("简单任务，直接回复")
elif result.goto == "planner":
    print("复杂任务，转交给规划员")
```

## 后续优化方向

1. 改进任务分类能力，减少误分类
2. 增强上下文理解能力
3. 提供更多对话管理功能（如澄清问题、管理对话历史）
4. 添加用户意图识别
