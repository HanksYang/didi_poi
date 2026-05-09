"""
data_processor.py
─────────────────
从 SQLite 读取原始采样，按时段聚合成「周热力权重」DataFrame，
供 heatmap_generator 使用。
"""

import sqlite3
import logging
import time
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import requests

import config

logger = logging.getLogger(__name__)


def load_week_data(period: str, weeks_back: int = 1) -> pd.DataFrame:
    """
    读取最近 N 周的某时段数据，返回聚合后的 DataFrame：
      columns: [grid_lng, grid_lat, score, sample_count]

    Parameters
    ----------
    period    : TIME_PERIODS 中的 key，如 "morning_peak"
    weeks_back: 取最近几周（默认 1，即过去7天）
    """
    cutoff = (datetime.now() - timedelta(weeks=weeks_back)).strftime("%Y-%m-%d %H:%M:%S")

    with sqlite3.connect(config.DB_PATH) as conn:
        df = pd.read_sql_query(
            """
            SELECT grid_lng, grid_lat, score
            FROM   traffic_samples
            WHERE  period = ?
              AND  sampled_at >= ?
            """,
            conn,
            params=(period, cutoff),
        )

    if df.empty:
        logger.warning("period=%s 在最近 %d 周内无数据", period, weeks_back)
        return pd.DataFrame(columns=["grid_lng", "grid_lat", "score", "sample_count"])

    # 按网格聚合：均值 + 样本数
    agg = (
        df.groupby(["grid_lng", "grid_lat"])["score"]
        .agg(score="mean", sample_count="count")
        .reset_index()
    )

    # 归一化到 [0, 1]
    s_min, s_max = agg["score"].min(), agg["score"].max()
    if s_max > s_min:
        agg["score_norm"] = (agg["score"] - s_min) / (s_max - s_min)
    else:
        agg["score_norm"] = 1.0

    # 过滤低可信格子（样本数太少的噪声点）
    # 至少需要 1 次采样；有足够历史数据后阈值会自动提高
    threshold = agg["sample_count"].quantile(0.1)
    agg = agg[agg["sample_count"] >= max(threshold, 1)].copy()

    logger.info("period=%s 聚合完成: %d 个网格，覆盖 %d 个原始样本",
                period, len(agg), df.shape[0])
    return agg


def get_top_hotspots(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """
    返回得分最高的 top_n 个网格（作为推荐停靠点标注）。
    中心点坐标 = 网格左下角 + 半个格子宽度。
    """
    if df.empty:
        return df
    half = config.GRID_RESOLUTION / 2
    top = df.nlargest(top_n, "score_norm").copy()
    top["center_lng"] = top["grid_lng"] + half
    top["center_lat"] = top["grid_lat"] + half
    return top


def _regeocode(lng: float, lat: float) -> str:
    """调用高德逆地理编码，返回可读地址；失败时返回坐标字符串。"""
    if not config.AMAP_API_KEY:
        return f"{lng:.4f},{lat:.4f}"
    try:
        resp = requests.get(
            "https://restapi.amap.com/v3/geocode/regeo",
            params={
                "key":        config.AMAP_API_KEY,
                "location":   f"{lng},{lat}",
                "radius":     300,
                "extensions": "base",
                "roadlevel":  0,
            },
            timeout=6,
        )
        data = resp.json()
        if data.get("status") == "1":
            addr = data["regeocode"].get("formatted_address", "")
            # 去掉省/直辖市前缀，保留城市及以下
            for prefix in ("北京市", "上海市", "广州市", "深圳市", "成都市"):
                addr = addr.replace(prefix, "").strip()
            return addr or f"{lng:.4f},{lat:.4f}"
    except Exception:
        pass
    return f"{lng:.4f},{lat:.4f}"


def get_top30_with_address(all_data: dict, top_n: int = 30) -> list[dict]:
    """
    跨时段合并，取综合得分最高的 top_n 个网格，
    调用逆地理编码返回地址，最终返回可直接渲染的字典列表：
    [{rank, address, morning, daytime, evening, max_score}, ...]
    """
    half = config.GRID_RESOLUTION / 2

    # 先把三个时段分别转成 {(glng,glat): score_norm} 字典
    period_maps = {}
    for key, df in all_data.items():
        if df.empty:
            period_maps[key] = {}
        else:
            period_maps[key] = {
                (row.grid_lng, row.grid_lat): row.score_norm
                for row in df.itertuples()
            }

    # 合并所有出现过的格子，综合得分取各时段均值
    all_cells = set()
    for pm in period_maps.values():
        all_cells.update(pm.keys())

    if not all_cells:
        return []

    rows = []
    for cell in all_cells:
        scores = [pm.get(cell, 0.0) for pm in period_maps.values()]
        rows.append({
            "grid_lng":   cell[0],
            "grid_lat":   cell[1],
            "max_score":  max(scores),
            "avg_score":  sum(scores) / len(scores),
            **{k: period_maps[k].get(cell, 0.0) for k in period_maps},
        })

    # 按综合得分降序，取 top_n
    rows.sort(key=lambda x: x["avg_score"], reverse=True)
    top_rows = rows[:top_n]

    # 批量逆地理编码（每次请求间隔 120ms 避免超 QPS）
    result = []
    for rank, row in enumerate(top_rows, start=1):
        clng = round(row["grid_lng"] + half, 6)
        clat = round(row["grid_lat"] + half, 6)
        addr = _regeocode(clng, clat)
        result.append({
            "rank":    rank,
            "address": addr,
            "morning": row.get("morning_peak", 0.0),
            "daytime": row.get("daytime", 0.0),
            "evening": row.get("evening_peak", 0.0),
            "score":   row["avg_score"],
            "lng":     clng,
            "lat":     clat,
        })
        time.sleep(0.12)

    logger.info("Top%d 热点地址解析完成", top_n)
    return result


def load_all_periods(weeks_back: int = 1) -> dict:
    """
    一次性加载所有时段，返回 {period_key: DataFrame}。
    """
    return {
        key: load_week_data(key, weeks_back)
        for key in config.TIME_PERIODS
    }


def get_data_stats() -> dict:
    """返回数据库基本统计（用于报告页脚）。"""
    with sqlite3.connect(config.DB_PATH) as conn:
        total = conn.execute("SELECT COUNT(*) FROM traffic_samples").fetchone()[0]
        earliest = conn.execute(
            "SELECT MIN(sampled_at) FROM traffic_samples"
        ).fetchone()[0]
        latest = conn.execute(
            "SELECT MAX(sampled_at) FROM traffic_samples"
        ).fetchone()[0]
        by_period = dict(conn.execute(
            "SELECT period, COUNT(*) FROM traffic_samples GROUP BY period"
        ).fetchall())
    return {
        "total_records": total,
        "earliest": earliest,
        "latest":   latest,
        "by_period": by_period,
    }
