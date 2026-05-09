#!/usr/bin/env python3
"""
跨平台构建和发布脚本
用于在不同操作系统上生成可执行文件

使用方法:
  python3 build_all_platforms.py              # 仅本地平台
  python3 build_all_platforms.py --doc        # 生成文档
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path
import argparse

PROJECT_DIR = Path(__file__).parent
RELEASES_DIR = PROJECT_DIR / 'releases'

def print_banner(text):
    """打印标题"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60 + "\n")

def build_current_platform():
    """为当前平台构建"""
    system = platform.system()
    machine = platform.machine()

    print_banner(f"为 {system} ({machine}) 构建")

    # 运行 PyInstaller
    result = subprocess.run(
        ['pyinstaller', 'build.spec', '--noconfirm'],
        cwd=PROJECT_DIR
    )

    if result.returncode != 0:
        print("❌ 构建失败")
        return False

    print("✅ 构建成功")
    return True

def create_cross_platform_docs():
    """创建跨平台部署文档"""
    print_banner("生成部署文档")

    docs_content = """# DiDi POI 热点系统 - 部署指南

## 🎯 三种部署方式

### 方式 1️⃣: 独立可执行文件（推荐）⭐⭐⭐

**适用场景**: 无需 Python 环境，开箱即用

#### macOS 用户:
```bash
cd DiDi-POI-热点系统-macOS-arm64
chmod +x DiDi_POI热点系统
./DiDi_POI热点系统
# 或直接双击 启动.sh
```

#### Windows 用户:
```
双击 启动.bat
或
双击 DiDi_POI热点系统.exe
```

#### Linux 用户:
```bash
cd DiDi-POI-热点系统-Linux-x64
chmod +x DiDi_POI热点系统
./DiDi_POI热点系统
```

---

### 方式 2️⃣: Docker 容器

**适用场景**: 云部署、跨平台部署

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt
ENV FLASK_APP=web_app.py

EXPOSE 5000
CMD ["python3", "web_app.py", "--host", "0.0.0.0"]
```

运行:
```bash
docker build -t didi-poi .
docker run -p 5000:5000 -v $(pwd)/.env:/.env didi-poi
```

---

### 方式 3️⃣: 源代码部署

**适用场景**: 开发环境、需要修改代码

```bash
# 1. 安装 Python 3.8+
# 2. 克隆项目
git clone <repo>

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 配置环境
cp .env.example .env
# 编辑 .env，填入 API Key

# 5. 运行
python3 web_app.py --host 127.0.0.1 --port 5000
```

---

## 📊 方式对比

| 特性 | 独立可执行 | Docker | 源代码 |
|------|---------|--------|--------|
| 文件大小 | ~33MB | ~500MB | 几 KB |
| 启动速度 | ⚡ 快 | ⚠️ 慢 | ⚡ 快 |
| 依赖配置 | ✅ 零配置 | ✅ 简单 | ❌ 复杂 |
| 跨平台 | ❌ 需分别构建 | ✅ 统一 | ✅ 统一 |
| 开发友好 | ❌ 不友好 | ✅ 友好 | ✅ 友好 |
| 生产部署 | ✅ 完美 | ✅ 完美 | ⚠️ 可用 |

---

## 🛠️ 生成多平台可执行文件

### 在 macOS 上生成

```bash
# 仅 macOS ARM64
python3 build_all_platforms.py

# 如需 macOS x86_64
# 在 Intel Mac 上运行同样命令
```

### 在 Windows 上生成

```cmd
python3 build_all_platforms.py
```

### 在 Linux 上生成

```bash
python3 build_all_platforms.py
```

### ⚠️ 交叉编译限制

PyInstaller **不支持交叉编译**，这意味着:
- 在 macOS 生成 macOS 可执行文件 ✅
- 在 macOS 生成 Windows 可执行文件 ❌

**解决方案**:
1. 在不同平台的机器上分别构建
2. 使用 GitHub Actions 自动化多平台构建
3. 使用虚拟机运行其他操作系统

---

## 🚀 使用 GitHub Actions 自动化构建

创建 `.github/workflows/build.yml`:

```yaml
name: Build Executables

on: [push]

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip3 install pyinstaller
      - run: pyinstaller build.spec --noconfirm
      - uses: actions/upload-artifact@v2
        with:
          name: didi-poi-macos
          path: dist/

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip3 install pyinstaller
      - run: pyinstaller build.spec --noconfirm
      - uses: actions/upload-artifact@v2
        with:
          name: didi-poi-windows
          path: dist/

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - run: pip3 install pyinstaller
      - run: pyinstaller build.spec --noconfirm
      - uses: actions/upload-artifact@v2
        with:
          name: didi-poi-linux
          path: dist/
```

---

## 📝 版本信息

- **应用名称**: DiDi POI 热点系统
- **版本**: v1.0
- **Python**: 3.8+
- **框架**: Flask
- **打包工具**: PyInstaller 6.20+

---

## 🔍 验证构建

```bash
# 显示文件大小
ls -lh dist/DiDi_POI热点系统

# 测试运行
./dist/DiDi_POI热点系统

# 检查依赖
otool -L dist/DiDi_POI热点系统  # macOS
ldd dist/DiDi_POI热点系统       # Linux
```

---

## 📦 发布检查清单

- [ ] 在 macOS ARM64 上构建
- [ ] 在 macOS x86_64 上构建（可选）
- [ ] 在 Windows 10/11 上构建
- [ ] 在 Linux x86_64 上构建
- [ ] 测试所有可执行文件
- [ ] 验证 .env 文件被包含
- [ ] 验证 templates/ 目录被包含
- [ ] 创建 README 和使用说明
- [ ] 上传到 GitHub Releases
- [ ] 更新版本号
- [ ] 发布公告

---

**最后更新**: 2026-05-06
"""

    guide_path = PROJECT_DIR / 'DEPLOYMENT_GUIDE_FULL.md'
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(docs_content)

    print(f"✓ 文档已生成: {guide_path}")

def main():
    parser = argparse.ArgumentParser(description='DiDi POI 跨平台构建脚本')
    parser.add_argument('--doc', action='store_true', help='仅生成文档')
    parser.add_argument('--clean', action='store_true', help='清理旧构建')

    args = parser.parse_args()

    print_banner("DiDi POI 热点系统 - 构建工具")

    if args.doc:
        create_cross_platform_docs()
        return

    if args.clean:
        for d in ['build', 'dist']:
            p = PROJECT_DIR / d
            if p.exists():
                shutil.rmtree(p)
        print("✓ 已清理旧构建\n")

    if build_current_platform():
        create_cross_platform_docs()
        print_banner("✅ 构建完成！")
        print(f"📁 输出目录: {PROJECT_DIR / 'dist'}\n")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
