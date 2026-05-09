# 🚀 DiDi 司机热点系统

智能热力图识别 + 路线规划系统，帮助滴滴司机了解接单热点分布和规划最优路线。

## ✨ 功能

### 📤 热力图上传
- 上传热力图图像（JPG/PNG/GIF）
- AI 自动识别地点和热度
- 更新 POI 接单热度权重
- 支持分时段数据存储

### 🗺️ 路线规划
- 输入起点和终点地点名称
- 系统自动规划 3 条最优路线
- 显示热度总和、距离、时长、接单评分
- 嵌入地图展示路线详情

### ⚙️ 设置
- 配置高德地图 API Key
- 配置火山引擎 API Key
- 密钥保存到本地 .env 文件

## 🔧 快速开始

### 1. 安装依赖
```bash
pip3 install -r requirements.txt --break-system-packages
```

### 2. 配置 API Key

在"⚙️ 设置"标签页中：
1. 点击"🔗 申请 Key"按钮前往申请页面
2. 获取高德地图 API Key：https://lbs.amap.com/api
3. 获取火山引擎 API Key：https://console.volcengine.com/ark
4. 粘贴到输入框并点击"💾 保存密钥"

### 3. 运行应用
```bash
python3 run_app.py
```

浏览器会自动打开 http://127.0.0.1:5000

## 📁 项目结构

```
didi_poi/
├── run_app.py                 # 启动脚本
├── requirements.txt           # 依赖列表
├── .env                       # 环境变量（本地）
├── .env.example              # 环境变量模板
│
├── web/
│   ├── web_app.py           # Flask 应用
│   ├── __init__.py
│   └── templates/
│       └── index.html        # 前端 UI
│
├── data/                      # 数据存储
│   └── traffic.db            # SQLite 数据库
│
└── output/                    # 输出文件
    ├── poi_heat_weights.json # POI 热度数据
    └── route_plan.html       # 路线规划地图
```

## 🔗 API 端点

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 获取主页 |
| POST | `/api/upload` | 上传热力图 |
| GET | `/api/pois` | 获取 POI 列表 |
| POST | `/api/route/plan` | 规划路线 |
| GET/POST | `/api/config` | 获取/保存配置 |
| GET | `/output/<file>` | 获取输出文件 |

## 💡 使用提示

- 首次使用必须先在"⚙️ 设置"中配置两个 API Key
- 热力图应该是高德地图的截图或类似格式
- 系统会自动识别图中的地点和热度中心
- POI 数据会自动更新到 `output/poi_heat_weights.json`
- 路线规划基于当前 POI 热度数据

## ⚠️ 常见问题

### 1. "缺少 API Key"
**解决**：在"⚙️ 设置"标签页配置高德地图和火山引擎 API Key

### 2. "地名识别失败"
**解决**：确认输入的地名有效，或使用 POI 列表中的地点

### 3. "浏览器未自动打开"
**解决**：手动访问 http://127.0.0.1:5000

### 4. "端口 5000 已被占用"
**解决**：关闭其他占用该端口的应用，或编辑 `run_app.py` 中的 `port` 值

## 📞 关于

DiDi POI 热点系统 v1.0
基于 Flask + 高德地图 API + 火山引擎 Vision API

---

**按 Ctrl+C 可以停止服务**
