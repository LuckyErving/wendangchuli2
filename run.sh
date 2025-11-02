#!/bin/bash
# 启动脚本（使用 Python 3.11）

cd "$(dirname "$0")"
source .venv311/bin/activate
python main.py
