import os
from dotenv import load_dotenv

load_dotenv()

# ─── API ──────────────────────────────────────────────────────────────────────
AMAP_API_KEY = os.environ.get("AMAP_API_KEY", "")
VOLC_API_KEY = os.environ.get("VOLC_API_KEY", "")

# 路况数据源选择: "amap" | "volcano"
TRAFFIC_PROVIDER = os.environ.get("TRAFFIC_PROVIDER", "amap")

# ─── 城市范围配置 ──────────────────────────────────────────────────────────────
# (min_lng, min_lat, max_lng, max_lat)
CITY_BOUNDS = {
    "shanghai": (121.18, 30.99, 121.78, 31.48),
    "beijing":  (116.10, 39.75, 116.85, 40.18),
    "guangzhou": (113.05, 22.95, 113.70, 23.40),
    "shenzhen": (113.75, 22.44, 114.38, 22.84),
    "chengdu":  (103.88, 30.48, 104.40, 30.82),
}
CITY = os.environ.get("CITY", "shanghai")
BOUNDS = CITY_BOUNDS[CITY]

# ─── 网格分辨率 ────────────────────────────────────────────────────────────────
# 0.01° ≈ 1 km；用于归并道路数据到热力格子
GRID_RESOLUTION = 0.01

# 单次API请求覆盖的矩形边长（度）；太大返回数据量大，太小调用次数多
# 高德路况API单次矩形查询上限约 0.08° lng × 0.06° lat
QUERY_CHUNK_LNG = 0.07
QUERY_CHUNK_LAT = 0.05

# 可选：仅采样城市核心区（节省API配额），None 表示使用完整 BOUNDS
# 北京核心区示例: (116.28, 39.82, 116.62, 40.02)
FOCUS_BOUNDS = None   # type: tuple | None

# ─── 分时段定义 ───────────────────────────────────────────────────────────────
TIME_PERIODS = {
    "morning_peak": {
        "label": "早高峰",
        "hours":  list(range(7, 10)),     # 07:00-09:59
        "color":  "#e74c3c",
    },
    "daytime": {
        "label": "白天",
        "hours":  list(range(10, 17)),    # 10:00-16:59
        "color":  "#f39c12",
    },
    "evening_peak": {
        "label": "晚高峰",
        "hours":  list(range(17, 21)),    # 17:00-20:59
        "color":  "#8e44ad",
    },
}

# 只在以下小时范围内采样（节省API调用）
ACTIVE_HOURS = [h for p in TIME_PERIODS.values() for h in p["hours"]]

# ─── 采样频率 ─────────────────────────────────────────────────────────────────
SAMPLE_INTERVAL_MINUTES = 30   # 每30分钟采一次

# ─── 热力权重：道路拥堵状态 → 接单可能性 ─────────────────────────────────────
# 1=畅通  2=缓行  3=拥堵  4=严重拥堵  0=未知
STATUS_WEIGHTS = {
    "1": 0.25,   # 畅通：路上有车，但司机/乘客都少
    "2": 1.00,   # 缓行：最佳接单时机——乘客多、还能动
    "3": 0.75,   # 拥堵：乘客多，但移动困难
    "4": 0.35,   # 严重拥堵：几乎寸步难行
    "0": 0.10,   # 未知
}

# ─── 路径 ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_DIR   = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
DB_PATH    = os.path.join(DATA_DIR, "traffic.db")

os.makedirs(DATA_DIR,   exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── 数据保留期 ───────────────────────────────────────────────────────────────
DATA_RETENTION_DAYS = 35   # 保留5周数据
