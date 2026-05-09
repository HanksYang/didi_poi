# 🚀 快速启动指南

## 一键启动

```bash
cd ~/didi_poi
python3 run_app.py
```

**结果：** 
- ✅ Flask 服务启动
- ✅ 浏览器自动打开 http://127.0.0.1:5000
- 🎨 看到三个标签页：📤 热力图上传 | 🗺️ 路线规划 | ⚙️ 设置

---

## 第一步：配置 API Key

1. 点击右上角的 **⚙️ 设置** 标签页
2. 第一个输入框：高德地图 API Key
   - 点击 **🔗 申请 Key** 按钮
   - 或访问 https://lbs.amap.com/api
   - 申请后粘贴 Key 到输入框

3. 第二个输入框：火山引擎 API Key
   - 点击 **🔗 申请 Key** 按钮
   - 或访问 https://console.volcengine.com/ark
   - 申请后粘贴 Key 到输入框

4. 点击 **💾 保存密钥** 按钮

---

## 第二步：使用功能

### 📤 热力图上传（第 1 个标签）
- 拖拽或点击上传热力图图像
- 选择时段（自动推断/早高峰/白天/晚高峰）
- 点击 **🚀 提交识别**
- 系统自动识别地点和热度

### 🗺️ 路线规划（第 2 个标签）
- 输入起点地点名称（支持自动完成）
- 输入终点地点名称（支持自动完成）
- 选择城市
- 点击 **🧭 规划路线**
- 查看 3 条最优路线和地图

### ⚙️ 设置（第 3 个标签）
- 配置或修改 API Key
- 点击链接直接前往申请页面

---

## 📁 项目文件

```
~/didi_poi/
├── run_app.py              ← 启动脚本（运行这个）
├── web/
│   ├── web_app.py         ← Flask 后端
│   └── templates/
│       └── index.html     ← Web 前端 UI
├── output/
│   └── poi_heat_weights.json  ← POI 数据
├── .env                   ← 本地配置（自动生成）
├── requirements.txt       ← 依赖列表
└── README.md             ← 完整文档
```

---

## 💡 常用命令

```bash
# 安装依赖
pip3 install -r requirements.txt --break-system-packages

# 启动应用
python3 run_app.py

# 停止应用
Ctrl + C

# 查看项目结构
ls -la
```

---

## ⚠️ 故障排除

| 问题 | 解决方案 |
|------|--------|
| 浏览器未自动打开 | 手动访问 http://127.0.0.1:5000 |
| 端口 5000 已占用 | 编辑 `run_app.py`，改变 `port` 值 |
| "缺少 API Key" | 在⚙️设置中配置两个 Key 并保存 |
| 文件找不到 | 确保在 `~/didi_poi` 目录中运行 |

---

就这么简单！🎉
