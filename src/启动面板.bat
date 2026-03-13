@echo off
chcp 65001 >nul 2>&1
echo 正在初始化AI创业快捷面板...
echo ==============================

:: 自动安装依赖（首次运行需要）
pip install flask pyautogui >nul 2>&1

:: 启动服务
cd /d "%~dp0"
python -X utf8 server.py

pause