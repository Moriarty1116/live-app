@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================================
echo   PersonalManagerApp - APK 打包工具
echo   (Windows 快捷启动器)
echo ==========================================
echo.

:: 检查 WSL 是否安装
wsl --list --quiet >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 WSL（Windows Subsystem for Linux）
    echo.
    echo 请先安装 WSL：
    echo   1. 以管理员身份打开 PowerShell
    echo   2. 运行: wsl --install -d Ubuntu-22.04
    echo   3. 重启电脑
    echo   4. 完成 Ubuntu 初始化设置
    echo.
    pause
    exit /b 1
)

echo [信息] 检测到 WSL 环境
echo.

:: 设置项目路径（Windows 格式）
set "PROJECT_DIR=C:\Users\JXGM\AppData\Roaming\Tencent\Marvis\User\oAN1i2Tn_pzTx4sNh59hSSLCXd_8\workspace\conv_19f0e5d64cf_b689032d9157\output\PersonalManagerApp"

:: 检查项目目录是否存在
if not exist "%PROJECT_DIR%" (
    echo [错误] 未找到项目目录: %PROJECT_DIR%
    pause
    exit /b 1
)

echo [信息] 项目目录: %PROJECT_DIR%
echo.

:: 转换为 WSL 路径格式
set "WSL_PROJECT_DIR=/mnt/c/Users/JXGM/AppData/Roaming/Tencent/Marvis/User/oAN1i2Tn_pzTx4sNh59hSSLCXd_8/workspace/conv_19f0e5d64cf_b689032d9157/output/PersonalManagerApp"

echo ==========================================
echo   选择操作模式
echo ==========================================
echo.
echo   [1] 首次打包（自动安装所有依赖 + 打包）
echo   [2] 增量打包（仅重新编译，跳过依赖安装）
echo   [3] 清理缓存后重新打包
echo   [4] 查看打包指南
echo   [5] 退出
echo.
set /p choice=请输入选项 (1-5): 

if "%choice%"=="1" goto first_build
if "%choice%"=="2" goto incremental_build
if "%choice%"=="3" goto clean_build
if "%choice%"=="4" goto show_guide
if "%choice%"=="5" goto end

echo [错误] 无效选项
pause
exit /b 1

:first_build
echo.
echo [模式] 首次打包（完整环境配置）
echo.
echo 正在启动 WSL 并执行自动配置脚本...
echo.
echo ⚠️  注意：首次运行需要下载 SDK/NDK（约 1-2 GB），耗时 30-60 分钟
echo.
wsl bash "%WSL_PROJECT_DIR%/setup_wsl_build.sh"
goto end

:incremental_build
echo.
echo [模式] 增量打包（快速编译）
echo.
wsl bash -c "cd '%WSL_PROJECT_DIR%' && buildozer android debug"
goto end

:clean_build
echo.
echo [模式] 清理缓存后重新打包
echo.
echo 这将删除 .buildozer 目录和 bin 目录中的旧文件...
set /p confirm=确认继续？(y/n): 
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b 0
)
wsl bash -c "cd '%WSL_PROJECT_DIR%' && rm -rf .buildozer bin && buildozer android debug"
goto end

:show_guide
echo.
echo [信息] 打开打包指南...
start "" "%PROJECT_DIR%\APK_BUILD_GUIDE.md"
goto end

:end
echo.
echo ==========================================
echo   操作完成
echo ==========================================
echo.
echo APK 文件位置（如果生成成功）:
echo   %PROJECT_DIR%\bin\
echo.
pause
