#!/usr/bin/env python3
"""
热度图上传 & 权重自动更新系统
功能：上传热力图 → Claude Vision识别地点 → 高斯衰减计算权重 → 写入SQLite + JSON
"""

import os
import sys
import json
import math
import base64
import sqlite3
import argparse
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

import numpy as np
from PIL import Image
import requests

# 导入现有项目的模块
from .data_collector import _to_grid
from . import config
from .llm_client import LLMClient


@dataclass
class Place:
    """地点"""
    name: str
    lng: float
    lat: float
    heat_score: float = 0.0
    description: str = ""


@dataclass
class HeatCenter:
    """热度中心"""
    lng: float
    lat: float
    name: str = "热度中心"
    confidence: float = 0.0


def find_heat_center_pixel(image_path: str) -> Tuple[float, float, float]:
    """
    从图像中找热度最高的像素质心（基于红色通道）
    返回: (center_x, center_y, radius_px)
    """
    img = Image.open(image_path)
    img_array = np.array(img)

    # 提取红色通道
    if len(img_array.shape) == 3:
        red_channel = img_array[:, :, 0]
    else:
        red_channel = img_array

    # 找红色值 > 150 的像素
    hot_pixels = red_channel > 150

    if not np.any(hot_pixels):
        print("⚠️  未检测到明显的热度区域（红色），使用图像中心")
        return img_array.shape[1] / 2, img_array.shape[0] / 2, 50.0

    # 计算热点区域的质心
    hot_coords = np.argwhere(hot_pixels)  # (y, x)
    center_y = np.mean(hot_coords[:, 0])
    center_x = np.mean(hot_coords[:, 1])

    # 计算热点区域的"半径"（标准差）
    radius = np.std(hot_coords) if len(hot_coords) > 1 else 50.0

    print(f"✓ 检测到热度中心: ({center_x:.0f}, {center_y:.0f}), 热点半径: {radius:.0f}px")
    return float(center_x), float(center_y), float(radius)


def encode_image_to_base64(image_path: str) -> str:
    """图片转 base64"""
    with open(image_path, "rb") as img_file:
        return base64.standard_b64encode(img_file.read()).decode("utf-8")


def analyze_with_claude(image_path: str, heat_center_pixel: Tuple[float, float],
                       api_key: str = None) -> Dict:
    """
    调用大模型 Vision 识别图中的地点和热度中心地理坐标
    返回 {"heat_center": {...}, "places": [...]}
    """
    img_b64 = encode_image_to_base64(image_path)

    center_x, center_y = heat_center_pixel[:2]

    system_prompt = """你是地图识别专家。我会给你一张滴滴接单热力图（通常是高德地图截图）。

你需要完成以下任务：
1. 识别图中最红（热度最高）的中心区域，这是接单热点中心
2. 根据这个红色中心的位置和周围的地名、建筑、地标，推算其所在的经纬度
3. 识别图中能看到的所有重要地点、地标、街道、商业区的名称
4. 为每个地点估算经纬度（基于图的地理位置和相对位置）

返回严格的JSON格式，包含：
{
  "heat_center": {
    "lng": 116.39,
    "lat": 39.90,
    "name": "热度中心区域的描述",
    "confidence": 0.85
  },
  "places": [
    {"name": "地点名称", "lng": 116.40, "lat": 39.91},
    ...
  ]
}

关键提示：
- 热度中心的像素坐标约为 (""" + f"{center_x:.0f}" + """, """ + f"{center_y:.0f}" + """)
- 这有助于你定位热度中心在地图上的确切位置
- 返回的坐标应该在北京范围内 (lng: 116.1~116.85, lat: 39.75~40.18)
- 只返回JSON，不要有其他文本"""

    user_prompt = """请分析这张热力图，返回JSON格式的识别结果。"""

    try:
        llm = LLMClient()
        print(f"   使用 LLM Provider: {llm.provider}")
        response_text = llm.chat_with_image(system_prompt, user_prompt, img_b64).strip()
    except Exception as e:
        print(f"❌ LLM 调用失败: {e}")
        print(f"   请检查:")
        print(f"   1. LLM_API_KEY 是否正确设置在 .env 文件中")
        print(f"   2. LLM_PROVIDER 是否设置为正确的提供商 (doubao 或 anthropic)")
        print(f"   3. 网络连接是否正常")
        raise ValueError(f"大模型识别失败: {str(e)}")

    # 清理Markdown包装
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    try:
        result = json.loads(response_text)
        print(f"✓ 模型识别了热度中心 & {len(result.get('places', []))} 个地点")
        return result
    except json.JSONDecodeError as e:
        print(f"❌ 模型返回的JSON解析失败: {e}")
        print(f"   原始响应: {response_text[:200]}")
        raise ValueError(f"模型返回格式错误: {str(e)}")


def haversine_distance(lng1: float, lat1: float, lng2: float, lat2: float) -> float:
    """计算两点距离（km）"""
    R = 6371  # 地球半径（km）
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlng / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


def compute_gaussian_weights(places: List[Dict], heat_center: Dict,
                            sigma_km: float = 3.0) -> List[Place]:
    """
    高斯衰减：计算每个地点到热度中心的权重
    weight = exp(-d² / (2 * σ²))
    """
    weighted_places = []

    heat_lng = heat_center["lng"]
    heat_lat = heat_center["lat"]

    for place_data in places:
        name = place_data.get("name", "")
        lng = place_data.get("lng", 0)
        lat = place_data.get("lat", 0)

        if not name or lng == 0 or lat == 0:
            continue

        # 计算距离
        dist_km = haversine_distance(heat_lng, heat_lat, lng, lat)

        # 高斯衰减公式
        sigma_sq = sigma_km ** 2
        weight = math.exp(-dist_km ** 2 / (2 * sigma_sq))

        # 归一化到 [0.1, 1.0]（兼容现有score范围）
        heat_score = max(0.1, min(1.0, weight))

        place = Place(
            name=name,
            lng=lng,
            lat=lat,
            heat_score=heat_score,
            description=place_data.get("description", "")
        )
        weighted_places.append(place)

    # 按热度排序
    weighted_places.sort(key=lambda p: p.heat_score, reverse=True)

    print(f"✓ 计算权重完成：{len(weighted_places)} 个地点，σ={sigma_km}km")
    if weighted_places:
        print(f"   Top3: {', '.join([f'{p.name}({p.heat_score:.2f})' for p in weighted_places[:3]])}")

    return weighted_places


def infer_period() -> str:
    """根据当前时间推断时段"""
    h = datetime.now().hour
    if 7 <= h < 9:
        return "morning_peak"
    elif 10 <= h < 16:
        return "daytime"
    elif 17 <= h < 20:
        return "evening_peak"
    else:
        return "daytime"


def write_to_sqlite(weighted_places: List[Place], period: str,
                   db_path: str, sampled_at: Optional[str] = None) -> int:
    """
    将加权地点写入 SQLite
    返回插入的行数
    """
    if not weighted_places:
        print("⚠️  没有地点数据需要写入")
        return 0

    if sampled_at is None:
        sampled_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 确保数据库表存在
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS traffic_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sampled_at TEXT NOT NULL,
                period TEXT NOT NULL,
                grid_lng REAL NOT NULL,
                grid_lat REAL NOT NULL,
                score REAL NOT NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_period_time ON traffic_samples (period, sampled_at)")
        conn.commit()
    except Exception as e:
        print(f"⚠️  表创建/检查出错: {e}")

    # 批量插入
    rows = []
    for place in weighted_places:
        grid_lng, grid_lat = _to_grid(place.lng, place.lat)
        rows.append((sampled_at, period, grid_lng, grid_lat, place.heat_score))

    try:
        cursor.executemany(
            "INSERT INTO traffic_samples (sampled_at, period, grid_lng, grid_lat, score) VALUES (?, ?, ?, ?, ?)",
            rows
        )
        conn.commit()
        inserted = cursor.rowcount
        print(f"✓ 写入SQLite成功：{inserted}条记录，period={period}")
        return inserted
    except Exception as e:
        print(f"❌ 写入SQLite失败: {e}")
        return 0
    finally:
        conn.close()


def match_place_to_poi(place: Place, pois: List[Dict]) -> Optional[int]:
    """
    匹配地点到POI，返回POI的索引
    优先级：名称匹配 > 距离匹配 (< 500m)
    """
    # 1. 名称匹配（模糊）
    place_name_lower = place.name.lower()
    for idx, poi in enumerate(pois):
        poi_name = poi.get("name", "").lower()
        if place_name_lower in poi_name or poi_name in place_name_lower:
            return idx

    # 2. 距离匹配 (< 500m)
    for idx, poi in enumerate(pois):
        poi_lng = poi.get("lng", 0)
        poi_lat = poi.get("lat", 0)
        if poi_lng and poi_lat:
            dist_km = haversine_distance(place.lng, place.lat, poi_lng, poi_lat)
            if dist_km < 0.5:  # 500m
                return idx

    return None


def update_poi_json(weighted_places: List[Place], json_path: str) -> Dict:
    """
    更新 POI JSON 文件中的热度分数
    返回 {"updated": int, "poi_list": [...]}
    """
    if not os.path.exists(json_path):
        print(f"⚠️  POI JSON 不存在: {json_path}，创建新文件")
        pois = []
    else:
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            pois = data.get("poi_list", [])
        except Exception as e:
            print(f"❌ 读取POI JSON失败: {e}")
            pois = []

    updated_count = 0
    updated_pois = []

    for place in weighted_places:
        poi_idx = match_place_to_poi(place, pois)
        if poi_idx is not None:
            old_score = pois[poi_idx].get("heat_score", 0)
            pois[poi_idx]["heat_score"] = place.heat_score
            updated_count += 1
            updated_pois.append({
                "name": place.name,
                "old_score": old_score,
                "new_score": place.heat_score,
                "idx": poi_idx
            })

    # 重新排序 rank
    pois.sort(key=lambda p: p.get("heat_score", 0), reverse=True)
    for idx, poi in enumerate(pois, 1):
        poi["rank"] = idx

    # 写回文件
    try:
        Path(json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"poi_list": pois}, f, ensure_ascii=False, indent=2)
        print(f"✓ 更新POI JSON成功：{updated_count}个POI")
        return {"updated": updated_count, "poi_list": pois, "details": updated_pois}
    except Exception as e:
        print(f"❌ 写入POI JSON失败: {e}")
        return {"updated": 0, "poi_list": pois, "details": []}


def run_pipeline(image_path: str, period: str = "auto", sigma_km: float = 3.0,
                db_path: str = "data/traffic.db",
                json_path: str = "output/poi_heat_weights.json",
                api_key: str = None) -> Dict:
    """
    完整流程：分析 → Vision → 权重 → 写入
    """
    print("\n" + "="*70)
    print("🔄 热度图上传管道启动")
    print("="*70)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"图片文件不存在: {image_path}")

    if period == "auto":
        period = infer_period()
        print(f"⏰ 自动推断时段: {period}")

    # Step 1: 找热度中心（像素）
    print("\n[Step 1/5] 像素分析...")
    center_px, center_py, radius_px = find_heat_center_pixel(image_path)

    # Step 2: Vision 识别
    print("\n[Step 2/5] Vision 识别...")
    claude_result = analyze_with_claude(image_path, (center_px, center_py))

    heat_center = claude_result.get("heat_center", {})
    places = claude_result.get("places", [])

    if not heat_center:
        raise ValueError("Claude未能识别热度中心")

    print(f"   热度中心: {heat_center.get('name')} ({heat_center['lng']}, {heat_center['lat']})")

    # Step 3: 高斯衰减计算权重
    print("\n[Step 3/5] 高斯衰减权重计算...")
    weighted_places = compute_gaussian_weights(places, heat_center, sigma_km)

    if not weighted_places:
        print("❌ 没有有效地点")
        error_detail = "模型无法识别图中的地点。可能原因：\n1. 图片不是有效的高德地图热力图\n2. 图片中没有清晰的地名或地标\n3. 热度中心无法准确定位"
        return {"success": False, "error": "模型未能识别到足够的地点信息", "detail": error_detail}

    # Step 4: 写入 SQLite
    print("\n[Step 4/5] 写入SQLite...")
    inserted = write_to_sqlite(weighted_places, period, db_path)

    # Step 5: 更新 POI JSON
    print("\n[Step 5/5] 更新POI热度JSON...")
    json_result = update_poi_json(weighted_places, json_path)

    # 结果总结
    print("\n" + "="*70)
    print("✅ 热度图上传完成！")
    print("="*70)
    print(f"SQLite 写入: {inserted} 条记录 (period={period})")
    print(f"POI JSON 更新: {json_result['updated']} 个POI")

    if json_result['details']:
        print("\n📊 Top 5 更新的POI:")
        for detail in json_result['details'][:5]:
            print(f"   {detail['name']}: {detail['old_score']:.2f} → {detail['new_score']:.2f}")

    return {
        "success": True,
        "inserted": inserted,
        "updated_pois": json_result["updated"],
        "heat_center": heat_center,
        "places_count": len(weighted_places),
        "period": period,
        "sigma_km": sigma_km,
    }


def main():
    parser = argparse.ArgumentParser(description="热度图上传 & 权重自动更新")
    parser.add_argument("--image", type=str, required=True, help="热力图路径")
    parser.add_argument("--period", type=str, default="auto",
                       choices=["morning_peak", "daytime", "evening_peak", "auto"],
                       help="时段(auto为自动推断)")
    parser.add_argument("--sigma", type=float, default=3.0, help="高斯衰减半径(km)")
    parser.add_argument("--db", type=str, default="data/traffic.db", help="SQLite数据库路径")
    parser.add_argument("--poi-json", type=str, default="output/poi_heat_weights.json",
                       help="POI热度JSON路径")

    args = parser.parse_args()

    try:
        result = run_pipeline(
            image_path=args.image,
            period=args.period,
            sigma_km=args.sigma,
            db_path=args.db,
            json_path=args.poi_json
        )
        sys.exit(0 if result.get("success") else 1)
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
