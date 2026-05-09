# 🐧 DiDi POI 热点系统 - Linux 版本生成指南

## 📋 前置要求

### 检查系统

```bash
uname -a
```

支持的 Linux 发行版：
- Ubuntu 18.04+
- Debian 10+
- CentOS 7+
- Fedora 32+
- Arch Linux
- 其他 glibc 2.17+ 的发行版

### 检查 Python

```bash
python3 --version
```

需要 Python 3.8+

**如果未安装，根据你的发行版安装：**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-dev
```

**CentOS/Fedora:**
```bash
sudo yum install python3 python3-pip python3-devel
```

**Arch:**
```bash
sudo pacman -S python python-pip
```

---

## 🚀 生成 Linux 可执行文件

### 步骤 1：准备项目文件

将整个 `didi_poi` 文件夹复制到 Linux 机器上

```bash
# 如果从 macOS/Windows 上复制
scp -r didi_poi user@linux-host:/home/user/

# 或直接 git clone
git clone <repo-url>
cd didi_poi
```

### 步骤 2：进入项目目录

```bash
cd ~/didi_poi
# 或你复制到的位置
```

### 步骤 3：创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate
```

### 步骤 4：升级 pip

```bash
pip install --upgrade pip
```

### 步骤 5：安装依赖

```bash
pip install -r requirements.txt
```

**等待完成**（可能需要 5-10 分钟）

### 步骤 6：安装 PyInstaller

```bash
pip install pyinstaller
```

### 步骤 7：生成可执行文件

```bash
python3 package.py
```

**或者直接使用 PyInstaller：**
```bash
pyinstaller build.spec --noconfirm
```

### 步骤 8：等待打包完成

输出应该类似：
```
✅ PyInstaller 构建成功!
📦 创建发布包...
✓ 发布包已创建: releases/DiDi-POI-热点系统-Linux-x64
✅ 打包完成!
```

---

## 📦 打包完成后

### 生成的文件位置

```
releases/
└── DiDi-POI-热点系统-Linux-x64/
    ├── DiDi_POI热点系统         ⭐ 主程序
    ├── 启动.sh                  ⭐ 启动脚本
    ├── .env                     配置文件
    └── README.txt               使用说明
```

### 运行程序

**设置可执行权限**
```bash
chmod +x releases/DiDi-POI-热点系统-Linux-x64/DiDi_POI热点系统
chmod +x releases/DiDi-POI-热点系统-Linux-x64/启动.sh
```

**运行方式 1：使用启动脚本（推荐）**
```bash
cd releases/DiDi-POI-热点系统-Linux-x64
./启动.sh
```

**运行方式 2：直接运行可执行文件**
```bash
./releases/DiDi-POI-热点系统-Linux-x64/DiDi_POI热点系统
```

**运行方式 3：后台运行**
```bash
nohup ./启动.sh > /tmp/didi.log 2>&1 &
```

---

## 🔧 常见问题

### Q1: 提示"command not found"

**原因**：Python 或 pip 未安装

**解决方案**：参考上面的"前置要求"安装

### Q2: 权限不足错误

**错误信息**：`Permission denied`

**解决方案**：
```bash
chmod +x DiDi_POI热点系统
chmod +x 启动.sh
```

### Q3: 依赖安装失败

**错误信息**：`error: command 'gcc' not found`

**原因**：缺少编译工具

**解决方案**：

Ubuntu/Debian:
```bash
sudo apt install build-essential python3-dev
```

CentOS/Fedora:
```bash
sudo yum groupinstall "Development Tools"
```

### Q4: PyInstaller 错误

**错误**：`ModuleNotFoundError`

**解决方案**：
```bash
# 确保在虚拟环境中
source venv/bin/activate

# 重新安装依赖
pip install -r requirements.txt

# 重试打包
python3 package.py
```

### Q5: 库文件缺失错误

**错误**：`libGL.so.1: cannot open shared object file`

**解决方案**（Ubuntu/Debian）：
```bash
sudo apt install libgl1-mesa-glx libxkbcommon-x11-0
```

### Q6: 打包后无法运行

**原因**：可能是架构不匹配

**解决方案**：
```bash
# 检查生成的可执行文件
file DiDi_POI热点系统

# 检查系统架构
uname -m
```

两者应该匹配（都是 x86_64 或都是 aarch64）

---

## 🌐 在服务器上运行

### 后台运行

```bash
nohup ./DiDi_POI热点系统 > /tmp/didi.log 2>&1 &
```

### 使用 systemd 自动启动（可选）

创建 `/etc/systemd/system/didi-poi.service`:

```ini
[Unit]
Description=DiDi POI 热点系统
After=network.target

[Service]
Type=simple
User=你的用户名
WorkingDirectory=/home/你的用户名/didi_poi/releases/DiDi-POI-热点系统-Linux-x64
ExecStart=/home/你的用户名/didi_poi/releases/DiDi-POI-热点系统-Linux-x64/DiDi_POI热点系统
Restart=always

[Install]
WantedBy=multi-user.target
```

启用服务：
```bash
sudo systemctl enable didi-poi
sudo systemctl start didi-poi
sudo systemctl status didi-poi
```

### 查看日志

```bash
tail -f /tmp/didi.log
```

### 停止运行

```bash
# 查找进程
ps aux | grep DiDi_POI

# 杀死进程
kill <PID>

# 或使用 systemctl
sudo systemctl stop didi-poi
```

---

## 📤 分发给他人

### 方式 1：直接分享文件夹

```bash
# 压缩
tar -czf DiDi-POI-热点系统-Linux.tar.gz releases/DiDi-POI-热点系统-Linux-x64/

# 分享给他人
# 他人接收后解压
tar -xzf DiDi-POI-热点系统-Linux.tar.gz
cd DiDi-POI-热点系统-Linux-x64
chmod +x 启动.sh
./启动.sh
```

### 方式 2：通过 SCP 传输

```bash
scp -r releases/DiDi-POI-热点系统-Linux-x64/ user@remote-host:/home/user/
```

---

## 🎯 验证打包是否成功

### 检查 1：可执行文件存在

```bash
ls -lh releases/DiDi-POI-热点系统-Linux-x64/
```

应该看到：
```
-rwxr-xr-x DiDi_POI热点系统
-rwxr-xr-x 启动.sh
-rw-r--r-- .env
-rw-r--r-- README.txt
```

### 检查 2：可执行文件架构

```bash
file releases/DiDi-POI-热点系统-Linux-x64/DiDi_POI热点系统
```

应该显示：
```
ELF 64-bit LSB executable, x86-64, ...
```

### 检查 3：运行程序

```bash
./releases/DiDi-POI-热点系统-Linux-x64/启动.sh
```

应该显示：
```
🚀 DiDi 司机热点系统启动中...
📍 服务地址: http://127.0.0.1:5000
```

### 检查 4：浏览器访问

在浏览器中访问 http://127.0.0.1:5000

---

## 🚀 快速参考

```bash
# 1. 进入项目目录
cd ~/didi_poi

# 2. 创建虚拟环境（可选但推荐）
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 生成可执行文件
python3 package.py

# 5. 给予执行权限
chmod +x releases/DiDi-POI-热点系统-Linux-x64/{DiDi_POI热点系统,启动.sh}

# 6. 运行程序
./releases/DiDi-POI-热点系统-Linux-x64/启动.sh
```

---

## 📋 Linux 打包检查清单

- [ ] Python 3.8+ 已安装
- [ ] pip 已安装
- [ ] 进入了项目目录
- [ ] 创建了虚拟环境（可选）
- [ ] 虚拟环境已激活
- [ ] 依赖已安装 (`pip install -r requirements.txt`)
- [ ] PyInstaller 已安装 (`pip install pyinstaller`)
- [ ] 运行了打包脚本 (`python3 package.py`)
- [ ] 等待打包完成（10-20 分钟）
- [ ] 生成的文件在 `releases/` 目录
- [ ] 文件有可执行权限
- [ ] 成功运行了 `启动.sh`
- [ ] 浏览器能访问 http://127.0.0.1:5000

---

## 💡 性能优化

### 使用 tmpfs 加速构建（可选）

```bash
# 在 RAM 中创建临时目录加速打包
mkdir /mnt/ramdisk
sudo mount -t tmpfs -o size=2G tmpfs /mnt/ramdisk

# 在 ramdisk 中打包
cd /mnt/ramdisk
pyinstaller /path/to/build.spec --noconfirm
```

### 多核并行打包

PyInstaller 在 Linux 上自动使用多核，无需额外配置

---

## 🔐 安全建议

### 保护 API Key

```bash
# 限制 .env 文件权限
chmod 600 releases/DiDi-POI-热点系统-Linux-x64/.env
```

### 非 root 运行

```bash
# 创建专用用户
sudo useradd -m didi-poi

# 将文件所有权更改为该用户
sudo chown -R didi-poi:didi-poi ~/didi_poi

# 以该用户身份运行
sudo -u didi-poi ~/didi_poi/releases/DiDi-POI-热点系统-Linux-x64/启动.sh
```

---

## 🆘 需要帮助？

### 检查系统信息

```bash
# 系统信息
uname -a

# Python 版本
python3 --version

# 已安装包
pip list | grep -E "Flask|folium|pyinstaller"

# 磁盘空间
df -h

# 内存使用
free -h
```

### 查看详细错误

```bash
# 运行时显示详细错误
python3 package.py -vvv
```

---

## 📞 Linux 特定问题

### 网络不稳定时安装依赖

```bash
pip install -r requirements.txt --retries 5
```

### 离线安装（如果网络不可用）

```bash
# 在有网络的机器上下载
pip download -r requirements.txt -d ./packages

# 在目标机器上离线安装
pip install --no-index --find-links ./packages -r requirements.txt
```

### 使用 conda 环替代 pip（可选）

```bash
conda create -n didi-poi python=3.11
conda activate didi-poi
pip install -r requirements.txt
```

---

**Linux 版本支持**: ✅ 完全支持  
**最小系统要求**: glibc 2.17+, Python 3.8+  
**推荐发行版**: Ubuntu 18.04+, Debian 10+  
**所需磁盘空间**: 200MB+ (包括构建文件)
