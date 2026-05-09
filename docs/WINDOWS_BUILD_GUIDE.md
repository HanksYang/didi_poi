# 🪟 DiDi POI 热点系统 - Windows 版本生成指南

## 📋 前置要求

### 检查 Windows 版本
- Windows 7 或更高版本
- 建议使用 Windows 10/11

### 检查 Python 环境

1. **打开命令提示符** (Win + R，输入 `cmd`)

2. **检查 Python 是否已安装**
```cmd
python --version
python3 --version
```

**如果显示版本号** (如 `Python 3.11.0`)，说明已安装，跳到下一步

**如果显示"命令不存在"**，需要安装 Python：
- 访问 https://www.python.org/downloads/
- 下载 Python 3.11+ 版本
- **⚠️ 重要：安装时勾选 "Add Python to PATH"**
- 完成后重启命令提示符

---

## 🚀 生成 Windows 可执行文件

### 步骤 1：准备项目文件

将整个 `didi_poi` 文件夹复制到 Windows 机器上

项目结构应该包含：
```
didi_poi/
├── web_app.py
├── run_app.py
├── build.spec
├── package.py
├── requirements.txt
├── templates/
├── .env
└── ... 其他文件
```

### 步骤 2：打开命令提示符

```
Win + R → 输入 cmd → 回车
```

### 步骤 3：进入项目目录

```cmd
cd C:\Users\你的用户名\Desktop\didi_poi
```

或者如果在其他位置：
```cmd
cd D:\项目\didi_poi
```

### 步骤 4：安装依赖

```cmd
pip install -r requirements.txt
```

**等待安装完成**（可能需要 5-10 分钟）

### 步骤 5：安装 PyInstaller

```cmd
pip install pyinstaller
```

### 步骤 6：生成可执行文件

```cmd
python package.py
```

**或者直接使用 PyInstaller：**
```cmd
pyinstaller build.spec --noconfirm
```

### 步骤 7：等待打包完成

输出应该类似：
```
...
✅ PyInstaller 构建成功!
📦 创建发布包...
✓ 发布包已创建: releases/DiDi-POI-热点系统-Windows
✅ 打包完成!
```

---

## 📦 打包完成后

### 生成的文件位置

```
releases/
└── DiDi-POI-热点系统-Windows/
    ├── DiDi_POI热点系统.exe      ⭐ 主程序
    ├── 启动.bat                  ⭐ 启动脚本
    ├── .env                      配置文件
    └── README.txt                使用说明
```

### 运行程序

**最简单的方法：直接双击**
```
双击 启动.bat 文件
```

**或者直接运行：**
```
双击 DiDi_POI热点系统.exe 文件
```

**或者命令行运行：**
```cmd
DiDi_POI热点系统.exe
```

---

## 🔧 常见问题

### Q1: 提示"找不到 Python"

**原因**：Python 未添加到 PATH

**解决方案**：
1. 重新安装 Python
2. 安装时务必勾选 "Add Python to PATH"
3. 安装后重启计算机

### Q2: pip 命令不存在

**原因**：同上

**解决方案**：
```cmd
# 使用完整路径
C:\Python311\Scripts\pip install -r requirements.txt
```

### Q3: 依赖安装失败

**错误信息**：`error: Microsoft Visual C++ 14.0 or greater is required`

**解决方案**：
1. 下载 Visual C++ Build Tools：https://visualstudio.microsoft.com/downloads/
2. 选择 "Desktop development with C++" 安装
3. 重试 `pip install -r requirements.txt`

### Q4: 打包速度很慢

**这是正常的**，第一次打包可能需要 10-20 分钟

**可以加速参数**：
```cmd
pyinstaller build.spec --noconfirm -y
```

### Q5: 生成的 .exe 文件很大

**这是正常的**，包含了所有 Python 依赖，约 33-50MB

---

## 📤 分发给他人

### 方式 1：直接分享文件夹

```
压缩 releases/DiDi-POI-热点系统-Windows/ 文件夹

发送给他人

他人解压后双击 启动.bat 即可运行
```

### 方式 2：创建 ZIP 压缩包

在命令提示符中：
```cmd
# Windows 10/11 内置压缩功能
# 右键点击文件夹 → 发送到 → 压缩文件夹

# 或使用 PowerShell
Compress-Archive -Path releases/DiDi-POI-热点系统-Windows -DestinationPath DiDi-POI-热点系统-Windows.zip
```

---

## 🎯 验证打包是否成功

### 检查 1：可执行文件存在

```cmd
cd releases\DiDi-POI-热点系统-Windows
dir
```

应该看到：
```
DiDi_POI热点系统.exe
启动.bat
.env
README.txt
```

### 检查 2：运行程序

```cmd
DiDi_POI热点系统.exe
```

应该显示：
```
🌐 Web 服务启动
   地址: http://127.0.0.1:5000
   模式: PRODUCTION
   打开浏览器访问上面的地址
```

### 检查 3：浏览器自动打开

http://127.0.0.1:5000 应该自动在浏览器中打开

---

## 🔐 防火墙提示

如果 Windows 防火墙提示：

```
Windows 已阻止某些功能
```

**点击"允许访问"** 即可

---

## 🚀 快速参考

```cmd
# 1. 进入项目目录
cd 你的项目路径

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 PyInstaller
pip install pyinstaller

# 4. 生成可执行文件
python package.py

# 5. 运行程序
releases\DiDi-POI-热点系统-Windows\启动.bat
```

---

## 📋 Windows 打包检查清单

- [ ] Python 已安装并添加到 PATH
- [ ] 命令提示符能识别 `python` 和 `pip`
- [ ] 进入了项目目录
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] PyInstaller 已安装 (`pip install pyinstaller`)
- [ ] 运行了打包脚本 (`python package.py`)
- [ ] 等待打包完成（10-20 分钟）
- [ ] 生成的文件在 `releases/` 目录
- [ ] 成功运行了 `DiDi_POI热点系统.exe`
- [ ] 浏览器自动打开 http://127.0.0.1:5000

---

## 💡 高级技巧

### 隐藏命令窗口

如果不想看到黑色命令窗口，创建一个 `.vbs` 文件：

```vbs
' 文件名: 启动_隐藏.vbs
Set objShell = CreateObject("WScript.Shell")
objShell.Run "DiDi_POI热点系统.exe", 0, False
```

双击 `启动_隐藏.vbs` 即可隐藏窗口运行

### 创建快捷方式

在 Windows 中创建快捷方式：
1. 右键点击 `DiDi_POI热点系统.exe`
2. 创建快捷方式
3. 可以放在桌面上双击运行

### 更改图标

使用第三方工具（如 Resource Hacker）可以更改 .exe 的图标

---

## 🆘 需要帮助？

### 检查日志

如果程序启动失败，查看命令提示符的错误信息

### 常见错误信息

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `ModuleNotFoundError` | 依赖未安装 | 运行 `pip install -r requirements.txt` |
| `Address already in use` | 端口被占用 | 关闭占用 5000 端口的程序 |
| `No such file` | 文件找不到 | 检查工作目录和文件路径 |

---

## 📞 技术支持

如果遇到问题：

1. **查看本指南**的常见问题部分
2. **检查错误信息**，通常能看出问题原因
3. **确保**已按步骤完成所有操作
4. **尝试重新安装** Python 和依赖

---

**Windows 版本支持**: ✅ 完全支持  
**最小系统要求**: Windows 7 SP1+  
**推荐**: Windows 10/11  
**所需磁盘空间**: 200MB+ (包括 Python 环境)
