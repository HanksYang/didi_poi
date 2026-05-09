#!/usr/bin/env python3
"""
打包脚本：为不同平台生成可执行文件和分发包
使用方法: python3 package.py [--macos | --windows | --linux | --all]
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import argparse

PROJECT_DIR = Path(__file__).parent
DIST_DIR = PROJECT_DIR / 'dist'
BUILD_DIR = PROJECT_DIR / 'build'
RELEASE_DIR = PROJECT_DIR / 'releases'

def clean_build():
    """清理之前的构建"""
    print("🧹 清理旧的构建文件...")
    for d in [BUILD_DIR, DIST_DIR]:
        if d.exists():
            shutil.rmtree(d)
    print("✓ 清理完成\n")

def build_pyinstaller(spec_file='build.spec'):
    """运行 PyInstaller 构建"""
    print(f"🔨 使用 PyInstaller 构建可执行文件...")
    result = subprocess.run(
        ['pyinstaller', spec_file, '--noconfirm'],
        cwd=PROJECT_DIR,
        capture_output=False
    )
    return result.returncode == 0

def create_release_package():
    """创建发布包"""
    print("📦 创建发布包...")

    RELEASE_DIR.mkdir(exist_ok=True)

    # 确定平台
    system = platform.system()
    arch = platform.machine()

    if system == 'Darwin':
        platform_name = 'macOS'
        exe_name = 'DiDi_POI热点系统'
        package_name = f'DiDi-POI-热点系统-macOS-{arch}'
    elif system == 'Windows':
        platform_name = 'Windows'
        exe_name = 'DiDi_POI热点系统.exe'
        package_name = f'DiDi-POI-热点系统-Windows'
    else:
        platform_name = 'Linux'
        exe_name = 'DiDi_POI热点系统'
        package_name = f'DiDi-POI-热点系统-Linux-{arch}'

    # 创建发布文件夹
    release_folder = RELEASE_DIR / package_name
    if release_folder.exists():
        shutil.rmtree(release_folder)
    release_folder.mkdir()

    # 复制可执行文件
    exe_path = DIST_DIR / exe_name
    if exe_path.exists():
        shutil.copy(exe_path, release_folder / exe_name)
    else:
        print(f"⚠️  警告：找不到可执行文件 {exe_path}")

    # 复制必要文件
    files_to_copy = ['.env', 'README.md', '.env.example']
    for file in files_to_copy:
        src = PROJECT_DIR / file
        if src.exists():
            shutil.copy(src, release_folder / file)

    # 创建运行说明
    instructions = f"""# DiDi POI 热点系统 - {platform_name}

## 🚀 快速开始

1. 解压这个文件夹
2. 双击运行 `{exe_name}` 文件
3. 浏览器会自动打开 http://127.0.0.1:5000

## ⚙️ 功能说明

### 标签页 1️⃣ - 热力图上传
- 拖拽上传热力图图像
- AI 自动识别地点和热度
- 更新 POI 接单热度权重

### 标签页 2️⃣ - 路线规划
- 输入起点和终点地点名称
- 系统自动规划 3 条最优路线
- 显示热度总和、距离、时长、接单评分
- 嵌入地图展示路线详情

### 标签页 3️⃣ - 设置
- 配置高德地图 API Key
- 配置火山引擎 API Key
- 密钥保存到 .env 文件

## 🔧 配置 API Key

首次运行时:
1. 点击"⚙️ 设置"标签页
2. 输入您的高德地图 API Key
3. 输入您的火山引擎 API Key
4. 点击"💾 保存密钥"

## ❌ 遇到问题?

- 如果浏览器未自动打开，手动访问: http://127.0.0.1:5000
- 确保 .env 文件和可执行文件在同一文件夹
- 检查防火墙是否阻止了 5000 端口

## 📞 关于作者

DiDi POI 热点系统 v1.0
基于 Flask + Folium + 高德地图 API

---
按 Ctrl+C 可以停止服务
"""

    readme_path = release_folder / 'README.txt'
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(instructions)

    print(f"✓ 发布包已创建: {release_folder}")

    # 为 Windows 创建启动脚本
    if system == 'Windows':
        bat_content = """@echo off
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
"""
        bat_path = release_folder / '启动.bat'
        with open(bat_path, 'w', encoding='gbk', errors='ignore') as f:
            f.write(bat_content)

    # 创建压缩包
    zip_name = f'{package_name}'
    zip_path = RELEASE_DIR / zip_name

    print(f"📁 压缩文件到: {zip_path}.zip")
    shutil.make_archive(str(zip_path), 'zip', release_folder.parent, package_name)

    print(f"✓ 发布包完成: {zip_path}.zip\n")

    return release_folder

def main():
    parser = argparse.ArgumentParser(
        description='打包 DiDi POI 热点系统为可执行文件'
    )
    parser.add_argument(
        '--target',
        choices=['macos', 'windows', 'linux', 'all'],
        default='all',
        help='目标平台 (默认: 当前平台)'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='清理旧的构建文件'
    )

    args = parser.parse_args()

    print("="*60)
    print("📦 DiDi POI 热点系统打包工具")
    print("="*60 + "\n")

    if args.clean:
        clean_build()

    print(f"🖥️  当前平台: {platform.system()} {platform.machine()}\n")

    # 构建
    if build_pyinstaller():
        print("✅ PyInstaller 构建成功!\n")
        release_dir = create_release_package()

        print("="*60)
        print(f"✅ 打包完成!")
        print(f"📍 可执行文件位置: {release_dir}")
        print("="*60)
    else:
        print("❌ PyInstaller 构建失败")
        sys.exit(1)

if __name__ == '__main__':
    main()
