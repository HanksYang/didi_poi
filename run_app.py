#!/usr/bin/env python3
import os
import sys
import time
import threading
import webbrowser

# 处理 PyInstaller 打包后的路径
if getattr(sys, 'frozen', False):
    # 运行在 PyInstaller 打包的可执行文件中
    base_dir = sys._MEIPASS
else:
    # 运行在开发环境中
    base_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, base_dir)
os.chdir(base_dir)

from web.web_app import app

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000')

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 5000

    thread = threading.Thread(target=open_browser, daemon=True)
    thread.start()

    print(f"启动应用: http://{host}:{port}")
    app.run(host=host, port=port, debug=False)
