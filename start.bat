@echo off
REM Windows快速启动脚本

cd /d "%~dp0"

REM 激活虚拟环境并启动应用
call .venv\Scripts\activate.bat
python main.py
pause
