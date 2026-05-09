# 🚀 DiDi POI 热点系统 - 分发和部署指南

## 📋 目录

1. [快速开始](#快速开始)
2. [三种部署方式](#三种部署方式)
3. [文件说明](#文件说明)
4. [常见问题](#常见问题)

---

## 快速开始

### 🎯 最简单的方式：使用独立可执行文件

#### macOS:
```bash
# 1. 进入文件夹
cd DiDi-POI-热点系统-macOS-arm64

# 2. 运行程序（三选一）
方案 A：双击 启动.sh
方案 B：./DiDi_POI热点系统
方案 C：chmod +x DiDi_POI热点系统 && ./DiDi_POI热点系统

# 3. 浏览器自动打开 http://127.0.0.1:5000
```

#### Windows:
```
1. 打开文件夹 DiDi-POI-热点系统-Windows
2. 双击 启动.bat 或 DiDi_POI热点系统.exe
3. 浏览器自动打开
```

#### Linux:
```bash
cd DiDi-POI-热点系统-Linux-x64
chmod +x DiDi_POI热点系统
./DiDi_POI热点系统
```

---

## 三种部署方式

### 方式 1️⃣: 独立可执行文件（⭐⭐⭐ 推荐）

**优点:**
- ✅ 零配置，开箱即用
- ✅ 无需 Python 环境
- ✅ 启动快速
- ✅ 文件大小适中（~33MB）

**缺点:**
- ❌ 每个平台需要单独的可执行文件
- ❌ 不能直接修改代码

**文件清单:**
```
DiDi-POI-热点系统-[平台]/
├── DiDi_POI热点系统.exe      (Windows) 或
├── DiDi_POI热点系统           (macOS/Linux)
├── 启动.bat                   (Windows) 或
├── 启动.sh                    (macOS/Linux)
├── .env                       配置文件
└── README.txt                 说明文档
```

---

### 方式 2️⃣: Docker 容器

**优点:**
- ✅ 完全隔离，不污染系统
- ✅ 跨平台一致性强
- ✅ 易于扩展和管理
- ✅ 适合服务器部署

**缺点:**
- ❌ 需要 Docker 环境
- ❌ 文件较大（~500MB）
- ❌ 启动略慢

**使用方法:**

1. 安装 Docker: https://www.docker.com/products/docker-desktop

2. 在项目目录创建 `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt --no-cache-dir

ENV FLASK_APP=web_app.py
EXPOSE 5000

CMD ["python3", "web_app.py", "--host", "0.0.0.0"]
```

3. 构建镜像:
```bash
docker build -t didi-poi:v1 .
```

4. 运行容器:
```bash
docker run -p 5000:5000 \
  -v $(pwd)/.env:/.env \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  didi-poi:v1
```

5. 访问: http://localhost:5000

---

### 方式 3️⃣: 源代码部署

**优点:**
- ✅ 完全控制，可任意修改
- ✅ 文件最小（几 KB）
- ✅ 最灵活

**缺点:**
- ❌ 需要 Python 3.8+
- ❌ 需要手工安装依赖
- ❌ 配置较复杂

**步骤:**

```bash
# 1. 克隆项目
git clone <repo-url>
cd didi_poi

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 3. 安装依赖
pip3 install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key

# 5. 运行
python3 web_app.py --host 127.0.0.1 --port 5000
```

---

## 📁 文件说明

### 可执行文件版本
```
releases/
└── DiDi-POI-热点系统-[平台]/
    ├── DiDi_POI热点系统*          # 主程序
    ├── 启动.sh / 启动.bat         # 启动脚本
    ├── .env                       # API 配置
    └── README.txt                 # 使用说明
```

### 源代码版本
```
didi_poi/
├── web_app.py                  # Flask 主程序
├── run_app.py                  # PyInstaller 入口
├── build.spec                  # PyInstaller 配置
├── package.py                  # 打包脚本
├── build_all_platforms.py      # 跨平台构建
├── requirements.txt            # Python 依赖
├── templates/                  # 网页模板
│   └── index.html              # 三标签 Web UI
├── .env                        # 配置文件
└── data/                       # 数据目录
    └── traffic.db              # SQLite 数据库
```

---

## 🔑 首次配置

无论使用哪种方式，首次运行都需要配置 API Key:

### 步骤 1: 获取高德 API Key
1. 访问: https://lbs.amap.com/
2. 注册并登录
3. 创建新应用
4. 获取 Web 服务 API Key

### 步骤 2: 获取火山引擎 API Key
1. 访问: https://www.volcengine.com/
2. 注册并登录
3. 创建路况 API 应用
4. 获取 API Key

### 步骤 3: 在网页上配置
1. 打开 http://127.0.0.1:5000
2. 点击"⚙️ 设置"标签
3. 输入两个 API Key
4. 点击"💾 保存密钥"

---

## 🆘 常见问题

### Q1: 如何停止程序?
```bash
按 Ctrl+C
```

### Q2: macOS 显示"无法验证开发者"?
```bash
# 第一次运行时执行
sudo xattr -d com.apple.quarantine ./DiDi_POI热点系统
```

### Q3: 浏览器没有自动打开?
手动访问: http://127.0.0.1:5000

### Q4: Windows 防火墙提示?
在 Windows 防火墙中勾选"允许"

### Q5: 报错"地址已被使用"?
5000 端口被占用，解决方案：
```bash
# macOS/Linux 查看占用进程
lsof -i :5000
# 然后杀死进程
kill -9 <PID>

# Windows 查看占用进程
netstat -ano | findstr :5000
# 然后杀死进程
taskkill /PID <PID> /F
```

### Q6: 数据保存在哪里?
- 热力图数据: `data/traffic.db`
- POI 权重: `output/poi_heat_weights.json`
- 配置: `.env`
- 路线地图: `output/route_plan.html`

### Q7: 能否更改端口号?
可以，编辑启动命令：
```bash
python3 web_app.py --host 127.0.0.1 --port 8888
```

### Q8: 如何在远程机器上访问?
将 `127.0.0.1` 改为 `0.0.0.0`:
```bash
python3 web_app.py --host 0.0.0.0 --port 5000
# 然后用 http://你的IP:5000 访问
```

### Q9: Linux 权限不足?
```bash
chmod +x DiDi_POI热点系统
./DiDi_POI热点系统
```

### Q10: 需要多个实例运行?
使用不同的端口：
```bash
./DiDi_POI热点系统 --port 5000 &
./DiDi_POI热点系统 --port 5001 &
./DiDi_POI热点系统 --port 5002 &
```

---

## 📊 方式对比表

| 对比项 | 独立可执行 | Docker | 源代码 |
|------|---------|--------|--------|
| 易用性 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| 配置难度 | ⭐ | ⭐⭐ | ⭐⭐⭐ |
| 文件大小 | 中等 (~33MB) | 大 (~500MB) | 小 (几KB) |
| 启动速度 | 快 | 慢 | 快 |
| 跨平台 | ✅ 需分别构建 | ✅ 统一 | ✅ 统一 |
| 修改代码 | ❌ 不能 | ⚠️ 需重新构建 | ✅ 直接改 |
| 生产部署 | ✅ 推荐 | ✅ 推荐 | ⚠️ 可用 |

---

## 🔄 如何生成新的可执行文件

如果你修改了代码，想重新打包：

```bash
# 1. 安装 PyInstaller
pip3 install pyinstaller

# 2. 重新构建
python3 package.py

# 3. 可执行文件在 releases/ 文件夹
```

---

## 📞 技术支持

遇到问题时，首先查看：
1. 程序输出的错误信息
2. 浏览器控制台的错误（F12）
3. 本文的常见问题部分

---

## ✅ 部署检查清单

- [ ] 已获取高德和火山引擎 API Key
- [ ] 已配置 .env 文件
- [ ] 已测试在本机运行
- [ ] 已在目标机器上验证
- [ ] 防火墙已配置
- [ ] 数据备份已完成

---

**版本**: v1.0  
**最后更新**: 2026-05-06  
**支持平台**: macOS, Windows, Linux
