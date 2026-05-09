"""
data_collector.py
─────────────────
调用高德地图「路况矩形查询」接口，把整个城市划分成若干矩形块分批请求，
解析返回的道路矢量，将每条道路的拥堵分映射到 (grid_lng, grid_lat) 网格，
最终写入 SQLite。
"""

import time
import logging
import sqlite3
from datetime import datetime

import config
from traffic_provider import get_provider

logger = logging.getLogger(__name__)


def _to_grid(lng: float, lat: float) -> tuple:
	"""转换坐标到网格坐标"""
	grid_lng = round(lng / config.GRID_RESOLUTION) * config.GRID_RESOLUTION
	grid_lat = round(lat / config.GRID_RESOLUTION) * config.GRID_RESOLUTION
	return (grid_lng, grid_lat)


def _build_grid_chunks():
    """
    把采样范围拆成若干 QUERY_CHUNK_LNG × QUERY_CHUNK_LAT 的矩形块。
    若配置了 FOCUS_BOUNDS 则只采样核心区，否则覆盖全城。
    """
    bounds = config.FOCUS_BOUNDS if config.FOCUS_BOUNDS else config.BOUNDS
    min_lng, min_lat, max_lng, max_lat = bounds
    step_lng = config.QUERY_CHUNK_LNG
    step_lat = config.QUERY_CHUNK_LAT
    chunks = []
    lng = min_lng
    while lng < max_lng:
        lat = min_lat
        while lat < max_lat:
            sw = (round(lng, 6), round(lat, 6))
            ne = (round(min(lng + step_lng, max_lng), 6),
                  round(min(lat + step_lat, max_lat), 6))
            chunks.append((sw, ne))
            lat += step_lat
        lng += step_lng
    return chunks


# ─── 数据库初始化 ──────────────────────────────────────────────────────────────

def init_db():
    """建表（若不存在）。"""
    with sqlite3.connect(config.DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS traffic_samples (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                sampled_at  TEXT    NOT NULL,
                period      TEXT    NOT NULL,
                grid_lng    REAL    NOT NULL,
                grid_lat    REAL    NOT NULL,
                score       REAL    NOT NULL
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_period_time
            ON traffic_samples (period, sampled_at)
        """)
        conn.commit()
    logger.info("数据库已就绪: %s", config.DB_PATH)


def _get_period(hour: int) -> str | None:
    """根据小时返回所属时段 key，不在任何时段则返回 None。"""
    for key, cfg in config.TIME_PERIODS.items():
        if hour in cfg["hours"]:
            return key
    return None


def collect_sample():
    """
    采集一次全城路况快照：
    - 仅在 ACTIVE_HOURS 内执行
    - 使用配置的 Provider（高德或火山引擎）
    - 分块请求 → 聚合 → 写 DB
    """
    now    = datetime.now()
    hour   = now.hour
    period = _get_period(hour)
    if period is None:
        logger.debug("当前 %02d 时不在采样时段，跳过", hour)
        return 0

    try:
        provider = get_provider()
    except ValueError as e:
        logger.error(str(e))
        return 0

    chunks  = _build_grid_chunks()
    all_recs = []
    ts = now.strftime("%Y-%m-%d %H:%M:%S")

    logger.info("[%s] 开始采样 provider=%s period=%s，共 %d 个矩形块",
                ts, config.TRAFFIC_PROVIDER, period, len(chunks))

    for i, (sw, ne) in enumerate(chunks):
        recs = provider.fetch_chunk(sw, ne)
        all_recs.extend(recs)
        # 礼貌延迟，避免触发 QPS 限制
        if i < len(chunks) - 1:
            time.sleep(0.12)

    if not all_recs:
        logger.warning("本次采样未获取到任何数据")
        return 0

    # 合并同网格分数（同一次采样中同一格子取平均）
    from collections import defaultdict
    cell_scores = defaultdict(list)
    for grid_lng, grid_lat, score in all_recs:
        cell_scores[(grid_lng, grid_lat)].append(score)

    rows = [
        (ts, period, glng, glat, sum(sc) / len(sc))
        for (glng, glat), sc in cell_scores.items()
    ]

    with sqlite3.connect(config.DB_PATH) as conn:
        conn.executemany(
            "INSERT INTO traffic_samples (sampled_at, period, grid_lng, grid_lat, score) "
            "VALUES (?, ?, ?, ?, ?)",
            rows
        )
        conn.commit()

    logger.info("采样完成: period=%s，写入 %d 个网格", period, len(rows))
    return len(rows)


def purge_old_data():
    """删除超过 DATA_RETENTION_DAYS 天的历史数据。"""
    cutoff = datetime.now().strftime(
        f"%Y-%m-%d"  # 取日期部分做前缀比较即可
    )
    from datetime import timedelta
    cutoff_dt = (datetime.now() - timedelta(days=config.DATA_RETENTION_DAYS))
    cutoff_str = cutoff_dt.strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(config.DB_PATH) as conn:
        cur = conn.execute(
            "DELETE FROM traffic_samples WHERE sampled_at < ?", (cutoff_str,)
        )
        conn.commit()
    logger.info("已清理 %d 条过期数据（%s 之前）", cur.rowcount, cutoff_str)
