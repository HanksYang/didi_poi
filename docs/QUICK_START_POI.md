# POI 热度权重生成 - 快速开始

## ⚡ 5分钟快速开始

### 第1步: 获取 API Key (1分钟)

1. 访问 https://console.anthropic.com/
2. 点击 "Create API Key"
3. 复制生成的 API Key（以 `sk-ant-` 开头）

### 第2步: 配置环境 (1分钟)

```bash
cd /Users/jingxifanyiguan/Desktop/didi_poi

# 复制配置文件
cp .env.example .env

# 编辑 .env 文件，粘贴 API Key
# 将这行：
#   ANTHROPIC_API_KEY=your_anthropic_api_key_here
# 改为：
#   ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxx
```

### 第3步: 安装依赖 (2分钟)

```bash
pip3 install anthropic pillow python-dotenv numpy --break-system-packages
```

### 第4步: 运行分析 (1分钟)

```bash
python3 poi_heat_analyzer.py --image /Users/jingxifanyiguan/Desktop/36dbc7a39a26839c4284a92fcdec5420.jpg
```

### 第5步: 查看结果

生成的文件位置：
- **JSON**: `output/poi_heat_weights.json`
- **CSV**: `output/poi_heat_weights.csv`

在 Excel 中打开 CSV 查看 top100 POI：

```bash
open output/poi_heat_weights.csv
```

---

## 🎯 脚本工作原理

```
输入: 热力图图片 (红色区域表示高热度)
  ↓
[1] 图像特征提取 (PIL/numpy)
    - 分析红色像素分布
    - 计算热度强度均值、最大值、覆盖比例
  ↓
[2] Claude Vision 分析
    - 理解热力图中的地理信息
    - 识别热度最高的区域
    - 基于北京地理知识生成 POI 列表
  ↓
[3] 热度权重计算
    - 为每个 POI 计算热度分数 (0-1)
    - 按热度从高到低排序
  ↓
输出: JSON + CSV (100 个 POI 及其热度权重)
```

---

## 📊 输出数据格式

### JSON 示例

```json
{
  "poi_list": [
    {
      "rank": 1,
      "name": "国贸中心",
      "district": "朝阳区",
      "category": "商务区",
      "lng": 116.461,
      "lat": 39.904,
      "heat_score": 0.95
    }
  ]
}
```

### CSV 示例

| rank | name | district | category | lng | lat | heat_score |
|------|------|----------|----------|-----|-----|------------|
| 1 | 国贸中心 | 朝阳区 | 商务区 | 116.461 | 39.904 | 0.95 |

---

## 🔧 配置参数

脚本命令行参数：

```bash
python3 poi_heat_analyzer.py \
  --image /path/to/heatmap.jpg \           # 热力图路径 (必需)
  --output ./my_output                    # 输出目录 (可选，默认: output)
```

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|--------|
| `ModuleNotFoundError: No module named 'anthropic'` | 运行 `pip3 install anthropic --break-system-packages` |
| `ANTHROPIC_API_KEY not found in .env` | 检查 `.env` 文件是否包含正确的 API Key |
| 输出 JSON 为空 | 检查热力图图像是否清晰，是否有明显的红色热度区域 |
| API 超时 | 稍等后重试，或检查网络连接 |

---

## 💡 进阶用法

### 与滴滴系统集成

将 POI 热度权重导入到现有的 heatmap_generator.py：

```python
import json
import pandas as pd

# 读取 POI 热度数据
with open('output/poi_heat_weights.json') as f:
    poi_data = json.load(f)

# 转换为 DataFrame
df_poi = pd.DataFrame(poi_data['poi_list'])

# 与网格热度数据合并
df_combined = pd.merge(
    df_existing_grid_data,
    df_poi[['lng', 'lat', 'heat_score']],
    on=['lng', 'lat'],
    how='outer'
)
```

### 批量处理多个城市

虽然当前脚本针对北京，但可以通过修改 Claude prompt 来支持其他城市。在 `poi_heat_analyzer.py` 中修改：

```python
system_prompt = """你是[城市名]城市地理专家...
"""
```

---

## 📞 支持

- 脚本问题: 检查 `README_POI_ANALYZER.md`
- Claude API 问题: https://support.anthropic.com
- 高德地图问题: https://lbs.amap.com/api

---

## 下一步

✅ 脚本已创建，可以开始使用  
✅ 获得 API Key 并配置  
✅ 运行脚本生成 POI 热度权重  
✅ 在 Excel 中分析结果  
✅ (可选) 集成到现有滴滴系统
