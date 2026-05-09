# POI 热度权重生成器使用指南

## 功能说明

`poi_heat_analyzer.py` 是一个基于 Claude Vision API 的热力图分析工具，可以：

1. **分析热力图图像** - 提取红色热度区域的分布特征
2. **调用 Claude API** - 使用 Vision 能力识别热力图中的地理位置和热度强度
3. **生成 POI 列表** - 基于热力图热度分布，为北京 top100 POI 生成热度权重分数
4. **输出结构化数据** - 保存为 JSON 和 CSV 格式

## 前提条件

### 1. 获取 Anthropic API Key

- 访问 https://console.anthropic.com/
- 创建 API Key 并复制

### 2. 配置环境

```bash
cd /Users/jingxifanyiguan/Desktop/didi_poi

# 复制配置模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxx
```

### 3. 安装依赖

```bash
pip3 install anthropic pillow python-dotenv numpy --break-system-packages
```

## 使用方法

### 基础用法

```bash
python3 poi_heat_analyzer.py --image /path/to/heatmap.jpg
```

### 指定输出目录

```bash
python3 poi_heat_analyzer.py --image /path/to/heatmap.jpg --output ./my_output
```

## 输出文件

脚本会在 `output/` 目录（或指定目录）生成：

### 1. `poi_heat_weights.json`

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
    },
    ...
  ]
}
```

### 2. `poi_heat_weights.csv`

| rank | name | district | category | lng | lat | heat_score |
|------|------|----------|----------|-----|-----|------------|
| 1 | 国贸中心 | 朝阳区 | 商务区 | 116.461 | 39.904 | 0.95 |
| 2 | 三里屯 | 朝阳区 | 商业街 | 116.443 | 39.906 | 0.92 |
| ... | ... | ... | ... | ... | ... | ... |

## 工作流程

### 步骤 1: 图像分析
- 使用 PIL/numpy 提取图像的红色通道
- 计算热度强度分布（均值、最大值、热点覆盖比例）

### 步骤 2: Claude Vision API 调用
- 将图像以 base64 编码方式传送给 Claude
- Claude 分析热力图识别地理区域和热度分布
- Claude 根据热度强度为每个 POI 生成热度分数（0-1）

### 步骤 3: 数据整合
- 将 Claude 返回的 POI 列表按热度排序
- 导出为 JSON 和 CSV 格式
- 生成统计摘要

## 示例运行

```bash
$ python3 poi_heat_analyzer.py --image /Users/jingxifanyiguan/Desktop/36dbc7a39a26839c4284a92fcdec5420.jpg

📊 开始分析热力图: /Users/jingxifanyiguan/Desktop/36dbc7a39a26839c4284a92fcdec5420.jpg
🔍 正在提取热力图特征...
   热度强度均值: 128.5
   热度最大值: 255.0
   热点覆盖比例: 35.2%
🤖 调用 Claude Vision API 分析...
✓ 成功识别 100 个 POI

📍 Top 10 热度 POI:
================================================================================
  1. 国贸中心           | 朝阳区      | 商务区       | 热度:0.95
  2. 三里屯            | 朝阳区      | 商业街       | 热度:0.92
  3. 中关村大街        | 海淀区      | 商业街       | 热度:0.90
  4. 金融街            | 西城区      | 商务区       | 热度:0.88
  5. 王府井街          | 东城区      | 商业街       | 热度:0.87
  6. CBD东扩          | 朝阳区      | 商务区       | 热度:0.86
  7. 西单广场          | 西城区      | 商业街       | 热度:0.85
  8. 五道口            | 海淀区      | 商业街       | 热度:0.84
  9. 北京站            | 东城区      | 交通枢纽     | 热度:0.83
 10. 大兴机场          | 大兴区      | 交通枢纽     | 热度:0.81

✅ 分析完成！
   JSON: output/poi_heat_weights.json
   CSV:  output/poi_heat_weights.csv
```

## 常见问题

### Q: API 调用失败，提示 "ANTHROPIC_API_KEY not found"
**A:** 检查 `.env` 文件是否存在且正确配置了 `ANTHROPIC_API_KEY`

### Q: 返回 JSON 解析失败
**A:** Claude 的响应格式可能不是纯 JSON。检查 API 返回的内容，或联系 Anthropic 支持

### Q: 热度分数都是 0 或 1
**A:** 检查热力图图像质量和热度分布。确保红色区域清晰可见

### Q: 如何修改输出的 POI 数量（不是 100）？
**A:** 编辑 `poi_heat_analyzer.py` 中的 Claude prompt，修改"生成TOP100"为你需要的数量

## 高级用法

### 与现有滴滴系统集成

poi_heat_analyzer.py 生成的 POI 数据可以直接导入到 heatmap_generator.py 的数据处理流程中：

```python
# 在 data_processor.py 中
import json
poi_data = json.load(open('output/poi_heat_weights.json'))
# 可以将 POI 热度分数与现有网格热度数据合并
```

### 批量处理多个热力图

```bash
for img in heatmaps/*.jpg; do
  python3 poi_heat_analyzer.py --image "$img" --output "output/$(basename $img .jpg)"
done
```

## 技术细节

- **模型**: Claude Opus 4.7 (claude-opus-4-7)
- **Vision 能力**: 支持 JPEG/PNG 图像分析
- **输入**: 热力图图像 (任意分辨率)
- **输出**: 100 个 POI 的热度权重 (JSON/CSV)
- **处理时间**: ~10-30 秒（取决于 API 响应）

## 许可证和免责声明

此脚本基于 Anthropic Claude API 构建。使用时需遵守 API 使用条款。

POI 数据基于 Claude 的地理知识生成，可能存在不准确性。如用于商业用途，建议与权威地理数据源验证。
