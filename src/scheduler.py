"""
scheduler.py
────────────
使用 APScheduler 管理两类定时任务：
  1. 采样任务：每 SAMPLE_INTERVAL_MINUTES 分钟执行一次，仅在 ACTIVE_HOURS 内生效
  2. 周报任务：每周一 06:00 自动生成上周热力图报告

运行方式：
  python scheduler.py          # 持续后台运行
  python main.py --sample      # 手动触发一次采样
  python main.py --report      # 手动触发生成报告
"""

import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

import config
import data_collector
import data_processor
import heatmap_generator

logger = logging.getLogger(__name__)


def job_collect():
    """定时采样任务。"""
    try:
        n = data_collector.collect_sample()
        logger.info("采样任务完成，写入 %d 个网格", n)
    except Exception:
        logger.exception("采样任务异常")


def job_weekly_report():
    """周报生成任务（每周一早上6点执行）。"""
    try:
        logger.info("开始生成周报…")
        all_data = data_processor.load_all_periods(weeks_back=1)
        stats    = data_processor.get_data_stats()
        path     = heatmap_generator.generate_report(all_data, stats, config.OUTPUT_DIR)
        logger.info("周报生成完成: %s", path)
        # 清理旧数据
        data_collector.purge_old_data()
    except Exception:
        logger.exception("周报任务异常")


def build_scheduler() -> BlockingScheduler:
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")

    # ── 采样任务：每 N 分钟一次 ───────────────────────────────────────────────
    scheduler.add_job(
        job_collect,
        trigger=IntervalTrigger(minutes=config.SAMPLE_INTERVAL_MINUTES),
        id="collect",
        name="路况采样",
        max_instances=1,
        misfire_grace_time=60,
    )

    # ── 周报任务：每周一 06:00 ────────────────────────────────────────────────
    scheduler.add_job(
        job_weekly_report,
        trigger=CronTrigger(day_of_week="mon", hour=6, minute=0),
        id="weekly_report",
        name="周报生成",
        max_instances=1,
    )

    return scheduler


def run():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    data_collector.init_db()

    scheduler = build_scheduler()

    def _shutdown(sig, frame):
        logger.info("收到退出信号，正在关闭调度器…")
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logger.info(
        "调度器启动 | 采样间隔=%d 分钟 | 活跃小时=%s",
        config.SAMPLE_INTERVAL_MINUTES,
        config.ACTIVE_HOURS,
    )
    logger.info("周报将在每周一 06:00 自动生成，输出目录: %s", config.OUTPUT_DIR)

    scheduler.start()


if __name__ == "__main__":
    run()
