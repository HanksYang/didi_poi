#!/usr/bin/env python3
"""
路径规划器使用示例

展示如何：
1. 批量规划多条路线
2. 与POI系统集成
3. 自定义评分和排序
4. 生成报告
"""

from route_planner import (
    load_config, parse_location_input, load_poi_data,
    plan_three_routes, generate_map, Location, POI
)
import json
from pathlib import Path
from datetime import datetime


def example_1_basic_usage():
    """示例1: 基础使用"""
    print("\n" + "="*70)
    print("【示例1】基础使用 - 规划单条路线对")
    print("="*70)

    amap_key, city = load_config()

    # 指定起终点
    start = Location(lng=116.39, lat=39.90, name="中关村")
    end = Location(lng=116.46, lat=39.92, name="朝阳区")

    # 加载POI
    pois = load_poi_data("output/poi_heat_weights.json")

    # 规划路线
    routes = plan_three_routes(start, end, pois, amap_key)

    # 显示结果
    print(f"\n从 {start.name} 到 {end.name}，规划了 {len(routes)} 条路线：\n")
    for idx, route in enumerate(routes, 1):
        print(f"路线{idx}: {route.heat_efficiency:.3f} 分")
        print(f"  热度总和: {route.heat_score_sum:.2f}")
        print(f"  距离: {route.distance/1000:.2f} km")
        if route.waypoints:
            print(f"  途经: {' → '.join([wp.name for wp in route.waypoints])}")
        print()

    # 生成地图
    generate_map(start, end, routes, "output/example1_basic.html")
    print(f"✓ 地图已保存: output/example1_basic.html\n")


def example_2_batch_planning():
    """示例2: 批量规划"""
    print("\n" + "="*70)
    print("【示例2】批量规划 - 同时规划多条路线对")
    print("="*70)

    amap_key, city = load_config()
    pois = load_poi_data("output/poi_heat_weights.json")

    # 多个路线对（地名格式）
    route_pairs = [
        ("三里屯", "国贸"),
        ("中关村", "北京站"),
        ("西单", "朝阳公园"),
    ]

    results = []

    for start_name, end_name in route_pairs:
        print(f"\n规划: {start_name} → {end_name}")
        try:
            start = parse_location_input(start_name, city, amap_key)
            end = parse_location_input(end_name, city, amap_key)
            routes = plan_three_routes(start, end, pois, amap_key)

            if routes:
                best_route = routes[0]
                results.append({
                    "start": start_name,
                    "end": end_name,
                    "route_count": len(routes),
                    "best_score": best_route.heat_efficiency,
                    "distance": best_route.distance / 1000,
                    "waypoints": [wp.name for wp in best_route.waypoints],
                })
                print(f"  ✓ 成功 - 最优路线评分: {best_route.heat_efficiency:.3f}")
        except Exception as e:
            print(f"  ❌ 失败: {e}")

    # 按评分排序
    results.sort(key=lambda x: x["best_score"], reverse=True)

    # 输出摘要
    print("\n" + "-"*70)
    print("【批量规划摘要】")
    print("-"*70)
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['start']} → {result['end']}")
        print(f"   评分: {result['best_score']:.3f}")
        print(f"   距离: {result['distance']:.2f}km")


def example_3_custom_poi():
    """示例3: 自定义POI数据"""
    print("\n" + "="*70)
    print("【示例3】自定义POI - 使用自定义的热度权重")
    print("="*70)

    amap_key, city = load_config()

    # 创建自定义POI列表
    custom_pois = [
        POI("公司A", 116.35, 39.88, 0.95, "西城区", "办公"),
        POI("客户B", 116.42, 39.92, 0.92, "朝阳区", "客户"),
        POI("午餐地点", 116.39, 39.90, 0.50, "海淀区", "餐饮"),
        POI("加油站", 116.38, 39.87, 0.30, "西城区", "服务"),
        POI("停车场", 116.45, 39.93, 0.25, "朝阳区", "服务"),
        POI("目的地C", 116.48, 39.95, 0.88, "朝阳区", "客户"),
    ]

    start = Location(lng=116.35, lat=39.88, name="公司A")
    end = Location(lng=116.48, lat=39.95, name="目的地C")

    routes = plan_three_routes(start, end, custom_pois, amap_key)

    print(f"\n使用 {len(custom_pois)} 个自定义POI，规划了 {len(routes)} 条路线\n")
    for idx, route in enumerate(routes, 1):
        print(f"路线{idx}:")
        print(f"  评分: {route.heat_efficiency:.3f}")
        if route.waypoints:
            waypoint_str = " → ".join([f"{wp.name}({wp.heat_score:.2f})" for wp in route.waypoints])
            print(f"  途经: {waypoint_str}")


def example_4_route_analysis():
    """示例4: 路线分析"""
    print("\n" + "="*70)
    print("【示例4】路线分析 - 评估和比较")
    print("="*70)

    amap_key, city = load_config()
    pois = load_poi_data("output/poi_heat_weights.json")

    start = parse_location_input("三里屯", city, amap_key)
    end = parse_location_input("国贸", city, amap_key)
    routes = plan_three_routes(start, end, pois, amap_key)

    print(f"\n分析 {len(routes)} 条从 {start.name} 到 {end.name} 的路线\n")

    # 详细分析
    for idx, route in enumerate(routes, 1):
        print(f"【路线{idx}】详细分析")
        print(f"  热度总和: {route.heat_score_sum:.2f}")
        print(f"  距离: {route.distance/1000:.2f} km")
        print(f"  时长: {route.duration/60:.0f} 分钟")
        print(f"  热度/距离: {route.heat_efficiency:.3f}")

        if route.waypoints:
            print(f"  途经点分析:")
            for wp in route.waypoints:
                print(f"    - {wp.name}: {wp.heat_score:.2f} ({wp.district})")

        # 计算平均热度
        avg_heat = route.heat_score_sum / len(route.waypoints) if route.waypoints else 0
        print(f"  平均热度: {avg_heat:.2f}")
        print(f"  单位距离热度: {route.heat_efficiency:.4f} (热/km)")
        print()

    # 排名建议
    print("【建议】")
    best = routes[0]
    if best.heat_efficiency > 0.2:
        print("✓ 强烈推荐路线1，接单概率最高")
    elif best.heat_efficiency > 0.15:
        print("✓ 推荐路线1，接单概率较高")
    else:
        print("✓ 可选择路线1，但热度较低，建议选择其他方案")


def example_5_export_json():
    """示例5: 导出结果为JSON"""
    print("\n" + "="*70)
    print("【示例5】导出数据 - 保存规划结果为JSON")
    print("="*70)

    amap_key, city = load_config()
    pois = load_poi_data("output/poi_heat_weights.json")

    start = parse_location_input("中关村", city, amap_key)
    end = parse_location_input("朝阳公园", city, amap_key)
    routes = plan_three_routes(start, end, pois, amap_key)

    # 构建导出数据
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "start": {
            "name": start.name,
            "lng": start.lng,
            "lat": start.lat,
        },
        "end": {
            "name": end.name,
            "lng": end.lng,
            "lat": end.lat,
        },
        "routes": [
            {
                "id": route.route_id,
                "heat_score_sum": route.heat_score_sum,
                "distance_km": route.distance / 1000,
                "duration_min": route.duration / 60,
                "heat_efficiency": route.heat_efficiency,
                "waypoints": [
                    {
                        "name": wp.name,
                        "lng": wp.lng,
                        "lat": wp.lat,
                        "heat_score": wp.heat_score,
                        "category": wp.category,
                    }
                    for wp in route.waypoints
                ],
            }
            for route in routes
        ]
    }

    # 保存到文件
    output_file = "output/route_export.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 数据已导出: {output_file}\n")
    print("文件内容预览:")
    print(json.dumps(export_data, ensure_ascii=False, indent=2)[:500] + "...\n")


def main():
    """运行所有示例"""
    print("\n" + "="*70)
    print("🚀 路径规划器 - 使用示例")
    print("="*70)

    examples = [
        ("1", "基础使用", example_1_basic_usage),
        ("2", "批量规划", example_2_batch_planning),
        ("3", "自定义POI", example_3_custom_poi),
        ("4", "路线分析", example_4_route_analysis),
        ("5", "导出结果", example_5_export_json),
    ]

    print("\n可用示例:")
    for idx, name, _ in examples:
        print(f"  {idx}. {name}")

    print("\n运行特定示例:")
    print("  python3 example_route_planner.py 1    # 运行示例1")
    print("  python3 example_route_planner.py all  # 运行所有示例")
    print()

    import sys
    if len(sys.argv) > 1:
        choice = sys.argv[1]
        if choice == "all":
            for idx, name, func in examples:
                try:
                    func()
                except Exception as e:
                    print(f"\n❌ 示例{idx}失败: {e}")
        else:
            for idx, name, func in examples:
                if idx == choice:
                    try:
                        func()
                    except Exception as e:
                        print(f"\n❌ 示例{choice}失败: {e}")
                    break
            else:
                print(f"❌ 示例 {choice} 不存在")
    else:
        # 默认运行示例1
        try:
            example_1_basic_usage()
        except Exception as e:
            print(f"❌ 执行失败: {e}")
            print("\n💡 提示: 确保已生成POI数据")
            print("   运行: python3 poi_heat_analyzer.py --image heatmap.jpg")


if __name__ == "__main__":
    main()
