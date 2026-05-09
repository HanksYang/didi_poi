#!/usr/bin/env python3
"""
POI 热度权重生成器
基于滴滴接单热力图，使用 Claude Vision API 分析并生成北京top100 POI的热度权重。
"""

import os
import sys
import json
import csv
import base64
import argparse
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import numpy as np
from llm_client import LLMClient


def load_config():
    """加载环境配置"""
    load_dotenv()
    try:
        client = LLMClient()
        return True
    except ValueError as e:
        raise ValueError(f"LLM配置错误: {e}")


def extract_heatmap_summary(image_path: str) -> dict:
    """
    分析热力图像素，提取热度概要。
    返回: {
        "red_intensity_distribution": str,  # 热度分布描述
        "image_size": (width, height),
        "hot_zones_count": int,
    }
    """
    image = Image.open(image_path)
    img_array = np.array(image)

    if len(img_array.shape) == 3:
        red_channel = img_array[:, :, 0]
    else:
        red_channel = img_array

    # 分析红色分布
    red_mean = float(np.mean(red_channel))
    red_max = float(np.max(red_channel))
    red_min = float(np.min(red_channel))

    # 计算热度区域（红色值 > 150）
    hot_pixels = np.sum(red_channel > 150)
    hot_percentage = (hot_pixels / red_channel.size) * 100 if red_channel.size > 0 else 0

    return {
        "red_intensity_mean": red_mean,
        "red_intensity_max": red_max,
        "red_intensity_min": red_min,
        "hot_percentage": hot_percentage,
        "image_size": image.size,
    }


def encode_image_to_base64(image_path: str) -> str:
    """将图片编码为 base64"""
    with open(image_path, "rb") as image_file:
        return base64.standard_b64encode(image_file.read()).decode("utf-8")


def analyze_heatmap_with_claude(image_path: str, heatmap_summary: dict) -> list:
    """
    使用大模型 Vision API 分析热力图，返回 POI 列表。
    """
    image_base64 = encode_image_to_base64(image_path)

    system_prompt = """你是北京城市地理专家和出行数据分析师。
我会给你一张北京的滴滴接单热力图（红色越深表示接单密度越高）。
请分析图中的热度分布，结合你对北京POI的了解，生成TOP100的POI列表。

每个POI需要包含以下字段：
- rank: 排名 (1-100)
- name: POI名称
- district: 区县（如朝阳区、西城区等）
- category: POI类别（如"地铁站"、"购物中心"、"办公楼"等）
- lng: 经度 (约116.1-116.9)
- lat: 纬度 (约39.75-40.2)
- heat_score: 热度分数 (0-1，基于该POI对应区域在热力图中的红色强度)

重要提示：
1. 返回ONLY纯JSON，不要有任何其他文本
2. 使用严格的JSON格式
3. heat_score 应该基于POI在热力图中的位置和该位置的红色强度
4. 确保返回正好100个POI
5. 按热度从高到低排序

JSON格式示例：
{"poi_list": [{"rank": 1, "name": "天安门广场", "district": "西城区", "category": "景点", "lng": 116.3974, "lat": 39.9075, "heat_score": 0.95}, ...]}
"""

    user_prompt = f"""请分析这张北京滴滴接单热力图。
图片统计信息：
- 热度强度均值: {heatmap_summary.get('red_intensity_mean', 0):.1f}
- 热度最大值: {heatmap_summary.get('red_intensity_max', 0):.1f}
- 热点覆盖比例: {heatmap_summary.get('hot_percentage', 0):.1f}%

请识别热力图中的高热度区域，并结合你对北京的了解，生成TOP100 POI列表。
返回纯JSON格式，包含100个POI条目，按热度从高到低排序。"""

    llm = LLMClient()
    response_text = llm.chat_with_image(system_prompt, user_prompt, image_base64).strip()

    # 清理响应文本（移除可能的markdown包装）
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    if response_text.startswith("```"):
        response_text = response_text[3:]
    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    result = json.loads(response_text)
    return result.get("poi_list", [])


def save_results(poi_list: list, output_dir: str = "output"):
    """保存POI结果为 JSON 和 CSV"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # 保存 JSON
    json_file = output_path / "poi_heat_weights.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump({"poi_list": poi_list}, f, ensure_ascii=False, indent=2)
    print(f"✓ JSON 文件已保存: {json_file}")

    # 保存 CSV
    csv_file = output_path / "poi_heat_weights.csv"
    if poi_list:
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["rank", "name", "district", "category", "lng", "lat", "heat_score"])
            writer.writeheader()
            writer.writerows(poi_list)
        print(f"✓ CSV 文件已保存: {csv_file}")

    return json_file, csv_file


def main():
    parser = argparse.ArgumentParser(description="基于热力图生成POI热度权重")
    parser.add_argument("--image", type=str, required=True, help="热力图图片路径")
    parser.add_argument("--output", type=str, default="output", help="输出目录（默认: output）")
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"❌ 图片文件不存在: {args.image}")
        sys.exit(1)

    print(f"📊 开始分析热力图: {args.image}")

    # 加载配置
    try:
        load_config()
    except ValueError as e:
        print(f"❌ 配置错误: {e}")
        print("请在 .env 中配置 LLM_API_KEY")
        sys.exit(1)

    # 分析热力图
    print("🔍 正在提取热力图特征...")
    heatmap_summary = extract_heatmap_summary(args.image)
    print(f"   热度强度均值: {heatmap_summary['red_intensity_mean']:.1f}")
    print(f"   热度最大值: {heatmap_summary['red_intensity_max']:.1f}")
    print(f"   热点覆盖比例: {heatmap_summary['hot_percentage']:.1f}%")

    # 调用大模型 Vision API
    print("🤖 调用大模型 Vision API 分析...")
    try:
        poi_list = analyze_heatmap_with_claude(args.image, heatmap_summary)
        print(f"✓ 成功识别 {len(poi_list)} 个 POI")
    except json.JSONDecodeError as e:
        print(f"❌ API 返回的JSON解析失败: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Claude API 调用失败: {e}")
        sys.exit(1)

    # 保存结果
    print("💾 正在保存结果...")
    json_file, csv_file = save_results(poi_list, args.output)

    # 显示前10个POI
    print("\n📍 Top 10 热度 POI:")
    print("=" * 80)
    for poi in poi_list[:10]:
        print(f"{poi['rank']:3d}. {poi['name']:20s} | {poi['district']:10s} | "
              f"{poi['category']:12s} | 热度:{poi['heat_score']:.2f}")

    print("\n✅ 分析完成！")
    print(f"   JSON: {json_file}")
    print(f"   CSV:  {csv_file}")


if __name__ == "__main__":
    main()
