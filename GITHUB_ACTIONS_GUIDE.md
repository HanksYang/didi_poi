# GitHub Actions 在线打包使用指南

## 功能说明

这个 GitHub Actions 工作流会在以下条件触发：
1. **推送标签**（推荐）：`git tag v1.0.0 && git push origin v1.0.0`
2. **手动触发**：GitHub Actions 标签页 → "Run workflow"

工作流会自动在以下平台构建：
- **Windows** (x86_64) - 生成 `.exe` 版本
- **macOS** (ARM64) - 生成 macOS 版本
- **Linux** (x86_64) - 生成 Linux 版本

## 方式 1：通过标签发布（推荐）

### 步骤 1：提交并推送代码

```bash
git add .
git commit -m "Update build configuration"
git push origin main
```

### 步骤 2：创建并推送标签

```bash
# 创建标签（格式：v主版本.次版本.修订版）
git tag v1.0.0
git push origin v1.0.0
```

### 步骤 3：查看构建进度

1. 访问 GitHub 仓库
2. 点击 "Actions" 标签页
3. 选择 "Build Release Packages" 工作流
4. 查看对应标签的构建日志

### 步骤 4：下载发布版本

构建完成后，自动创建 Release 页面：
1. 仓库主页 → "Releases"
2. 找到对应版本（v1.0.0）
3. 下载对应平台的 zip 文件

## 方式 2：手动触发（用于测试）

### 步骤 1：进入 Actions 页面

1. GitHub 仓库 → Actions 标签页
2. 左侧选择 "Build Release Packages"
3. 点击 "Run workflow" 按钮

### 步骤 2：下载构建产物

工作流完成后：
1. 点击对应的工作流运行
2. "Artifacts" 部分下载对应平台的产物
3. 产物会保留 7 天

## 文件结构说明

构建完成后，releases 目录结构：

```
releases/
├── DiDi-POI-热点系统-Windows/
│   ├── DiDi_POI热点系统.exe
│   ├── 启动.bat
│   ├── .env
│   └── README.txt
├── DiDi-POI-热点系统-macOS-arm64/
│   ├── DiDi_POI热点系统
│   ├── .env
│   └── README.txt
└── DiDi-POI-热点系统-Linux-x86_64/
    ├── DiDi_POI热点系统
    ├── .env
    └── README.txt
```

## 版本命名规范

推荐使用语义化版本：
- `v1.0.0` - 初始版本（主版本.次版本.修订版）
- `v1.0.1` - 修复版本
- `v1.1.0` - 新功能版本
- `v2.0.0` - 重大更新版本

## 常见问题

**Q: 工作流失败了怎么办？**
- 检查工作流日志（Actions 页面查看具体错误）
- 常见原因：依赖安装失败、Python 版本问题
- 尝试重新运行工作流

**Q: 如何更新已发布的版本？**
- 删除现有标签：`git tag -d v1.0.0 && git push origin :refs/tags/v1.0.0`
- 重新创建标签：`git tag v1.0.0 && git push origin v1.0.0`
- 删除 Release 页面上的旧版本

**Q: 如何跳过 Linux/macOS 构建？**
- 编辑 `.github/workflows/build-release.yml`
- 在 `strategy.matrix.include` 中注释掉不需要的平台

**Q: 为什么 Windows 版本很大？**
- PyInstaller 会包含整个 Python 运行时环境
- 正常情况下 50-100MB 是预期的
- 可以配置 UPX 压缩进一步减小（需在 build.spec 中启用）

## 环境变量管理

如果需要在构建时使用敏感信息（API Key 等）：

1. GitHub 仓库设置 → "Secrets and variables" → "Actions"
2. 添加 Secret（如 `AMAP_API_KEY`）
3. 在工作流中使用：
   ```yaml
   env:
     AMAP_API_KEY: ${{ secrets.AMAP_API_KEY }}
   ```

## 工作流触发事件

当前工作流支持：
- **`push` with tags** - 推送带有 `v*` 标签的提交
- **`workflow_dispatch`** - 手动从 Actions 页面触发

可选的其他触发方式（修改 yml 文件）：
```yaml
on:
  schedule:
    - cron: '0 0 * * 0'  # 每周日自动构建
  pull_request:
    branches:
      - main
```

---

**首次使用步骤总结：**

```bash
# 1. 推送代码
git add .
git commit -m "Setup GitHub Actions"
git push origin main

# 2. 创建发布标签
git tag v1.0.0
git push origin v1.0.0

# 3. 等待 GitHub Actions 完成构建（约 5-10 分钟）

# 4. 在 GitHub Releases 页面下载打包文件
```

