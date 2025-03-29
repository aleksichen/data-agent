# Data Agent 测试框架

这个目录包含为 Data Agent 项目设计的测试驱动开发（TDD）测试框架。

## 目录结构

- `unit/`: 单元测试，测试单个组件的功能
- `integration/`: 集成测试，测试多个组件的交互
- `conftest.py`: 公共测试工具和夹具

## 运行测试

安装测试依赖：

```bash
pip install -e ".[test]"
```

运行所有测试：

```bash
pytest
```

运行单元测试：

```bash
pytest tests/unit/
```

运行集成测试：

```bash
pytest tests/integration/
```

运行带覆盖率报告的测试：

```bash
pytest --cov=src
```

## TDD 工作流

1. 先编写一个失败的测试，明确定义预期行为
2. 实现最小代码使测试通过
3. 重构代码，保持测试通过
4. 添加新功能时重复此过程

## 测试顺序建议

1. 首先测试 `types.py`，确保类型定义正确
2. 然后测试单个节点函数
3. 测试简单的节点组合
4. 测试完整的工作流

## 模拟策略

为了避免在测试中使用真实的LLM，我们使用以下策略：

1. 使用 `mock_llm` 夹具来模拟LLM响应
2. 使用 `patch` 来替换真实的API调用
3. 使用预定义的响应来模拟不同场景

## 调试测试

如果测试失败，可以使用以下命令获取详细输出：

```bash
pytest -v --log-cli-level=DEBUG
```

也可以使用 `-k` 参数只运行特定的测试：

```bash
pytest -k "test_supervisor_node"
```
