#!/usr/bin/env python3
"""
DiDi POI 热点系统 - 启动脚本
运行后自动打开浏览器并启动 Flask 应用
"""
import os
import sys
import webbrowser
from pathlib import Path
import time

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置工作目录
os.chdir(BASE_DIR)

# 添加 web 目录到 Python 路径
sys.path.insert(0, os.path.join(BASE_DIR, 'web'))

# 导入 Flask 应用
from web_app import app

def main():
    """启动 Web 服务器并打开浏览器"""
    host = '127.0.0.1'
    port = 5000

    print("\n" + "="*60)
    print("🚀 DiDi 司机热点系统启动中...")
    print("="*60)
    print(f"📍 服务地址: http://{host}:{port}")
    print("💡 如浏览器未自动打开，请访问上面的地址")
    print("❌ 按 Ctrl+C 停止服务")
    print("="*60 + "\n")

    # 等待后自动打开浏览器
    def open_browser():
        time.sleep(1.5)
        try:
            webbrowser.open(f'http://{host}:{port}')
            print("🌐 浏览器已打开")
        except:
            print("⚠️  浏览器未能自动打开，请手动访问上面的地址")

    import threading
    thread = threading.Thread(target=open_browser, daemon=True)
    thread.start()

    try:
        app.run(host=host, port=port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n👋 已关闭服务")
        sys.exit(0)

if __name__ == '__main__':
    main()
