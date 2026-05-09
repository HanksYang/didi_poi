# ⚡ DiDi POI 热点系统 - 快速开始

## 🎯 2分钟快速上手

### 第一步：找到可执行文件
位置: `releases/DiDi-POI-热点系统-macOS-arm64/`

### 第二步：运行程序
**macOS:**
```bash
cd DiDi-POI-热点系统-macOS-arm64
chmod +x 启动.sh
./启动.sh
```

**Windows:** 
双击 `启动.bat`

**Linux:**
```bash
cd DiDi-POI-热点系统-Linux-x64
chmod +x 启动.sh
./启动.sh
```

### 第三步：配置 API
1. 浏览器自动打开 http://127.0.0.1:5000
2. 点击"⚙️ 设置"标签
3. 输入高德 API Key 和火山引擎 API Key
4. 点击"💾 保存密钥"

### 第四步：开始使用
✅ 完成！现在可以：
- 上传热力图
- 规划路线
- 查看数据

---

## 三个标签页功能速览

### 🔥 热力图上传
1. 拖拽或点击选择热力图
2. 设置参数（周期、sigma）
3. 点击上传
4. 查看识别结果

### 🛣️ 路线规划
1. 输入起点（如"三里屯"）
2. 输入终点（如"国贸"）
3. 选择城市
4. 点击"📍 规划路线"
5. 查看3条路线和地图

### ⚙️ 设置
1. 配置高德 API Key
2. 配置火山引擎 API Key
3. 点击保存
4. 完成！

---

## 🆘 卡住了？

| 问题 | 解决方案 |
|------|---------|
| 浏览器没打开 | 手动访问 http://127.0.0.1:5000 |
| 无法连接 | 检查 5000 端口是否被占用 |
| macOS 提示"无法验证" | 运行 `sudo xattr -d com.apple.quarantine DiDi_POI热点系统` |
| Windows 防火墙提示 | 点击"允许" |
| API Key 不知道从哪获取 | 查看DISTRIBUTION.md |

---

## 📞 获取 API Key

**高德地图:**
1. https://lbs.amap.com/
2. 注册 → 创建应用 → 获取 Key

**火山引擎:**
1. https://www.volcengine.com/
2. 注册 → 创建路况应用 → 获取 Key

---

## ✅ 就是这样！

现在可以享受使用了！

有问题？查看 `DISTRIBUTION.md` 获取完整文档。
