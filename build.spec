# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 配置文件：将 DiDi POI 热点系统打包成可执行文件
"""
import os

a = Analysis(
    ['run_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('web/templates', 'web/templates'),
        ('src', 'src'),
        ('web', 'web'),
        ('data', 'data'),
        ('output', 'output'),
        ('.env', '.'),
        ('.env.example', '.'),
    ],
    hiddenimports=[
        'flask',
        'werkzeug',
        'jinja2',
        'click',
        'itsdangerous',
        'markupsafe',
        'flask.json',
        'flask.templating',
        'folium',
        'folium.plugins',
        'branca',
        'branca.element',
        'requests',
        'urllib3',
        'certifi',
        'charset_normalizer',
        'idna',
        'PIL',
        'numpy',
        'pandas',
        'src.route_planner',
        'src.traffic_provider',
        'src.data_collector',
        'src.heatmap_uploader',
        'src.llm_client',
        'src.config',
        'dotenv',
        'web.web_app',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DiDi_POI热点系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
