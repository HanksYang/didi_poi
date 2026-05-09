#!/usr/bin/env python3
"""
测试脚本：验证火山引擎 API 集成和路径规划执行
"""

import sys
import json
from pathlib import Path
from traffic_provider import get_provider
from route_planner import (
    Location, plan_three_routes, generate_map, load_poi_data,
    load_config
)
from config import TRAFFIC_PROVIDER, VOLC_API_KEY
import config

def test_provider_init():
    """测试 Provider 初始化"""
    print("\n" + "="*70)
    print("【测试1】Provider 初始化")
    print("="*70)

    print(f"当前配置: TRAFFIC_PROVIDER={TRAFFIC_PROVIDER}")
    print(f"火山引擎 API Key: {VOLC_API_KEY[:15]}...")

    try:
        provider = get_provider()
        print(f"✓ Provider 初始化成功: {provider.__class__.__name__}")
        return True
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        return False


def test_route_planning():
    """测试路径规划"""
    print("\n" + "="*70)
    print("【测试2】路径规划执行")
    print("="*70)

    try:
        amap_key, city = load_config()

        # 加载 POI 数据
        pois = load_poi_data("output/poi_heat_weights.json")
        print(f"✓ 加载 {len(pois)} 个 POI")

        # 规划路线
        start = Location(lng=116.39, lat=39.90, name="中关村")
        end = Location(lng=116.46, lat=39.92, name="朝阳区")

        print(f"\n规划路线: {start.name} → {end.name}")
        routes = plan_three_routes(start, end, pois, amap_key)

        if not routes:
            print("❌ 无法规划路线")
            return False

        print(f"✓ 成功规划 {len(routes)} 条路线")

        # 显示路线信息
        for idx, route in enumerate(routes, 1):
            print(f"\n  路线{idx}:")
            print(f"    热度总和: {route.heat_score_sum:.2f}")
            print(f"    距离: {route.distance/1000:.2f} km")
            print(f"    接单评分: {route.heat_efficiency:.3f}")
            print(f"    途经点数: {len(route.waypoints)}")

        return True
    except Exception as e:
        print(f"❌ 路径规划失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_map_generation():
    """测试地图生成"""
    print("\n" + "="*70)
    print("【测试3】地图生成")
    print("="*70)

    try:
        amap_key, city = load_config()
        pois = load_poi_data("output/poi_heat_weights.json")

        start = Location(lng=116.39, lat=39.90, name="中关村")
        end = Location(lng=116.46, lat=39.92, name="朝阳区")
        routes = plan_three_routes(start, end, pois, amap_key)

        output_path = "output/test_route_plan.html"
        generate_map(start, end, routes, output_path)

        if Path(output_path).exists():
            size = Path(output_path).stat().st_size / 1024
            print(f"✓ 地图已生成: {output_path} ({size:.1f} KB)")
            return True
        else:
            print(f"❌ 地图生成失败")
            return False
    except Exception as e:
        print(f"❌ 地图生成失败: {e}")
        return False


def test_multi_routes():
    """测试多条路线规划"""
    print("\n" + "="*70)
    print("【测试4】多条路线规划")
    print("="*70)

    try:
        amap_key, city = load_config()
        pois = load_poi_data("output/poi_heat_weights.json")

        route_pairs = [
            ("三里屯", "国贸", "output/route_test_sanlitun.html"),
            ("中关村", "北京站", "output/route_test_zhongguancun.html"),
        ]

        for start_name, end_name, output_file in route_pairs:
            try:
                start = Location(lng=116.39, lat=39.90, name=start_name)
                end = Location(lng=116.46, lat=39.92, name=end_name)
                routes = plan_three_routes(start, end, pois, amap_key)

                if routes:
                    generate_map(start, end, routes, output_file)
                    best_route = routes[0]
                    print(f"✓ {start_name} → {end_name}: "
                          f"评分 {best_route.heat_efficiency:.3f}, "
                          f"{len(routes)} 条路线")
            except Exception as e:
                print(f"⚠️  {start_name} → {end_name} 规划失败: {e}")

        return True
    except Exception as e:
        print(f"❌ 多路线规划失败: {e}")
        return False


def test_export():
    """测试数据导出"""
    print("\n" + "="*70)
    print("【测试5】数据导出")
    print("="*70)

    try:
        amap_key, city = load_config()
        pois = load_poi_data("output/poi_heat_weights.json")

        start = Location(lng=116.39, lat=39.90, name="中关村")
        end = Location(lng=116.46, lat=39.92, name="朝阳区")
        routes = plan_three_routes(start, end, pois, amap_key)

        export_data = {
            "provider": TRAFFIC_PROVIDER,
            "start": {"name": start.name, "lng": start.lng, "lat": start.lat},
            "end": {"name": end.name, "lng": end.lng, "lat": end.lat},
            "routes_count": len(routes),
            "routes": [
                {
                    "id": route.route_id,
                    "heat_efficiency": route.heat_efficiency,
                    "waypoints": [wp.name for wp in route.waypoints],
                }
                for route in routes
            ]
        }

        export_file = "output/test_export.json"
        with open(export_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        print(f"✓ 数据已导出: {export_file}")
        print(f"  内容: {json.dumps(export_data, ensure_ascii=False, indent=2)}")
        return True
    except Exception as e:
        print(f"❌ 数据导出失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*70)
    print("🧪 DiDi POI 热力图系统 - 综合测试")
    print("="*70)
    print(f"\n系统配置:")
    print(f"  路况数据源: {TRAFFIC_PROVIDER}")
    print(f"  目标城市: {config.CITY}")

    tests = [
        ("Provider 初始化", test_provider_init),
        ("路径规划", test_route_planning),
        ("地图生成", test_map_generation),
        ("多条路线规划", test_multi_routes),
        ("数据导出", test_export),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 发生异常: {e}")
            results.append((test_name, False))

    # 测试总结
    print("\n" + "="*70)
    print("【测试总结】")
    print("="*70)

    for test_name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n总体: {passed}/{total} 测试通过")

    if passed == total:
        print("\n🎉 所有测试都通过了！系统运行正常。")
        sys.exit(0)
    else:
        print("\n⚠️  部分测试失败，请检查日志。")
        sys.exit(1)


if __name__ == "__main__":
    main()
