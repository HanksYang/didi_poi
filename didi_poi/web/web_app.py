#!/usr/bin/env python3
import os
import sys
import json
import tempfile
import uuid
import numpy as np
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

try:
    from PIL import Image, ImageEnhance
except ImportError:
    Image = None
    ImageEnhance = None

load_dotenv()

app = Flask(__name__, template_folder='templates')
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

TASK_RESULTS = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png', 'gif'}

def diagnose_heatmap_image(image_path: str) -> dict:
    """
    诊断热力图图像质量
    返回诊断信息和改进建议
    """
    if Image is None:
        return {"can_diagnose": False}

    try:
        img = Image.open(image_path)
        img_array = np.array(img)

        diagnosis = {
            "can_diagnose": True,
            "filename": os.path.basename(image_path),
            "size": f"{img.width}x{img.height}",
            "file_size_mb": round(os.path.getsize(image_path) / (1024*1024), 2),
            "mode": img.mode,
            "issues": [],
            "suggestions": []
        }

        # 检查红色通道（热点区域）
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            red_channel = img_array[:, :, 0]
            red_avg = float(np.mean(red_channel))
            diagnosis["red_channel_avg"] = red_avg

            # 计算热点像素比例
            hot_pixels = (red_channel > 150).sum()
            hot_percentage = (hot_pixels / red_channel.size) * 100
            diagnosis["hot_pixels_percentage"] = round(hot_percentage, 2)

            if hot_percentage < 0.5:
                diagnosis["issues"].append("热点区域不明显（红色像素 < 0.5%）")
                diagnosis["suggestions"].append("✓ 确保上传的是高德地图热力图，红色区域应该明显")
            elif hot_percentage < 2:
                diagnosis["suggestions"].append("✓ 热点区域较小，但可以识别")
            else:
                diagnosis["suggestions"].append("✓ 热点区域明显，有利于识别")

        # 检查对比度
        if len(img_array.shape) == 3:
            gray = np.mean(img_array, axis=2)
        else:
            gray = img_array

        contrast = float(np.std(gray))
        diagnosis["contrast"] = round(contrast, 2)

        if contrast < 20:
            diagnosis["issues"].append("对比度过低（可能是模糊或褪色图像）")
            diagnosis["suggestions"].append("✓ 建议使用高清截图或增强图像对比度")
        elif contrast < 50:
            diagnosis["suggestions"].append("✓ 对比度一般，可以改进")
        else:
            diagnosis["suggestions"].append("✓ 对比度良好，有利于识别")

        # 检查分辨率
        if img.width < 300 or img.height < 300:
            diagnosis["issues"].append("分辨率过低（建议至少 300x300）")
            diagnosis["suggestions"].append("✓ 建议使用高分辨率截图")
        else:
            diagnosis["suggestions"].append("✓ 分辨率足够")

        # 检查文件大小
        file_size_mb = os.path.getsize(image_path) / (1024*1024)
        if file_size_mb > 10:
            diagnosis["issues"].append("文件过大（> 10MB）")
            diagnosis["suggestions"].append("✓ 建议压缩文件大小到 5MB 以下")
        else:
            diagnosis["suggestions"].append("✓ 文件大小合适")

        return diagnosis
    except Exception as e:
        return {
            "can_diagnose": False,
            "error": str(e)
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "只支持 JPG/PNG/GIF 格式"}), 400

        filename = secure_filename(file.filename)
        temp_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(file_path)

        job_id = str(uuid.uuid4())

        # 诊断上传的图像
        diagnosis = diagnose_heatmap_image(file_path)

        # 如果有严重问题，返回诊断信息
        if diagnosis.get("can_diagnose") and diagnosis.get("issues"):
            result = {
                "success": False,
                "job_id": job_id,
                "error": "图像质量检测到问题",
                "diagnosis": diagnosis,
                "detail": "系统检测到以下问题：\n" + "\n".join(diagnosis["issues"]) + "\n\n改进建议：\n" + "\n".join(diagnosis["suggestions"])
            }
            TASK_RESULTS[job_id] = result
            try:
                os.remove(file_path)
            except:
                pass
            return jsonify(result), 400

        # 模拟成功识别
        result = {
            "success": True,
            "job_id": job_id,
            "inserted": 45,
            "updated_pois": 12,
            "places_count": 15,
            "period": request.form.get('period', 'auto'),
            "sigma_km": float(request.form.get('sigma', 3.0)),
            "heat_center": {
                "name": "系统识别的热度中心",
                "lng": 116.4,
                "lat": 39.9
            },
            "diagnosis": diagnosis,
            "timestamp": datetime.now().isoformat()
        }

        TASK_RESULTS[job_id] = result

        try:
            os.remove(file_path)
        except:
            pass

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/diagnose', methods=['POST'])
def diagnose_image():
    """诊断上传的图像质量（无需处理，仅获取诊断信息）"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "没有上传文件"}), 400

        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "只支持 JPG/PNG/GIF 格式"}), 400

        # 临时保存文件
        filename = secure_filename(file.filename)
        temp_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        file.save(file_path)

        # 诊断
        diagnosis = diagnose_heatmap_image(file_path)

        # 清理
        try:
            os.remove(file_path)
        except:
            pass

        return jsonify({
            "success": True,
            "diagnosis": diagnosis
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/result/<job_id>', methods=['GET'])
def get_result(job_id):
    if job_id not in TASK_RESULTS:
        return jsonify({"error": "任务不存在"}), 404
    return jsonify(TASK_RESULTS[job_id]), 200

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "running",
        "version": "1.0",
        "timestamp": datetime.now().isoformat(),
        "tasks_completed": len(TASK_RESULTS)
    }), 200

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        "amap_key": os.getenv("AMAP_API_KEY", ""),
        "volc_key": os.getenv("VOLC_API_KEY", "")
    }), 200

@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        amap_key = data.get('amap_key', '').strip()
        volc_key = data.get('volc_key', '').strip()

        if not amap_key or not volc_key:
            return jsonify({"success": False, "error": "缺少必要的 API Key"}), 400

        os.environ['AMAP_API_KEY'] = amap_key
        os.environ['VOLC_API_KEY'] = volc_key

        env_path = '.env'
        lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()

        found_amap = False
        found_volc = False
        for i, line in enumerate(lines):
            if line.startswith('AMAP_API_KEY='):
                lines[i] = f'AMAP_API_KEY={amap_key}\n'
                found_amap = True
            elif line.startswith('VOLC_API_KEY='):
                lines[i] = f'VOLC_API_KEY={volc_key}\n'
                found_volc = True

        if not found_amap:
            lines.append(f'AMAP_API_KEY={amap_key}\n')
        if not found_volc:
            lines.append(f'VOLC_API_KEY={volc_key}\n')

        with open(env_path, 'w') as f:
            f.writelines(lines)

        return jsonify({
            "success": True,
            "message": "API 配置已保存"
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/pois', methods=['GET'])
def get_pois():
    try:
        json_path = request.args.get('json_path', 'output/poi_heat_weights.json')

        if not os.path.exists(json_path):
            return jsonify({"pois": []}), 200

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        pois = data.get('poi_list', [])
        result = [
            {
                "name": poi.get("name", ""),
                "lng": poi.get("lng", 0),
                "lat": poi.get("lat", 0),
                "heat_score": poi.get("heat_score", 0)
            }
            for poi in pois if poi.get("name")
        ]

        return jsonify({"pois": result}), 200
    except Exception as e:
        return jsonify({"error": str(e), "pois": []}), 500

@app.route('/api/route/plan', methods=['POST'])
def plan_route():
    try:
        data = request.get_json()
        start_name = data.get('start', '').strip()
        end_name = data.get('end', '').strip()
        city = data.get('city', 'beijing')

        if not start_name or not end_name:
            return jsonify({"success": False, "error": "起点和终点不能为空"}), 400

        # 模拟三条路线
        routes = [
            {
                "id": 1,
                "heat_score_sum": 3.58,
                "distance": 4750.0,
                "duration": 1020,
                "heat_efficiency": 0.754,
                "waypoints": [
                    {"name": "国贸中心", "heat_score": 0.95},
                    {"name": "朝阳门", "heat_score": 0.87}
                ]
            },
            {
                "id": 2,
                "heat_score_sum": 3.22,
                "distance": 5200.0,
                "duration": 1140,
                "heat_efficiency": 0.618,
                "waypoints": [
                    {"name": "建国门", "heat_score": 0.82},
                    {"name": "崇文门", "heat_score": 0.76}
                ]
            },
            {
                "id": 3,
                "heat_score_sum": 2.95,
                "distance": 4500.0,
                "duration": 900,
                "heat_efficiency": 0.656,
                "waypoints": [
                    {"name": "天安门", "heat_score": 0.91},
                    {"name": "前门", "heat_score": 0.68}
                ]
            }
        ]

        return jsonify({
            "success": True,
            "routes": routes,
            "map_url": "/output/route_plan.html",
            "start_name": start_name,
            "end_name": end_name,
            "city": city
        }), 200

    except Exception as e:
        return jsonify({"success": False, "error": f"服务器错误: {str(e)}"}), 500

@app.route('/output/<filename>', methods=['GET'])
def get_output_file(filename):
    try:
        return send_from_directory('output', filename)
    except Exception as e:
        return jsonify({"error": "文件不存在"}), 404

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "找不到资源"}), 404

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
