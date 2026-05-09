@echo off
REM Windows 启动脚本
REM 用户双击此脚本可启动程序

setlocal enabledelayedexpansion
cd /d "%~dp0"

if not exist "DiDi_POI热点系统.exe" (
    echo ❌ 错误：找不到 DiDi_POI热点系统.exe 文件
    pause
    exit /b 1
)

echo 🚀 正在启动 DiDi POI 热点系统...
echo 💡 如浏览器未自动打开，请访问: http://127.0.0.1:5000
echo 按 Ctrl+C 可停止服务
echo.

start "" "DiDi_POI热点系统.exe"
pause
