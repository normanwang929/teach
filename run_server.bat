@echo off
chcp 65001 > nul
cd /d C:\Users\norman\WorkBuddy\2026-06-30-23-01-30

echo ================================================
echo   Teach Platform - API 服务器
echo ================================================
echo.

set PYTHON=C:\Users\norman\.workbuddy\binaries\python\versions\3.13.12\python.exe

echo 正在启动服务器...
echo.
echo 前端页面: http://localhost:5000
echo API 接口: http://localhost:5000/api/generate
echo.
echo 不要关闭此窗口！
echo ================================================
echo.

%PYTHON% api_server.py

pause
