"""
main.py
───────
CLI 入口，支持：
  python main.py                    # 启动后台调度器（持续运行）
  python main.py --sample           # 立即执行一次采样
  python main.py --report           # 立即生成热力图报告
  python main.py --report --weeks 2 # 用最近2周数据生成报告
  python main.py --check            # 查看数据库统计
  python main.py --demo             # 生成演示报告（用随机模拟数据，无需 API Key）
"""

import argparse
import logging
import os
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def cmd_sample():
    import data_collector
    data_collector.init_db()
    n = data_collector.collect_sample()
    print(f"✅ 采样完成，写入 {n} 个网格记录")


def cmd_report(weeks_back: int = 1):
    import data_processor
    import heatmap_generator
    import config

    all_data = data_processor.load_all_periods(weeks_back=weeks_back)
    stats    = data_processor.get_data_stats()
    path     = heatmap_generator.generate_report(all_data, stats, config.OUTPUT_DIR)
    print(f"✅ 报告已生成: {path}")
    _try_open(path)


def cmd_check():
    import data_processor
    stats = data_processor.get_data_stats()
    print("\n📊 数据库统计")
    print(f"  总记录数  : {stats['total_records']:,}")
    print(f"  最早时间  : {stats['earliest']}")
    print(f"  最新时间  : {stats['latest']}")
    print("  各时段记录:")
    for period, cnt in (stats.get("by_period") or {}).items():
        print(f"    {period:20s}: {cnt:,}")


def cmd_demo():
    """用随机模拟数据生成演示报告，验证渲染效果。"""
    import numpy as np
    import pandas as pd
    import config
    import heatmap_generator

    rng = np.random.default_rng(42)
    min_lng, min_lat, max_lng, max_lat = config.BOUNDS
    r = config.GRID_RESOLUTION

    def _make_demo_df(n_cells: int = 300) -> pd.DataFrame:
        # 模拟若干热点簇 + 随机背景
        rows = []
        # 热点簇
        for _ in range(5):
            cx = rng.uniform(min_lng + 0.1, max_lng - 0.1)
            cy = rng.uniform(min_lat + 0.05, max_lat - 0.05)
            for _ in range(n_cells // 5):
                glng = round(cx + rng.normal(0, 0.04), 6)
                glat = round(cy + rng.normal(0, 0.02), 6)
                rows.append({"grid_lng": glng, "grid_lat": glat,
                             "score": rng.uniform(0.6, 1.0),
                             "sample_count": rng.integers(5, 30)})
        # 背景噪声
        for _ in range(n_cells // 3):
            rows.append({
                "grid_lng": round(rng.uniform(min_lng, max_lng), 6),
                "grid_lat": round(rng.uniform(min_lat, max_lat), 6),
                "score": rng.uniform(0.05, 0.4),
                "sample_count": rng.integers(2, 8),
            })
        df = pd.DataFrame(rows)
        s_min, s_max = df["score"].min(), df["score"].max()
        df["score_norm"] = (df["score"] - s_min) / (s_max - s_min)
        return df

    all_data = {key: _make_demo_df() for key in config.TIME_PERIODS}
    stats = {"total_records": 9999, "earliest": "2026-03-31 07:00:00",
             "latest": "2026-04-07 20:00:00",
             "by_period": {k: 3333 for k in config.TIME_PERIODS}}

    path = heatmap_generator.generate_report(all_data, stats, config.OUTPUT_DIR)
    print(f"✅ 演示报告已生成: {path}")
    _try_open(path)


def _try_open(path: str):
    """尝试在系统默认浏览器中打开 HTML 文件。"""
    import subprocess, platform
    try:
        if platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        elif platform.system() == "Windows":
            os.startfile(path)
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(description="滴滴司机热点地图生成器")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--sample", action="store_true", help="立即采样一次")
    group.add_argument("--report", action="store_true", help="立即生成报告")
    group.add_argument("--check",  action="store_true", help="查看数据统计")
    group.add_argument("--demo",   action="store_true", help="生成演示报告（不需要 API Key）")
    parser.add_argument("--weeks", type=int, default=1, help="报告覆盖最近N周（默认1）")
    args = parser.parse_args()

    if args.sample:
        cmd_sample()
    elif args.report:
        cmd_report(weeks_back=args.weeks)
    elif args.check:
        cmd_check()
    elif args.demo:
        cmd_demo()
    else:
        # 默认启动调度器
        import scheduler
        scheduler.run()


if __name__ == "__main__":
    main()
