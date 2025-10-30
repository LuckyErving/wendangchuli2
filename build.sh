#!/bin/bash
# 本地构建脚本（用于测试）

echo "开始构建可执行文件..."

# 激活虚拟环境
source .venv/bin/activate

# 使用spec文件构建
pyinstaller main.spec

echo "构建完成！"
echo "可执行文件位于: dist/文档处理工具"
