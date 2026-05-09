# 📁 DiDi POI 热点系统 - 项目结构说明

## 完整项目布局

```
didi_poi/
│
├── 📦 可执行文件版本
│   ├── run_app.py                      # PyInstaller 入口脚本
│   ├── build.spec                      # PyInstaller 打包配置
│   ├── package.py                      # 自动打包脚本
│   ├── build_all_platforms.py          # 跨平台构建脚本
│   ├── requirements.txt                # Python 依赖列表
│   │
│   └── releases/                       # 📤 分发包
│       ├── DiDi-POI-热点系统-macOS-arm64/
│       │   ├── DiDi_POI热点系统        # ⭐ macOS 可执行文件
│       │   ├── 启动.sh
│       │   ├── .env
│       │   └── README.txt
│       │
│       ├── DiDi-POI-热点系统-Windows/
│       │   ├── DiDi_POI热点系统.exe    # ⭐ Windows 可执行文件
│       │   ├── 启动.bat
│       │   ├── .env
│       │   └── README.txt
│       │
│       └── DiDi-POI-热点系统-Linux-x64/
│           ├── DiDi_POI热点系统        # ⭐ Linux 可执行文件
│           ├── 启动.sh
│           ├── .env
│           └── README.txt
│
├── 🌐 Web 应用
│   ├── web_app.py                      # Flask 主程序
│   ├── templates/
│   │   └── index.html                  # 三标签 Web UI
│   ├── static/                         # 静态资源（CSS/JS）
│   └── output/                         # 输出目录
│       ├── route_plan.html             # 路线规划地图
│       └── poi_heat_weights.json       # POI 权重数据
│
├── 🔄 核心模块
│   ├── route_planner.py                # 路线规划引擎
│   ├── traffic_provider.py             # 路况数据接口
│   ├── heatmap_uploader.py             # 热力图上传处理
│   ├── llm_client.py                   # LLM 调用客户端
│   ├── data_collector.py               # 数据采集（包含 _to_grid 函数）
│   ├── data_processor.py              # 数据处理
│   ├── heatmap_generator.py            # 热力图生成
│   ├── scheduler.py                    # 任务调度
│   ├── config.py                       # 配置管理
│   └── main.py                         # CLI 入口
│
├── 💾 数据文件
│   ├── .env                            # 环境变量配置
│   ├── .env.example                    # 环境模板
│   ├── data/
│   │   └── traffic.db                  # SQLite 数据库
│   └── output/
│       ├── *.html                      # 热力图/地图文件
│       ├── *.json                      # 数据导出
│       └── *.png                       # 图像文件
│
├── 📚 文档
│   ├── README.md                       # 项目概述
│   ├── QUICK_START.md                  # 快速开始指南
│   ├── DISTRIBUTION.md                 # 分发和部署指南
│   ├── DEPLOYMENT_GUIDE.md             # 部署指南
│   ├── DEPLOYMENT_GUIDE_FULL.md        # 完整部署文档
│   ├── README_PACKAGING.md             # 打包说明
│   ├── PROJECT_STRUCTURE.md            # 本文件
│   └── docs/                           # 其他文档
│
└── 🔧 构建文件
    ├── build/                          # PyInstaller 构建临时文件
    ├── dist/                           # PyInstaller 输出目录
    ├── Dockerfile                      # Docker 配置
    └── .github/
        └── workflows/
            └── build.yml               # GitHub Actions 自动化
```

---

## 文件用途详解

### 🎯 核心入口
| 文件 | 用途 | 使用者 |
|------|------|--------|
| `web_app.py` | Flask Web 应用主程序 | 开发者/最终用户 |
| `run_app.py` | PyInstaller 打包用入口 | 打包工具 |
| `main.py` | CLI 命令行工具 | 开发者 |

### 📦 打包相关
| 文件 | 用途 | 何时使用 |
|------|------|---------|
| `build.spec` | PyInstaller 配置 | 打包时 |
| `package.py` | 快速打包脚本 | 生成发布包 |
| `build_all_platforms.py` | 跨平台构建 | 多平台支持 |
| `requirements.txt` | 依赖列表 | 源代码部署 |

### 🌐 Web 模块
| 文件 | 功能 |
|------|------|
| `route_planner.py` | 路线规划算法 |
| `traffic_provider.py` | 高德/火山路况数据 |
| `heatmap_uploader.py` | 热力图识别处理 |
| `llm_client.py` | Claude/大模型调用 |

### 💾 数据处理
| 文件 | 功能 |
|------|------|
| `data_collector.py` | 从高德 API 采集数据 |
| `data_processor.py` | 数据聚合、归一化 |
| `heatmap_generator.py` | 生成热力图 HTML |

### ⚙️ 配置和调度
| 文件 | 内容 |
|------|------|
| `config.py` | 城市范围、时段、参数 |
| `scheduler.py` | 定时任务调度 |
| `.env` | API Key 和密钥 |

### 📄 文档
| 文件 | 目的 |
|------|------|
| `README.md` | 项目总体说明 |
| `QUICK_START.md` | 2分钟快速指南 |
| `DISTRIBUTION.md` | 详细分发部署 |
| `DEPLOYMENT_GUIDE.md` | 各种部署方式 |

---

## 三种部署方案对比

### 1️⃣ 独立可执行文件
```
✅ 推荐用于: 最终用户分发
📍 位置: releases/
💾 大小: ~33MB/个
🚀 运行: 直接双击
📋 包含: run_app.py, 所有依赖
```

### 2️⃣ Docker 容器
```
✅ 推荐用于: 云服务器部署
📍 位置: Dockerfile (待创建)
💾 大小: ~500MB
🚀 运行: docker run
📋 包含: 完整 Python 环境
```

### 3️⃣ 源代码
```
✅ 推荐用于: 开发和定制
📍 位置: didi_poi/ 根目录
💾 大小: 几 KB
🚀 运行: python3 web_app.py
📋 包含: 原始代码和配置
```

---

## 数据流向

```
用户输入 (Web UI)
    ↓
web_app.py (Flask 路由)
    ↓
├─ 热力图上传 → heatmap_uploader.py → llm_client.py → data_processor.py
├─ 路线规划 → route_planner.py → traffic_provider.py → 地图生成
└─ API 配置 → .env 文件
    ↓
数据存储 (SQLite/JSON)
    ↓
输出展示 (HTML/地图)
```

---

## 构建流程

```
源代码
    ↓
pip3 install -r requirements.txt (依赖)
    ↓
pyinstaller build.spec (打包)
    ↓
dist/ (输出可执行文件)
    ↓
releases/ (打包分发)
    ↓
DiDi-POI-热点系统-[平台].zip (压缩包)
    ↓
📤 分发给用户
```

---

## 关键配置

### config.py
```python
CITY = "beijing"              # 目标城市
GRID_RESOLUTION = 0.01        # 网格分辨率 (约1km)
QUERY_CHUNK_LNG = 0.07        # 查询块大小
QUERY_CHUNK_LAT = 0.05
TIME_PERIODS = {              # 时段定义
    "morning": (7, 9),
    "day": (10, 16),
    "evening": (17, 20)
}
```

### .env
```
AMAP_API_KEY=your_key         # 高德地图
VOLC_API_KEY=your_key         # 火山引擎
TRAFFIC_PROVIDER=volcano      # 数据源
CITY=beijing                  # 城市
```

---

## 依赖说明

### Web 框架
- Flask: Web 服务器
- Werkzeug: WSGI 工具库

### 数据处理
- pandas: 数据分析
- numpy: 数值计算
- Pillow: 图像处理

### 地图
- folium: 地图库
- branca: HTML 组件

### API
- requests: HTTP 请求
- anthropic: Claude API

---

## 更新流程

修改代码 → 测试 → 重新打包

```bash
# 1. 修改代码
vim route_planner.py

# 2. 本地测试
python3 web_app.py

# 3. 重新打包
python3 package.py --clean

# 4. 新的分发包在 releases/
```

---

## 故障排除

### 打包失败
```bash
# 清理旧文件
rm -rf build dist

# 重新打包
python3 package.py
```

### 运行错误
```bash
# 检查 Python 版本
python3 --version  # 需要 3.8+

# 检查依赖
pip3 list | grep -E "Flask|folium"
```

### 端口被占用
```bash
# macOS/Linux
lsof -i :5000
kill -9 PID

# Windows
netstat -ano | findstr :5000
taskkill /PID PID /F
```

---

**最后更新**: 2026-05-06  
**项目版本**: v1.0  
**维护者**: DiDi POI Team
