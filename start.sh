#!/bin/bash
# 快速启动脚本

# 设置当前目录为脚本所在目录
cd "$(dirname "$0")"

# 激活虚拟环境并启动应用
source .venv/bin/activate
python main.py
