# Windows 打包问题修复说明

## 问题诊断

Windows 打包版本执行失败的主要原因：

1. **PyInstaller 资源路径问题**
   - 打包后，资源文件（templates、data 等）的相对路径会改变
   - Flask 找不到 templates 文件夹导致启动失败

2. **build.spec 配置不完整**
   - 缺少必要的数据文件目录
   - `web/web_app.py` 不应该在 datas 中（它是 Python 模块）

3. **模块导入问题**
   - 相对导入需要在打包后正确处理
   - `sys.path.insert()` 在打包环境中可能失效

## 修复内容

### 1. 更新 `build.spec`

**改进：**
- 正确配置 templates 目录映射：`('web/templates', 'web/templates')`
- 包含 `src`、`web`、`data`、`output` 完整目录
- 移除不必要的文件级别数据项

**新增 datas：**
```python
datas=[
    ('web/templates', 'web/templates'),
    ('src', 'src'),
    ('web', 'web'),
    ('data', 'data'),
    ('output', 'output'),
    ('.env', '.'),
    ('.env.example', '.'),
],
```

### 2. 更新 `run_app.py`

**改进：**
- 检测是否运行在 PyInstaller 打包环境中
- 正确设置 `sys._MEIPASS`（PyInstaller 的临时解包路径）
- 改变工作目录到正确的位置

**关键代码：**
```python
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
else:
    base_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_dir)
os.chdir(base_dir)
```

### 3. 更新 `web/web_app.py`

**改进：**
- Flask 的 `template_folder` 现在动态计算正确路径
- 在打包和开发环境中都能正确工作

**关键代码：**
```python
if getattr(sys, 'frozen', False):
    base_dir = sys._MEIPASS
    template_dir = os.path.join(base_dir, 'web', 'templates')
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_dir = os.path.join(base_dir, 'web', 'templates')

app = Flask(__name__, template_folder=template_dir)
```

### 4. 更新 `src/heatmap_uploader.py`

**改进：**
- 移除不必要的 `sys.path.insert()`
- 改为相对导入，让 Python 正确处理模块路径

**变化：**
```python
# 从：
from data_collector import _to_grid
import config
from llm_client import LLMClient

# 改为：
from .data_collector import _to_grid
from . import config
from .llm_client import LLMClient
```

### 5. 增强 `package.py`

**改进：**
- 添加 Windows 启动脚本生成逻辑
- 检测可执行文件是否存在
- 包含 `.env.example` 文件
- 为 Windows 创建 `启动.bat` 脚本

## 如何重新打包

```bash
# 清理旧的构建文件并重新打包
python3 package.py --clean

# 或者直接打包（使用缓存）
python3 package.py
```

打包完成后，在 `releases/DiDi-POI-热点系统-Windows/` 目录中会生成：
- `DiDi_POI热点系统.exe` - 可执行文件
- `启动.bat` - Windows 启动脚本
- `.env` - 环境变量配置文件
- `README.txt` - 使用说明

## 测试步骤

1. **在 Windows 系统上**，双击 `启动.bat` 或 `DiDi_POI热点系统.exe`
2. 浏览器应该自动打开 http://127.0.0.1:5000
3. 检查以下功能是否正常：
   - 热力图上传页面加载
   - 路线规划页面加载
   - 设置页面可以保存配置

## 常见问题排查

**Q: 仍然提示找不到 templates**
- 确保 build.spec 中配置了正确的 datas 路径
- 运行 `pyinstaller build.spec --clean --noconfirm` 进行完全重建

**Q: 模块导入错误**
- 检查 web_app.py 中的 template_folder 是否正确设置
- 查看控制台错误信息，记录具体的导入路径

**Q: .env 文件找不到**
- 将 `.env` 放在与可执行文件同一目录
- 或在 build.spec 中已经配置为打包数据

**Q: 浏览器未自动打开**
- 防火墙可能阻止了 5000 端口
- 手动访问 http://127.0.0.1:5000
- 检查控制台是否报告了绑定错误

## 性能优化建议

1. 如果打包文件过大（>100MB），考虑使用 UPX 压缩
2. 在 build.spec 中添加 `upx=True` 和 `upx_exclude=[]`
3. 使用 `--onefile` 选项打包成单个可执行文件（已在 spec 中使用）

---

修复日期：2026-05-09
