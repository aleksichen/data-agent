#!/bin/bash

# 脚本用于运行所有测试

# 确保在正确的目录中
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR

echo "正在运行测试..."

# 设置 PYTHONPATH 环境变量
export PYTHONPATH=$SCRIPT_DIR:$PYTHONPATH

# 检查是否已设置 DEEPSEEK_API_KEY 环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "警告: 未设置 DEEPSEEK_API_KEY 环境变量，某些测试可能会失败"
    echo "可以通过以下命令设置: export DEEPSEEK_API_KEY=your_api_key_here"
fi

# 运行 coordinator 测试
echo -e "\n===== 运行 coordinator 测试 ====="
python examples/test_coordinator.py

# 运行 LLM 集成测试
echo -e "\n===== 运行 LLM 集成测试 ====="
python examples/test_llm_integration.py

# 运行工作流测试
echo -e "\n===== 运行工作流测试 ====="
python examples/test_langgraph_workflow.py

echo -e "\n所有测试完成!"
