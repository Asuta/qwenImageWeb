@echo off
chcp 65001 >nul
title 图像生成 AI 工具 - 本地服务器

echo ================================================
echo 🎨 图像生成 AI 工具 - 本地服务器
echo ================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未找到Python，请先安装Python 3.6+
    echo 💡 下载地址: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python已安装
echo 🚀 正在启动服务器...
echo.

REM 启动Python服务器
python start-server.py

pause
