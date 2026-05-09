#!/usr/bin/env python3
"""
图像预处理脚本 - 确保大模型能准确识别热力图
"""
from PIL import Image
import numpy as np
import os

def enhance_heatmap_image(image_path: str, output_path: str = None) -> str:
    """
    增强热力图以便大模型识别
    
    优化：
    1. 增加图片对比度
    2. 自动调整亮度
    3. 清晰化文字标签
    4. 增强颜色饱和度（特别是红色区域）
    """
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # 1. 增加对比度
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)  # 增加50%对比度
    
    # 2. 增加饱和度
    enhancer = ImageEnhance.Color(img)
    img = enhancer.enhance(1.3)  # 增加30%饱和度
    
    # 3. 锐化
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)
    
    # 4. 调整亮度
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.1)
    
    if output_path is None:
        output_path = image_path.replace('.jpg', '_enhanced.jpg').replace('.png', '_enhanced.png')
    
    img.save(output_path, quality=95)
    print(f"✓ 图像增强完成: {output_path}")
    return output_path

def validate_heatmap(image_path: str) -> dict:
    """
    验证热力图的识别能力
    返回诊断信息
    """
    img = Image.open(image_path)
    img_array = np.array(img)
    
    info = {
        "file": os.path.basename(image_path),
        "size": img.size,
        "mode": img.mode,
        "file_size_mb": os.path.getsize(image_path) / (1024*1024),
        "red_channel_avg": None,
        "contrast_score": None,
        "recommendations": []
    }
    
    # 分析红色通道
    if len(img_array.shape) == 3:
        red_channel = img_array[:, :, 0]
        info["red_channel_avg"] = float(np.mean(red_channel))
        
        # 检查热度区域
        hot_pixels = (red_channel > 150).sum()
        info["hot_pixels_percentage"] = float((hot_pixels / red_channel.size) * 100)
        
        if info["hot_pixels_percentage"] < 1:
            info["recommendations"].append("⚠️  热点区域较少，确保热力图的红色区域明显")
    
    # 计算对比度
    if len(img_array.shape) == 3:
        gray = np.mean(img_array, axis=2)
    else:
        gray = img_array
    
    contrast = np.std(gray)
    info["contrast_score"] = float(contrast)
    
    if contrast < 30:
        info["recommendations"].append("⚠️  对比度较低，建议先运行 enhance_heatmap_image() 增强图像")
    
    if info["file_size_mb"] > 5:
        info["recommendations"].append("⚠️  文件过大，建议压缩到 5MB 以下")
    
    if info["size"][0] < 300 or info["size"][1] < 300:
        info["recommendations"].append("⚠️  分辨率较低，建议使用高清图片（至少 300x300）")
    
    return info

if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("用法: python3 improve_image_recognition.py <图片路径> [--enhance] [--validate]")
        print("\n示例:")
        print("  # 验证图片")
        print("  python3 improve_image_recognition.py /path/to/heatmap.jpg --validate")
        print("\n  # 增强图片")
        print("  python3 improve_image_recognition.py /path/to/heatmap.jpg --enhance")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"❌ 文件不存在: {image_path}")
        sys.exit(1)
    
    if '--validate' in sys.argv:
        info = validate_heatmap(image_path)
        print("\n📊 图像诊断报告:")
        print(json.dumps(info, indent=2, ensure_ascii=False))
    
    if '--enhance' in sys.argv:
        enhanced_path = enhance_heatmap_image(image_path)
        print(f"\n验证增强后的图像:")
        info = validate_heatmap(enhanced_path)
        print(json.dumps(info, indent=2, ensure_ascii=False))
