# DeepSeek LLM 集成

本文档描述了如何使用 DeepSeek API 与多智能体系统集成。

## 功能概述

此集成实现了以下功能：

1. 基于任务类型选择不同的 DeepSeek 模型：
   - 普通任务 (`basic`): 使用 `deepseek-chat`
   - 复杂推理任务 (`reasoning`): 使用 `deepseek-reasoner`

2. LangChain 兼容的 LLM 客户端：
   - 提供 `invoke`、`stream` 方法
   - 处理各种消息格式并正确转换

3. API 处理：
   - 异步调用 DeepSeek API
   - 流式响应处理
   - 错误处理和重试机制

## 设置与使用

### 环境设置

1. 设置 API 密钥：
   ```bash
   export DEEPSEEK_API_KEY=your_api_key_here
   ```

2. 安装依赖 (如果尚未安装)：
   ```bash
   pip install -r requirements.txt
   ```

### 运行测试

测试脚本位于 `examples` 目录中。可通过以下命令运行测试：

```bash
# 先确保设置 PYTHONPATH
export PYTHONPATH=/Users/aleksichen/git/data-agent:$PYTHONPATH

# 运行 coordinator 测试
python examples/test_coordinator.py

# 运行 LLM 集成测试
python examples/test_llm_integration.py

# 运行完整工作流测试
python examples/test_langgraph_workflow.py
```

也可以使用提供的 shell 脚本运行所有测试：

```bash
chmod +x run_tests.sh
./run_tests.sh
```

## 组件说明

### `get_llm_by_type` 函数

此函数根据任务类型返回适当的 LLM 实例：

```python
# 示例
from src.llm.llm import get_llm_by_type

# 获取基本 LLM (deepseek-chat)
basic_llm = get_llm_by_type("basic")

# 获取推理 LLM (deepseek-reasoner)
reasoning_llm = get_llm_by_type("reasoning")
```

### 消息转换

`src/llm/transform/openai_format.py` 提供了消息格式转换功能：

```python
from src.llm.transform.openai_format import convert_to_openai_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 创建消息
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Hello!"),
    AIMessage(content="Hello! How can I help you?")
]

# 转换为 OpenAI 格式
openai_messages = convert_to_openai_messages(messages)
```

### coordinator_node 中的使用

`coordinator_node` 已经集成了 LLM 客户端：

```python
from src.graph.nodes.coordinator import coordinator_node
from src.graph.types import State
from langchain_core.messages import HumanMessage

# 创建状态
state = State(
    messages=[HumanMessage(content="你好，请帮我分析数据")],
    next="",
    full_plan="",
    deep_thinking_mode=False,
    search_before_planning=False,
    TEAM_MEMBERS=["coordinator", "planner", "supervisor", "researcher", "coder", "browser", "reporter"]
)

# 调用协调员节点
result = coordinator_node(state)
```

## 调试提示

1. 如果遇到导入错误，确保正确设置了 `PYTHONPATH`：
   ```bash
   export PYTHONPATH=/Users/aleksichen/git/data-agent:$PYTHONPATH
   ```

2. 如果遇到 API 错误，确保：
   - 已设置正确的 API 密钥
   - 网络连接正常
   - API 请求格式正确

3. 对于事件循环问题：
   - 检查是否有嵌套的事件循环
   - 使用单独的事件循环处理异步调用

## 常见问题

1. **消息格式错误**
   - 问题：DeepSeek API 返回消息格式错误
   - 解决：确保使用 `convert_to_openai_messages` 函数转换消息

2. **事件循环错误**
   - 问题：`RuntimeError: This event loop is already running`
   - 解决：使用我们实现的 `LangChainCompatibleLLM` 类，它能处理事件循环问题

3. **模型选择**
   - 问题：如何为不同的节点选择不同的模型？
   - 解决：编辑 `src/config/agents.py` 中的 `AGENT_LLM_MAP` 配置
