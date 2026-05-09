# 设置 GitHub Actions 快速指南

## 第一步：初始化 Git 仓库并推送到 GitHub

```bash
# 进入项目目录
cd /Users/jingxifanyiguan/Desktop/didi_poi

# 初始化 git
git init
git add .
git commit -m "Initial commit: DiDi POI 热点地图生成系统"

# 添加远程仓库（替换 YOUR_USERNAME 和 YOUR_REPO）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

## 第二步：创建发布标签并触发打包

```bash
# 创建标签
git tag v1.0.0
git push origin v1.0.0
```

## 第三步：查看打包进度

1. 打开 GitHub 仓库链接
2. 点击 "Actions" 标签页
3. 查看 "Build Release Packages" 工作流的运行状态
4. 等待所有平台的构建完成（通常 10-15 分钟）

## 第四步：下载打包文件

构建完成后：
1. 进入仓库的 "Releases" 页面
2. 找到 `v1.0.0` 版本
3. 下载对应平台的 `.zip` 文件

## 什么是 GitHub Actions？

GitHub Actions 是 GitHub 提供的 CI/CD 服务，可以自动：
- 在推送代码时运行测试
- 在创建标签时自动打包
- 在多个平台上进行交叉编译
- 自动发布到 Releases 页面

## 工作流文件位置

工作流配置文件已生成在：
```
.github/workflows/build-release.yml
```

这个文件定义了：
- 何时触发：推送标签时自动运行
- 在哪里运行：Windows、macOS、Linux
- 运行什么：调用 `package.py` 进行打包

## 快速命令参考

```bash
# 初始化仓库
git init && git add . && git commit -m "Initial commit"

# 添加 GitHub 远程仓库
git remote add origin https://github.com/YOU/REPO.git

# 推送到 GitHub
git push -u origin main

# 创建发布版本
git tag v1.0.0
git push origin v1.0.0

# 查看标签
git tag -l

# 删除本地标签
git tag -d v1.0.0

# 删除远程标签
git push origin :refs/tags/v1.0.0
```

## 自动化优势

✅ **无需本地环境**
- 不用在本机安装 PyInstaller
- 不用安装多个 Python 版本

✅ **跨平台支持**
- 自动在 Windows、macOS、Linux 上构建
- 生成真正的平台特定可执行文件

✅ **自动化发布**
- 构建完成自动创建 Release
- 用户直接下载使用

✅ **版本管理**
- 每个版本独立发布
- 清晰的版本历史

## 下次更新流程

```bash
# 1. 修改代码
# ... 修改文件 ...

# 2. 提交修改
git add .
git commit -m "Fix: 修复 Windows 打包路径问题"
git push origin main

# 3. 发布新版本
git tag v1.0.1
git push origin v1.0.1

# 4. 在 GitHub Releases 页面下载
```

---

**需要帮助？**
- 如果工作流失败，查看 Actions 页面的错误日志
- 常见错误通常在依赖安装阶段显示
- 可以在工作流文件中添加调试步骤

