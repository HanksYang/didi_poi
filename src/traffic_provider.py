"""
traffic_provider.py
─────────────────────
抽象层，支持多个路况数据源（高德、火山引擎等）。
每个 provider 实现统一接口，返回 [(grid_lng, grid_lat, score), ...]
"""

import logging
import requests
from abc import ABC, abstractmethod
from collections import defaultdict
import config

logger = logging.getLogger(__name__)


class TrafficProvider(ABC):
    """路况数据源抽象基类。"""

    @abstractmethod
    def fetch_chunk(self, sw: tuple, ne: tuple) -> list:
        """
        请求一个矩形区域的路况。
        返回: [(grid_lng, grid_lat, score), ...]
        """
        pass


class AmapProvider(TrafficProvider):
    """高德地图路况 Provider。"""

    TRAFFIC_URL = "https://restapi.amap.com/v3/traffic/status/rectangle"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_chunk(self, sw: tuple, ne: tuple) -> list:
        """请求高德路况矩形查询。"""
        rectangle = f"{sw[0]},{sw[1]};{ne[0]},{ne[1]}"
        params = {
            "key": self.api_key,
            "rectangle": rectangle,
            "level": 5,
            "extensions": "all",
        }
        try:
            resp = requests.get(self.TRAFFIC_URL, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("高德请求失败 rectangle=%s: %s", rectangle, e)
            return []

        if data.get("status") != "1":
            logger.warning("高德返回错误 rectangle=%s info=%s", rectangle, data.get("info"))
            return []

        roads = data.get("trafficinfo", {}).get("roads", [])
        records = []
        for road in roads:
            status = str(road.get("status", "0"))
            weight = config.STATUS_WEIGHTS.get(status, 0.1)
            polyline = road.get("polyline", "")
            if not polyline:
                continue
            pts = self._parse_polyline(polyline)
            seen_cells = set()
            for lng, lat in pts:
                cell = self._to_grid(lng, lat)
                if cell not in seen_cells:
                    seen_cells.add(cell)
                    records.append((*cell, weight))
        return records

    @staticmethod
    def _parse_polyline(polyline_str: str):
        """'lng,lat;lng,lat;...' → [(lng, lat), ...]"""
        pts = []
        for pair in polyline_str.strip().split(";"):
            parts = pair.split(",")
            if len(parts) == 2:
                try:
                    pts.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
        return pts

    @staticmethod
    def _to_grid(lng: float, lat: float) -> tuple:
        """将经纬度对齐到 GRID_RESOLUTION 网格。"""
        import math
        r = config.GRID_RESOLUTION
        return (round(math.floor(lng / r) * r, 6),
                round(math.floor(lat / r) * r, 6))


class VolcanoProvider(TrafficProvider):
    """火山引擎（ByteDance）路况 Provider。"""

    TRAFFIC_URL = "https://openapi.volcengine.com/traffic/v1/road-status"

    def __init__(self, api_key: str):
        self.api_key = api_key

    def fetch_chunk(self, sw: tuple, ne: tuple) -> list:
        """请求火山引擎路况数据。"""
        rectangle = f"{sw[0]},{sw[1]};{ne[0]},{ne[1]}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "rectangle": rectangle,
            "level": 5,
            "extensions": "all",
        }
        try:
            resp = requests.post(self.TRAFFIC_URL, json=payload, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("火山引擎请求失败 rectangle=%s: %s", rectangle, e)
            return []

        if data.get("code") != 0:
            logger.warning("火山引擎返回错误 rectangle=%s msg=%s", rectangle, data.get("message"))
            return []

        roads = data.get("data", {}).get("roads", [])
        records = []
        for road in roads:
            status = str(road.get("status", "0"))
            weight = config.STATUS_WEIGHTS.get(status, 0.1)
            polyline = road.get("polyline", "")
            if not polyline:
                continue
            pts = self._parse_polyline(polyline)
            seen_cells = set()
            for lng, lat in pts:
                cell = self._to_grid(lng, lat)
                if cell not in seen_cells:
                    seen_cells.add(cell)
                    records.append((*cell, weight))
        return records

    @staticmethod
    def _parse_polyline(polyline_str: str):
        """'lng,lat;lng,lat;...' → [(lng, lat), ...]"""
        pts = []
        for pair in polyline_str.strip().split(";"):
            parts = pair.split(",")
            if len(parts) == 2:
                try:
                    pts.append((float(parts[0]), float(parts[1])))
                except ValueError:
                    pass
        return pts

    @staticmethod
    def _to_grid(lng: float, lat: float) -> tuple:
        """将经纬度对齐到 GRID_RESOLUTION 网格。"""
        import math
        r = config.GRID_RESOLUTION
        return (round(math.floor(lng / r) * r, 6),
                round(math.floor(lat / r) * r, 6))


def get_provider(provider_name: str = None) -> TrafficProvider:
    """
    获取路况 Provider 实例。
    provider_name: "amap" | "volcano" | None (自动选择)
    """
    provider_name = provider_name or config.TRAFFIC_PROVIDER

    if provider_name == "amap":
        if not config.AMAP_API_KEY:
            raise ValueError("AMAP_API_KEY 未配置")
        return AmapProvider(config.AMAP_API_KEY)
    elif provider_name == "volcano":
        if not config.VOLC_API_KEY:
            raise ValueError("VOLC_API_KEY 未配置")
        return VolcanoProvider(config.VOLC_API_KEY)
    else:
        raise ValueError(f"未知的 Provider: {provider_name}")
