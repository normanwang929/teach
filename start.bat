@echo off
chcp 65001 > nul
echo ================================================
echo   Teach Platform - 启动服务器
echo ================================================
echo.

REM 使用 managed Python 环境
set PYTHON=C:\Users\norman\.workbuddy\binaries\python\versions\3.13.12\python.exe

echo 🔍 检查依赖...
%PYTHON% -c "import flask" 2>nul
if errorlevel 1 (
    echo ⚠️ 缺少依赖，正在安装...
    %PYTHON% -m pip install flask flask-cors -q
)

echo.
echo 🚀 启动 API 服务器...
echo.
echo 📡 API 服务器：http://localhost:5000
echo 🌐 前端页面：http://localhost:5000
echo.
echo ⚠️  不要关闭此窗口！
echo ⚠️  按 Ctrl+C 停止服务器
echo.
echo ================================================
echo.

%PYTHON% api_server.py

pause
