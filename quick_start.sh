#!/usr/bin/env bash
set -e

echo "== AI 内测推广日程管理器：新手快速启动 =="

if ! command -v python3 >/dev/null 2>&1; then
  echo "❌ 没有找到 python3，请先安装 Python 3.9+"
  exit 1
fi

echo "✅ 检测到 Python：$(python3 --version)"

echo "\n[1/3] 初始化示例任务..."
python3 scheduler.py seed

echo "\n[2/3] 查看当前任务..."
python3 scheduler.py list

echo "\n[3/3] 查看仪表盘..."
python3 scheduler.py dashboard

echo "\n🎉 完成！你现在可以照 README 的示例继续新增/更新任务。"
