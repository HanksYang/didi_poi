# 滴滴司机接单最优路径规划器

## 功能介绍

`route_planner.py` 是一个基于高德地图API和POI热度权重的智能路径规划工具，可以：

1. **多格式输入支持** - 接受经纬度坐标或中文地名作为起点/终点
2. **三条高热度路径** - 规划三条都追求高接单概率但空间不重叠的驾车路线
3. **热度加权规划** - 优先途经高热度POI，提高司机接单概率
4. **可视化展示** - 在Folium地图上显示三条路线、POI分布和接单评分
5. **离线演示** - 内置北京主要POI演示数据，无需先生成POI权重也能使用

## 快速开始

### 基础用法

```bash
# 用坐标规划（起点和终点）
python3 route_planner.py --start "116.35,39.90" --end "116.50,39.90"

# 用地名规划
python3 route_planner.py --start "三里屯" --end "国贸"

# 混合使用坐标和地名
python3 route_planner.py --start "116.443,39.906" --end "国贸"
```

### 完整参数

```bash
python3 route_planner.py \
  --start "起点(坐标或地名)"  \          # 必需
  --end "终点(坐标或地名)"    \          # 必需
  --city beijing              \          # 城市(默认从.env读取)
  --output output/route.html  \          # 输出地图文件
  --poi-data output/poi_heat_weights.json  # POI数据文件
```

## 工作原理

### 1. 输入解析

支持两种格式：

- **坐标格式**: `116.39,39.90` — 直接使用
- **地名格式**: `国贸`, `三里屯` — 调用高德地理编码API转换为坐标

### 2. POI加载

- 优先读取 `output/poi_heat_weights.json`（由poi_heat_analyzer.py生成）
- 如果不存在，使用内置演示数据（北京30个主要POI）
- 每个POI包含：name, lng, lat, heat_score(0-1), district, category

### 3. 三路径规划

**基本思路**：按起终点连线的侧向(left/center/right)分组POI，每组独立规划一条路线

```
                    ◆ 北京大学
                   / \
        ◇ 五道口  /   \  ◆ 798艺术区
                /       \
        ◇ 西单 /         \ ◆ 三里屯
         ___/_____________\___
      起点◆    中心路线        ◆终点
                (经过高热POI)
```

**分组方法**：
1. 计算每个POI到起终点连线的距离
2. 筛选距离在buffer范围内的POI
3. 根据叉积判断POI在左/中/右侧
4. 每组按热度从高到低排序

**途经点选择**：
- 从左组选 top-4 高热度POI 作为路线1的途经点
- 从中组选 top-4 高热度POI 作为路线2的途经点
- 从右组选 top-4 高热度POI 作为路线3的途经点

### 4. 高德驾车规划

调用高德 `direction/driving` API：

```
GET https://restapi.amap.com/v3/direction/driving
  ?origin=116.35,39.90
  &destination=116.50,39.90
  &waypoints=116.40,39.91|116.42,39.91  # 途经点
  &key=YOUR_AMAP_KEY
```

返回：
- `distance` — 实际路线距离（米）
- `duration` — 预计时长（秒）
- `polyline` — 道路坐标串（编码格式）

### 5. 接单概率评分

**评分公式**：
```
heat_efficiency = 途经POI热度总和 / (路线距离/1000)
               = sum(heat_score) / distance_km
```

**示例**：
- 热度总和：3.5，距离：15km → 评分 = 3.5/15 = 0.233
- 热度总和：3.2，距离：12km → 评分 = 3.2/12 = 0.267 (更优)

评分越高，表示单位距离内的热度积累越多，接单概率越高。

### 6. 地图可视化

使用Folium生成交互式地图：

- **绿色标记** — 起点
- **红色标记** — 终点
- **三条不同颜色的路线** — 红、青、黄分别代表三条方案
- **彩色圆点** — 途经POI，大小/颜色对应热度

## 输出示例

### 控制台输出

```
🗺️  路径规划系统
======================================================================

📍 解析起点: 116.35,39.90
   ✓ (116.35,39.90) (116.35, 39.90)

📍 解析终点: 116.50,39.90
   ✓ (116.50,39.90) (116.50, 39.90)

📊 加载POI数据...
✓ 加载 30 个POI

🛣️  规划最优路线...
   规划 LEFT 路线... 途经点: ['中关村', '五道口', '西单广场', '闽龙广场']
   规划 CENTER 路线... 途经点: ['国贸中心', '金融街', '天安门广场', '故宫']
   规划 RIGHT 路线... 途经点: ['三里屯', '朝阳公园', '798艺术区', '建国门']

======================================================================
✅ 成功规划 3 条路线
======================================================================

【路线1】
  途经点数: 4
  途经点: 中关村 → 五道口 → 西单广场 → 闽龙广场
  热度总和: 3.33
  距离: 15.39 km
  时长: 46 分钟
  接单概率评分 (热度/距离): 0.216

【路线2】
  途经点数: 4
  途经点: 国贸中心 → 金融街 → 天安门广场 → 故宫
  热度总和: 3.06
  距离: 18.52 km
  时长: 52 分钟
  接单概率评分 (热度/距离): 0.165

【路线3】
  途经点数: 4
  途经点: 三里屯 → 朝阳公园 → 798艺术区 → 建国门
  热度总和: 3.18
  距离: 16.75 km
  时长: 48 分钟
  接单概率评分 (热度/距离): 0.190

🗺️  生成地图...
✓ 地图已保存: output/route_plan.html

✨ 完成！在浏览器中打开地图: output/route_plan.html
```

### 地图文件

`output/route_plan.html` — 交互式地图

## 与POI热度系统集成

### 场景1：有POI权重数据

```bash
# 1. 生成POI热度权重
python3 poi_heat_analyzer.py --image heatmap.jpg

# 2. 规划最优路线（自动加载output/poi_heat_weights.json）
python3 route_planner.py --start "中关村" --end "三里屯"
```

### 场景2：自定义POI数据

编辑 `route_planner.py` 的 `get_demo_poi_data()` 函数，或创建自己的JSON：

```json
{
  "poi_list": [
    {
      "rank": 1,
      "name": "自定义POI",
      "district": "朝阳区",
      "category": "商务",
      "lng": 116.39,
      "lat": 39.90,
      "heat_score": 0.95
    }
  ]
}
```

然后：
```bash
python3 route_planner.py \
  --start "116.35,39.90" \
  --end "116.50,39.90" \
  --poi-data your_poi_data.json
```

## 高级用法

### 批量规划多个路线对

```bash
#!/bin/bash
routes=(
  "中关村|国贸"
  "三里屯|北京站"
  "朝阳公园|金融街"
)

for route in "${routes[@]}"; do
  IFS='|' read -r start end <<< "$route"
  echo "规划 $start → $end"
  python3 route_planner.py --start "$start" --end "$end" \
    --output "output/route_${start}_${end}.html"
done
```

### 集成到Web服务

```python
from route_planner import (
    parse_location_input, load_poi_data, plan_three_routes,
    generate_map, load_config
)

amap_key, city = load_config()

start = parse_location_input("三里屯", city, amap_key)
end = parse_location_input("国贸", city, amap_key)
pois = load_poi_data("output/poi_heat_weights.json")

routes = plan_three_routes(start, end, pois, amap_key)

for route in routes:
    print(f"路线 {route.route_id}: {route.heat_efficiency:.3f}")
```

## 常见问题

### Q: 为什么只规划出了1条或2条路线？

**A:** 演示数据较少或POI分布不均。两个解决方案：
- 运行 `poi_heat_analyzer.py` 生成真实的100个POI
- 修改 `get_demo_poi_data()` 添加更多演示POI

### Q: 高德API调用失败怎么办？

**A:** 检查以下项：
1. `.env` 中的 `AMAP_API_KEY` 是否正确
2. API Key 的免费配额是否已用完（每天免费300次）
3. 网络连接是否正常

### Q: 如何修改三条路线的数量？

**A:** 编辑 `plan_three_routes()` 函数的 `sides` 列表：

```python
sides = ["left", "center", "right"]  # 改为想要的数量
```

### Q: 为什么地图显示的路线与控制台数据不符？

**A:** 这通常是因为polyline解码错误。检查 `decode_polyline()` 函数的实现，确保高德返回的编码格式正确。

### Q: 如何调整每条路线的途经点数？

**A:** 编辑 `select_waypoints()` 的 `num_waypoints` 参数（默认4）：

```python
waypoints = select_waypoints(grouped, side, num_waypoints=6)
```

高德API限制最多16个途经点，但建议不超过8个以避免路线过度绕路。

## 架构设计

### 模块结构

| 模块 | 功能 |
|------|------|
| Location | 地理位置数据类 |
| POI | 兴趣点数据类 |
| Route | 路线数据类及评分方法 |
| 工具函数 | 距离计算、编码解析、API调用 |
| 主函数 | CLI入口和全流程协调 |

### 关键算法

1. **Haversine公式** — 计算两点大圆距离
2. **点到直线距离** — 判断POI离起终点连线的偏离程度
3. **叉积** — 判断POI在直线的左侧还是右侧
4. **Polyline编码** — 解析高德API返回的压缩坐标

## 性能指标

| 操作 | 耗时 |
|------|------|
| 地理编码（地名→坐标） | ~200ms（单次API调用） |
| POI加载和筛选 | ~50ms（100个POI） |
| 三路线规划（含3次API） | ~3秒（每次高德API ~1s） |
| 地图生成 | ~500ms |
| **总耗时** | ~4秒 |

## 许可和免责

- 本脚本基于高德地图API和开源库（folium、requests等）
- 接单概率评分为启发式算法，不代表实际接单率
- 使用高德API需遵守其服务条款和配额限制
- 路线规划结果仅供参考，实际驾行请遵守交通规则

## 下一步

- [ ] 获得高德地图 Web服务 API Key
- [ ] 配置 .env 文件
- [ ] 运行 poi_heat_analyzer.py 生成真实POI权重
- [ ] 运行 route_planner.py 规划最优路线
- [ ] 在浏览器中打开HTML地图
- [ ] 根据评分选择最优路线进行接单
