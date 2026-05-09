#!/usr/bin/env python3
"""
滴滴司机接单最优路径规划器
根据POI热度权重，规划三条高热度、空间不重叠的驾车路线
"""

import os
import sys
import json
import argparse
import requests
import math
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import numpy as np
import folium
from folium import plugins


@dataclass
class Location:
    """地理位置"""
    lng: float
    lat: float
    name: str

    @property
    def coord_tuple(self) -> Tuple[float, float]:
        return (self.lng, self.lat)

    @property
    def amap_str(self) -> str:
        return f"{self.lng},{self.lat}"


@dataclass
class POI:
    """兴趣点"""
    name: str
    lng: float
    lat: float
    heat_score: float
    district: str = ""
    category: str = ""
    rank: int = 0

    def distance_to(self, other: 'POI') -> float:
        """计算到另一个POI的直线距离（米）"""
        return haversine_distance(self.lng, self.lat, other.lng, other.lat)

    def distance_to_line(self, p1: Location, p2: Location) -> float:
        """计算到直线的距离"""
        return point_to_line_distance(self.lng, self.lat, p1.lng, p1.lat, p2.lng, p2.lat)

    def get_side(self, p1: Location, p2: Location) -> int:
        """判断POI在起终点连线的哪一侧：-1左侧，0中间，1右侧"""
        cross = (p2.lng - p1.lng) * (self.lat - p1.lat) - (p2.lat - p1.lat) * (self.lng - p1.lng)
        # 使用较小的阈值，让更多POI被分类到左/右侧而不是中间
        if cross > 0.001:  # 左侧
            return -1
        elif cross < -0.001:  # 右侧
            return 1
        else:  # 中间
            return 0


@dataclass
class Route:
    """路线"""
    route_id: int
    start: Location
    end: Location
    waypoints: List[POI]
    distance: float = 0.0
    duration: int = 0
    polyline: Optional[str] = None
    heat_score_sum: float = 0.0

    @property
    def heat_efficiency(self) -> float:
        """接单概率评分 = 热度总和 / 距离(km)"""
        if self.distance <= 0:
            return 0
        return self.heat_score_sum / (self.distance / 1000.0)

    @property
    def amap_waypoints_str(self) -> str:
        """高德API格式的途经点字符串"""
        if not self.waypoints:
            return ""
        return "|".join([f"{wp.lng},{wp.lat}" for wp in self.waypoints])


# ==================== 工具函数 ====================

def haversine_distance(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """
    计算两点间大圆距离（米）
    """
    R = 6371000  # 地球半径（米）
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def point_to_line_distance(x: float, y: float, x1: float, y1: float, x2: float, y2: float) -> float:
    """
    计算点(x,y)到直线(x1,y1)-(x2,y2)的距离
    """
    if x1 == x2 and y1 == y2:
        return haversine_distance(x, y, x1, y1)

    # 使用向量叉积计算点到直线的距离
    a = (y2 - y1) ** 2 + (x2 - x1) ** 2
    b = 2 * ((y2 - y1) * (y1 - y) + (x2 - x1) * (x1 - x))
    c = (y1 - y) ** 2 + (x1 - x) ** 2 - (((x2 - x1) * (y1 - y) - (y2 - y1) * (x1 - x)) ** 2) / a

    dist_squared = c
    if dist_squared < 0:
        dist_squared = 0

    # 转换到米
    avg_lat = (y + y1 + y2) / 3
    lng_to_m = 111320 * math.cos(math.radians(avg_lat))
    lat_to_m = 111320

    return math.sqrt(dist_squared * (lng_to_m ** 2 + lat_to_m ** 2) / 2)


def load_config() -> Tuple[str, str]:
    """加载配置"""
    load_dotenv()
    amap_key = os.getenv("AMAP_API_KEY")
    city = os.getenv("CITY", "beijing")
    if not amap_key:
        raise ValueError("AMAP_API_KEY not found in .env")
    return amap_key, city


def geocode_address(address: str, city: str, amap_key: str) -> Location:
    """
    调用高德地理编码API，将地名转为坐标
    """
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "address": address,
        "city": city,
        "key": amap_key,
        "output": "json"
    }

    try:
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()

        if data.get("status") != "1" or not data.get("geocodes"):
            raise ValueError(f"地址 {address} 在 {city} 未找到")

        location = data["geocodes"][0]["location"]
        lng, lat = map(float, location.split(","))
        return Location(lng=lng, lat=lat, name=address)
    except Exception as e:
        raise ValueError(f"地理编码失败: {e}")


def parse_location_input(loc_str: str, city: str, amap_key: str) -> Location:
    """
    解析输入的起点/终点，支持坐标或地名
    """
    loc_str = loc_str.strip()

    # 尝试识别为坐标（lng,lat 格式）
    if "," in loc_str:
        try:
            parts = loc_str.split(",")
            lng, lat = float(parts[0].strip()), float(parts[1].strip())
            # 基本检查
            if 73 <= lng <= 135 and 18 <= lat <= 53:  # 中国范围
                return Location(lng=lng, lat=lat, name=f"({lng},{lat})")
        except (ValueError, IndexError):
            pass

    # 否则作为地名调用高德API
    return geocode_address(loc_str, city, amap_key)


def load_poi_data(json_path: str) -> List[POI]:
    """
    加载POI热度数据
    """
    if not os.path.exists(json_path):
        print(f"⚠️  POI数据文件不存在: {json_path}")
        print("   使用演示数据，请先运行: python3 poi_heat_analyzer.py")
        return get_demo_poi_data()

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        poi_list = []
        for poi_data in data.get("poi_list", []):
            poi = POI(
                name=poi_data.get("name", ""),
                lng=poi_data.get("lng", 0),
                lat=poi_data.get("lat", 0),
                heat_score=poi_data.get("heat_score", 0),
                district=poi_data.get("district", ""),
                category=poi_data.get("category", ""),
                rank=poi_data.get("rank", 0)
            )
            poi_list.append(poi)

        print(f"✓ 加载 {len(poi_list)} 个POI")
        return poi_list
    except Exception as e:
        print(f"❌ 加载POI数据失败: {e}")
        return get_demo_poi_data()


def get_demo_poi_data() -> List[POI]:
    """
    演示数据：北京主要商业/交通枢纽
    """
    demo_pois = [
        # 高热度商务区
        POI("国贸中心", 116.4611, 39.9043, 0.95, "朝阳区", "商务区"),
        POI("CBD东扩", 116.4837, 39.9040, 0.90, "朝阳区", "商务区"),
        POI("金融街", 116.3618, 39.8973, 0.85, "西城区", "商务区"),
        POI("中关村", 116.3195, 39.9827, 0.88, "海淀区", "高科技园区"),

        # 左侧(西部)热点
        POI("西单广场", 116.3625, 39.9087, 0.83, "西城区", "商业街"),
        POI("宣武门", 116.3556, 39.8886, 0.80, "西城区", "商业"),
        POI("复兴门", 116.3476, 39.8956, 0.78, "西城区", "商业"),
        POI("闽龙广场", 116.3283, 39.9156, 0.76, "西城区", "商业"),

        # 右侧(东部)热点
        POI("三里屯", 116.4426, 39.9060, 0.92, "朝阳区", "商业街"),
        POI("王府井", 116.4177, 39.9050, 0.82, "东城区", "商业街"),
        POI("东直门", 116.4372, 39.9310, 0.79, "东城区", "商业"),
        POI("建国门", 116.4356, 39.8896, 0.77, "东城区", "商业"),
        POI("朝阳门", 116.4288, 39.9148, 0.75, "东城区", "商业"),

        # 中部路线
        POI("五道口", 116.3303, 39.9997, 0.86, "海淀区", "商业街"),
        POI("北京站", 116.4288, 39.9026, 0.81, "东城区", "交通枢纽"),
        POI("天安门广场", 116.3974, 39.9075, 0.75, "东城区", "景点"),
        POI("故宫", 116.3972, 39.9164, 0.74, "东城区", "景点"),

        # 北部热点
        POI("798艺术区", 116.4862, 39.9788, 0.76, "朝阳区", "艺术区"),
        POI("奥体中心", 116.4081, 40.0046, 0.70, "朝阳区", "体育"),
        POI("北京大学", 116.3065, 40.0053, 0.71, "海淀区", "学校"),
        POI("清华大学", 116.2619, 40.0086, 0.72, "海淀区", "学校"),
        POI("颐和园", 116.2752, 40.0008, 0.73, "海淀区", "景点"),

        # 交通枢纽
        POI("北京南站", 116.3783, 39.8658, 0.78, "丰台区", "交通枢纽"),
        POI("首都机场", 116.5851, 40.0808, 0.79, "朝阳区", "交通枢纽"),
        POI("大兴机场", 116.5837, 39.7455, 0.80, "大兴区", "交通枢纽"),

        # 其他热点
        POI("朝阳公园", 116.5417, 39.9547, 0.77, "朝阳区", "公园"),
        POI("日坛公园", 116.4500, 39.9400, 0.69, "朝阳区", "公园"),
        POI("陶然亭公园", 116.3440, 39.8760, 0.68, "西城区", "公园"),
    ]
    return demo_pois


def filter_and_rank_pois(pois: List[POI], start: Location, end: Location) -> Dict[str, List[POI]]:
    """
    按地理位置把POI分为左/中/右三组，每组按热度排序
    返回: {"left": [...], "center": [...], "right": [...]}
    """
    # 计算起终点距离作为参考
    route_distance = haversine_distance(start.lng, start.lat, end.lng, end.lat)
    # buffer = 起终点距离的 0.5倍 + 5km，确保覆盖足够宽的区域
    BUFFER_DIST = max(route_distance * 0.5, 5000)

    filtered = []
    for poi in pois:
        dist_to_line = poi.distance_to_line(start, end)
        # 距离直线不超过buffer，且不太偏离起终点连线
        if dist_to_line <= BUFFER_DIST:
            filtered.append(poi)

    # 按起终点连线的侧向分组（用更宽松的阈值）
    left_pois = []
    center_pois = []
    right_pois = []

    for p in filtered:
        side = p.get_side(start, end)
        if side == -1:
            left_pois.append(p)
        elif side == 0:
            center_pois.append(p)
        else:
            right_pois.append(p)

    # 每组按热度从高到低排序
    left_pois.sort(key=lambda p: p.heat_score, reverse=True)
    center_pois.sort(key=lambda p: p.heat_score, reverse=True)
    right_pois.sort(key=lambda p: p.heat_score, reverse=True)

    # debug info
    # print(f"   [DEBUG] buffer={BUFFER_DIST/1000:.1f}km, filtered={len(filtered)}, left={len(left_pois)}, center={len(center_pois)}, right={len(right_pois)}")

    return {
        "left": left_pois,
        "center": center_pois,
        "right": right_pois
    }


def select_waypoints(grouped_pois: Dict[str, List[POI]], side: str, num_waypoints: int = 4) -> List[POI]:
    """
    从指定侧向选择热度最高的途经点
    """
    waypoints = grouped_pois[side][:num_waypoints]
    return waypoints


def call_amap_driving(start: Location, end: Location, waypoints: List[POI],
                      amap_key: str) -> Optional[Route]:
    """
    调用高德驾车路线规划API
    """
    url = "https://restapi.amap.com/v3/direction/driving"

    waypoints_str = ""
    if waypoints:
        waypoints_str = "|".join([f"{wp.lng},{wp.lat}" for wp in waypoints])

    params = {
        "origin": start.amap_str,
        "destination": end.amap_str,
        "waypoints": waypoints_str,
        "key": amap_key,
        "output": "json"
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()

        if data.get("status") != "1":
            print(f"⚠️  高德API错误: {data.get('info')}")
            return None

        route_data = data["route"]
        paths = route_data.get("paths", [])
        if not paths:
            return None

        path = paths[0]
        distance = path.get("distance", 0)
        duration = path.get("duration", 0)
        polyline = path.get("polyline", "")

        heat_score_sum = sum(wp.heat_score for wp in waypoints)

        route = Route(
            route_id=0,
            start=start,
            end=end,
            waypoints=waypoints,
            distance=float(distance),
            duration=int(duration),
            polyline=polyline,
            heat_score_sum=heat_score_sum
        )
        return route
    except Exception as e:
        print(f"⚠️  高德API调用失败: {e}")
        return None


def plan_three_routes(start: Location, end: Location, pois: List[POI],
                      amap_key: str) -> List[Route]:
    """
    规划三条高热度、空间不重叠的路线
    """
    # 按侧向分组POI
    grouped = filter_and_rank_pois(pois, start, end)

    routes = []
    sides = ["left", "center", "right"]

    for route_id, side in enumerate(sides, 1):
        waypoints = select_waypoints(grouped, side, num_waypoints=4)

        if not waypoints:
            print(f"   ⚠️  {side} 侧没有合适的途经点")
            continue

        print(f"   规划 {side.upper()} 路线... 途经点: {[wp.name for wp in waypoints]}")
        route = call_amap_driving(start, end, waypoints, amap_key)

        if route:
            route.route_id = route_id
            routes.append(route)

    # 按接单概率从高到低排序
    routes.sort(key=lambda r: r.heat_efficiency, reverse=True)

    return routes


def decode_polyline(encoded: str) -> List[Tuple[float, float]]:
    """
    解码高德的polyline格式为坐标列表
    """
    if not encoded:
        return []

    points = []
    index = 0
    lat = 0
    lng = 0

    while index < len(encoded):
        result = 0
        shift = 0

        while True:
            b = ord(encoded[index]) - 64
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not (b & 0x20):
                break

        dlat = ~(result >> 1) if (result & 1) else (result >> 1)
        lat += dlat

        result = 0
        shift = 0

        while True:
            b = ord(encoded[index]) - 64
            index += 1
            result |= (b & 0x1f) << shift
            shift += 5
            if not (b & 0x20):
                break

        dlng = ~(result >> 1) if (result & 1) else (result >> 1)
        lng += dlng

        points.append((lng / 1e5, lat / 1e5))

    return points


def generate_map(start: Location, end: Location, routes: List[Route],
                output_path: str = "output/route_plan.html"):
    """
    生成Folium地图
    """
    # 计算地图中心
    center_lat = (start.lat + end.lat) / 2
    center_lng = (start.lng + end.lng) / 2

    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=12,
        tiles="OpenStreetMap"
    )

    # 色彩方案
    colors = ["#FF6B6B", "#4ECDC4", "#FFE66D"]  # 红、青、黄

    # 绘制起终点
    folium.Marker(
        location=[start.lat, start.lng],
        popup=f"<b>起点</b><br>{start.name}",
        icon=folium.Icon(color="green", icon="play"),
        tooltip="起点"
    ).add_to(m)

    folium.Marker(
        location=[end.lat, end.lng],
        popup=f"<b>终点</b><br>{end.name}",
        icon=folium.Icon(color="red", icon="stop"),
        tooltip="终点"
    ).add_to(m)

    # 绘制三条路线
    for idx, route in enumerate(routes):
        color = colors[idx % len(colors)]

        # 解码polyline
        if route.polyline:
            points = decode_polyline(route.polyline)
        else:
            points = [(start.lng, start.lat), (end.lng, end.lat)]

        # 绘制路线
        lat_lng_points = [[p[1], p[0]] for p in points]
        folium.PolyLine(
            lat_lng_points,
            color=color,
            weight=3,
            opacity=0.8,
            popup=f"路线{idx+1}"
        ).add_to(m)

        # 绘制途经点
        for wp in route.waypoints:
            folium.CircleMarker(
                location=[wp.lat, wp.lng],
                radius=5,
                popup=f"<b>{wp.name}</b><br>热度: {wp.heat_score:.2f}",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7,
                weight=2
            ).add_to(m)

    # 创建输出目录
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    m.save(output_path)
    print(f"\n✓ 地图已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="滴滴司机接单最优路径规划")
    parser.add_argument("--start", type=str, required=True,
                       help="起点（坐标 或 地名，如 '116.39,39.90' 或 '三里屯'）")
    parser.add_argument("--end", type=str, required=True,
                       help="终点（坐标 或 地名，如 '116.46,39.92' 或 '国贸'）")
    parser.add_argument("--city", type=str, default="beijing",
                       help="城市（默认: beijing）")
    parser.add_argument("--output", type=str, default="output/route_plan.html",
                       help="输出地图文件（默认: output/route_plan.html）")
    parser.add_argument("--poi-data", type=str, default="output/poi_heat_weights.json",
                       help="POI数据文件（默认: output/poi_heat_weights.json）")

    args = parser.parse_args()

    print("🗺️  路径规划系统")
    print("=" * 70)

    # 加载配置
    try:
        amap_key, default_city = load_config()
        if args.city:
            city = args.city
        else:
            city = default_city
    except ValueError as e:
        print(f"❌ {e}")
        sys.exit(1)

    # 解析起终点
    print(f"\n📍 解析起点: {args.start}")
    try:
        start = parse_location_input(args.start, city, amap_key)
        print(f"   ✓ {start.name} ({start.lng}, {start.lat})")
    except Exception as e:
        print(f"   ❌ {e}")
        sys.exit(1)

    print(f"\n📍 解析终点: {args.end}")
    try:
        end = parse_location_input(args.end, city, amap_key)
        print(f"   ✓ {end.name} ({end.lng}, {end.lat})")
    except Exception as e:
        print(f"   ❌ {e}")
        sys.exit(1)

    # 加载POI数据
    print(f"\n📊 加载POI数据...")
    pois = load_poi_data(args.poi_data)

    # 规划路线
    print(f"\n🛣️  规划最优路线...")
    routes = plan_three_routes(start, end, pois, amap_key)

    if not routes:
        print("❌ 无法规划路线，请检查输入")
        sys.exit(1)

    # 输出结果
    print(f"\n" + "=" * 70)
    print(f"✅ 成功规划 {len(routes)} 条路线")
    print("=" * 70)

    for idx, route in enumerate(routes, 1):
        print(f"\n【路线{idx}】")
        print(f"  途经点数: {len(route.waypoints)}")
        if route.waypoints:
            print(f"  途经点: {' → '.join([wp.name for wp in route.waypoints])}")
        print(f"  热度总和: {route.heat_score_sum:.2f}")
        print(f"  距离: {route.distance/1000:.2f} km")
        print(f"  时长: {route.duration/60:.0f} 分钟")
        print(f"  接单概率评分 (热度/距离): {route.heat_efficiency:.3f}")

    # 生成地图
    print(f"\n🗺️  生成地图...")
    generate_map(start, end, routes, args.output)

    print(f"\n✨ 完成！在浏览器中打开地图: {args.output}")


if __name__ == "__main__":
    main()
