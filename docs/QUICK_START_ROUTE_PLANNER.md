# 路径规划器 - 5分钟快速开始

## ⚡ 最快体验

### 步骤1：验证配置（10秒）

```bash
cd /Users/jingxifanyiguan/Desktop/didi_poi

# 检查.env中的AMAP_API_KEY
cat .env | grep AMAP_API_KEY
```

确保看到类似输出：
```
AMAP_API_KEY=f4913c27a741d63daf6cb21b43ba8b80
```

### 步骤2：安装依赖（已完成）

所需包：`requests`, `folium`（已在前面步骤安装）

```bash
python3 -c "import requests, folium; print('✓ 依赖就绪')"
```

### 步骤3：运行路径规划（1分钟）

**用坐标运行** (北京 西客站→国贸):
```bash
python3 route_planner.py \
  --start "116.35,39.90" \
  --end "116.50,39.90"
```

**用地名运行** (三里屯→国贸):
```bash
python3 route_planner.py \
  --start "三里屯" \
  --end "国贸"
```

### 步骤4：查看结果（30秒）

程序会输出：

```
🗺️  路径规划系统
======================================================================
✅ 成功规划 3 条路线
======================================================================

【路线1】
  途经点数: 4
  接单概率评分 (热度/距离): 0.216

【路线2】
  途经点数: 3
  接单概率评分 (热度/距离): 0.165

【路线3】
  途经点数: 2
  接单概率评分 (热度/距离): 0.190

🗺️  生成地图...
✓ 地图已保存: output/route_plan.html

✨ 完成！在浏览器中打开地图: output/route_plan.html
```

### 步骤5：在地图上查看（10秒）

```bash
# macOS
open output/route_plan.html

# 或用浏览器直接打开
# /Users/jingxifanyiguan/Desktop/didi_poi/output/route_plan.html
```

---

## 🎯 三条路线是什么

| 路线 | 特点 | 适用场景 |
|------|------|--------|
| 路线1 | 评分最高，热度最多 | 优先选择，最有利接单 |
| 路线2 | 评分次高，中等热度 | 路线1堵车时备选 |
| 路线3 | 评分最低，热度最少 | 需要最短路线时选择 |

三条路线空间不重叠，让司机有多个选择。

---

## 📊 输入格式

### 坐标格式

```bash
# 格式: lng,lat (用逗号分隔，无空格)
python3 route_planner.py \
  --start "116.39,39.90" \
  --end "116.46,39.92"
```

| 起点 | 含义 |
|------|------|
| 116.39,39.90 | 北京中关村附近 |
| 116.35,39.88 | 北京金融街附近 |
| 116.50,39.95 | 北京朝阳区 |

### 地名格式

```bash
# 调用高德地理编码API
python3 route_planner.py \
  --start "三里屯" \
  --end "国贸"

# 或更具体的地名
python3 route_planner.py \
  --start "朝阳区三里屯" \
  --end "朝阳区国贸中心"
```

| 地名 | 含义 |
|------|------|
| 三里屯 | 北京著名商业街 |
| 国贸 | 国际贸易中心 |
| 中关村 | 高科技园区 |
| 五道口 | 北京商业街 |

---

## 🔧 更多命令行选项

### 基础选项

```bash
python3 route_planner.py \
  --start "起点" \              # 必需
  --end "终点"                  # 必需
```

### 高级选项

```bash
python3 route_planner.py \
  --start "116.39,39.90" \
  --end "116.46,39.92" \
  --city beijing \              # 城市（默认从.env读取）
  --output my_route.html \      # 输出地图文件
  --poi-data my_pois.json       # POI数据文件
```

### 示例：自定义输出目录

```bash
mkdir -p custom_output
python3 route_planner.py \
  --start "西单" \
  --end "朝阳公园" \
  --output custom_output/route.html
```

---

## 📈 接单概率评分解读

```
热度/距离 = 接单概率评分

0.20+  ⭐⭐⭐⭐⭐ 超优（强烈推荐）
0.15~0.20 ⭐⭐⭐⭐   很好
0.10~0.15 ⭐⭐⭐     不错
<0.10  ⭐⭐     较差
```

**实例**：
- 热度3.5，距离15km → 0.233 ⭐⭐⭐⭐⭐
- 热度2.5，距离20km → 0.125 ⭐⭐⭐

---

## 🛠️ 常见问题

### Q: 地名输入不成功？

A: 1. 确保地名是北京的（脚本默认beijing）
   2. 用更具体的地名，如"朝阳区三里屯"
   3. 用坐标代替

### Q: API报错？

A: 1. 检查网络连接
   2. 检查 `AMAP_API_KEY` 是否正确
   3. 确认API配额未用完（免费300次/天）

### Q: 地图打不开？

A: 确保输出的HTML文件存在：
```bash
ls -lh output/route_plan.html
```

### Q: 三条路线都是同样的地方？

A: 这是因为演示数据较少。运行以生成真实POI数据：
```bash
python3 poi_heat_analyzer.py --image heatmap.jpg
# 再运行
python3 route_planner.py --start "三里屯" --end "国贸"
```

---

## 💡 使用建议

### 场景1：早高峰接单

```bash
# 查找高热度集中的路线
python3 route_planner.py --start "住所" --end "市中心"

# 选择评分最高的路线（通常路线1）
```

### 场景2：比较多个路线对

```bash
# 批量规划
for pair in "三里屯|国贸" "中关村|北京站" "朝阳公园|西单"; do
  IFS='|' read start end <<< "$pair"
  python3 route_planner.py --start "$start" --end "$end"
done
```

### 场景3：动态调整

```bash
# 根据实时热力图调用
python3 route_planner.py --start "当前位置" --end "目标位置"

# 然后选择最优的三条中的一条
```

---

## 📱 地图交互

在 `output/route_plan.html` 中：

- **滚动缩放** — 用鼠标滚轮
- **拖拽移动** — 左键拖动地图
- **点击POI** — 查看详细信息
- **路线选择** — 不同颜色代表三条路线

---

## 🚀 下一步

1. ✅ 已验证配置和依赖
2. ✅ 已运行路径规划
3. ✅ 已查看地图结果
4. ⏳ 如需真实POI数据：运行 `poi_heat_analyzer.py`
5. ⏳ 如需集成到生产：参考 `README_ROUTE_PLANNER.md` 的集成部分

---

## 📚 更多文档

- **详细文档** — `README_ROUTE_PLANNER.md`
- **脚本源码** — `route_planner.py`
- **POI热度** — `README_POI_ANALYZER.md` 和 `poi_heat_analyzer.py`

---

## ✨ 就这么简单！

```bash
# 完整一行命令体验
python3 route_planner.py --start "116.39,39.90" --end "116.46,39.92" && open output/route_plan.html
```

享受最优接单路线！🎯
