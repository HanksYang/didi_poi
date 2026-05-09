"""
heatmap_generator.py
────────────────────
把处理后的各时段热力数据渲染成：
  1. 一张含「图层切换」的交互 Folium 热力图（all_periods_map.html）
  2. 每个时段单独一张热力图（morning_peak.html / daytime.html / evening_peak.html）
  3. 汇总报告页面（report_<date>.html），内嵌 iframe 标签页
"""

import os
import logging
from datetime import datetime

import folium
import folium.plugins
from folium.plugins import HeatMap
import pandas as pd

import config
import data_processor

logger = logging.getLogger(__name__)


# ─── 辅助 ─────────────────────────────────────────────────────────────────────

def _city_center():
    min_lng, min_lat, max_lng, max_lat = config.BOUNDS
    return [(min_lat + max_lat) / 2, (min_lng + max_lng) / 2]


def _heat_data(df: pd.DataFrame):
    """DataFrame → [[lat, lng, intensity], ...]（Folium HeatMap 格式）"""
    if df.empty:
        return []
    half = config.GRID_RESOLUTION / 2
    return [
        [row.grid_lat + half, row.grid_lng + half, float(row.score_norm)]
        for row in df.itertuples()
    ]


def _heatmap_config(color: str) -> dict:
    """根据时段颜色生成 HeatMap 渐变色。"""
    return {
        "radius":    18,
        "blur":      15,
        "min_opacity": 0.35,
        "gradient": {0.2: "blue", 0.5: color, 1.0: "red"},
    }


def _add_hotspot_markers(fg: folium.FeatureGroup, top_df: pd.DataFrame, color: str):
    """在 FeatureGroup 上添加 Top N 热点标记圆圈。"""
    for rank, row in enumerate(top_df.itertuples(), start=1):
        folium.CircleMarker(
            location=[row.center_lat, row.center_lng],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.75,
            popup=folium.Popup(
                f"<b>Top {rank}</b><br>"
                f"热力得分: {row.score_norm:.2f}<br>"
                f"样本数: {row.sample_count}",
                max_width=180,
            ),
            tooltip=f"#{rank} 热点",
        ).add_to(fg)


# ─── 核心生成函数 ──────────────────────────────────────────────────────────────

def generate_combined_map(all_data: dict, output_dir: str) -> str:
    """
    生成含所有时段图层的综合热力图（图层控制面板切换）。
    返回保存路径。
    """
    center = _city_center()
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )

    # 添加比例尺和全屏按钮
    folium.plugins.Fullscreen().add_to(m)
    folium.plugins.MeasureControl().add_to(m)

    first_period = True
    for period_key, df in all_data.items():
        period_cfg = config.TIME_PERIODS[period_key]
        label  = period_cfg["label"]
        color  = period_cfg["color"]

        fg = folium.FeatureGroup(name=f"🔥 {label}", show=first_period)
        first_period = False

        heat = _heat_data(df)
        if heat:
            HeatMap(heat, name=label, **_heatmap_config(color)).add_to(fg)

            top = data_processor.get_top_hotspots(df, top_n=15)
            _add_hotspot_markers(fg, top, color)
        else:
            # 占位 marker，提示无数据
            folium.Marker(
                location=center,
                popup=f"{label}: 暂无数据",
                icon=folium.Icon(color="gray"),
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    _add_legend(m)

    out_path = os.path.join(output_dir, "all_periods_map.html")
    m.save(out_path)
    logger.info("综合热力图已保存: %s", out_path)
    return out_path


def generate_period_map(period_key: str, df: pd.DataFrame, output_dir: str) -> str:
    """生成单时段热力图，返回保存路径。"""
    period_cfg = config.TIME_PERIODS[period_key]
    label = period_cfg["label"]
    color = period_cfg["color"]
    center = _city_center()

    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles="CartoDB dark_matter",
        prefer_canvas=True,
    )
    folium.plugins.Fullscreen().add_to(m)

    heat = _heat_data(df)
    if heat:
        HeatMap(heat, **_heatmap_config(color)).add_to(m)
        top = data_processor.get_top_hotspots(df, top_n=20)
        _add_hotspot_markers(
            m,   # 直接加到 map（单图层无需 FeatureGroup）
            top, color
        )

    _add_legend(m, period_label=label)

    out_path = os.path.join(output_dir, f"{period_key}.html")
    m.save(out_path)
    logger.info("%s 热力图已保存: %s", label, out_path)
    return out_path


def generate_report(all_data: dict, stats: dict, output_dir: str) -> str:
    """
    生成汇总 HTML 报告（内嵌三个时段 iframe + 统计信息）。
    返回报告路径。
    """
    today = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(output_dir, f"report_{today}.html")

    # 先生成各时段地图
    period_map_paths = {}
    for period_key, df in all_data.items():
        p = generate_period_map(period_key, df, output_dir)
        period_map_paths[period_key] = os.path.basename(p)

    combined_path = generate_combined_map(all_data, output_dir)

    # ── Top 30 热点（含逆地理编码地址）─────────────────────────────────────
    logger.info("正在获取 Top 30 热点地址（调用逆地理编码）…")
    top30 = data_processor.get_top30_with_address(all_data, top_n=30)
    top30_html = _render_top30(top30)

    # 构建报告 HTML
    tabs_html = ""
    tab_buttons_html = ""
    for i, (period_key, period_cfg) in enumerate(config.TIME_PERIODS.items()):
        label   = period_cfg["label"]
        color   = period_cfg["color"]
        df      = all_data.get(period_key, pd.DataFrame())
        top_cnt = len(data_processor.get_top_hotspots(df, top_n=20)) if not df.empty else 0
        map_file = period_map_paths.get(period_key, "")
        active_btn = "active" if i == 0 else ""
        active_tab = "active show" if i == 0 else ""

        tab_buttons_html += f"""
          <button class="tab-btn {active_btn}" onclick="switchTab('{period_key}')"
                  data-period="{period_key}" style="border-top: 3px solid {color}">
            {label}
            <span class="badge" style="background:{color}">{top_cnt} 热点</span>
          </button>"""

        tab_body = f'<iframe src="{map_file}" width="100%" height="600px" frameborder="0"></iframe>' \
                   if map_file else "<p class='no-data'>暂无数据，请等待采样积累。</p>"

        tabs_html += f"""
          <div id="tab-{period_key}" class="tab-content {active_tab}">
            {tab_body}
          </div>"""

    stat_rows = "".join(
        f"<tr><td>{k.replace('_peak', '高峰').replace('morning', '早').replace('evening', '晚').replace('daytime', '白天')}</td><td>{v:,}</td></tr>"
        for k, v in (stats.get("by_period") or {}).items()
    )

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>滴滴司机热点周报 · {today}</title>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{ font-family: -apple-system, 'PingFang SC', sans-serif; background: #0f0f1a; color: #e0e0e0; }}
    header {{ background: #1a1a2e; padding: 20px 32px; border-bottom: 1px solid #2d2d4e; }}
    header h1 {{ font-size: 1.5rem; color: #fff; }}
    header p  {{ font-size: 0.85rem; color: #888; margin-top: 4px; }}
    .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 32px; }}
    .stats-row {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
    .stat-card {{ background: #1a1a2e; border: 1px solid #2d2d4e; border-radius: 8px;
                  padding: 16px 20px; flex: 1; min-width: 160px; }}
    .stat-card .value {{ font-size: 1.6rem; font-weight: bold; color: #7c83fd; }}
    .stat-card .label {{ font-size: 0.78rem; color: #888; margin-top: 4px; }}
    .tabs-wrapper {{ background: #1a1a2e; border-radius: 10px; border: 1px solid #2d2d4e; overflow: hidden; }}
    .tab-buttons {{ display: flex; background: #12122a; border-bottom: 1px solid #2d2d4e; }}
    .tab-btn {{ flex: 1; padding: 14px 16px; background: none; border: none; color: #999;
                cursor: pointer; font-size: 0.9rem; transition: all .2s; border-top: 3px solid transparent; }}
    .tab-btn.active, .tab-btn:hover {{ background: #1a1a2e; color: #fff; }}
    .badge {{ display: inline-block; background: #333; border-radius: 12px; padding: 2px 8px;
              font-size: 0.72rem; margin-left: 6px; }}
    .tab-content {{ display: none; padding: 0; }}
    .tab-content.active {{ display: block; }}
    .no-data {{ padding: 60px; text-align: center; color: #555; }}
    .map-combined {{ margin-top: 24px; border-radius: 10px; overflow: hidden;
                     border: 1px solid #2d2d4e; }}
    .map-combined h2 {{ background: #12122a; padding: 14px 20px; font-size: 1rem; color: #aaa; }}
    footer {{ text-align: center; color: #444; font-size: 0.78rem; padding: 24px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 0.85rem; }}
    td {{ padding: 6px 12px; border-bottom: 1px solid #222; }}
    tr:last-child td {{ border: none; }}
    .top30 {{ background:#1a1a2e; border:1px solid #2d2d4e; border-radius:10px;
               margin-bottom:24px; overflow:hidden; }}
    .top30 h2 {{ background:#12122a; padding:14px 20px; font-size:1rem; color:#aaa; }}
    .top30 table {{ font-size:0.82rem; }}
    .top30 th {{ background:#12122a; color:#888; padding:10px 12px;
                 text-align:left; font-weight:500; white-space:nowrap; }}
    .top30 td {{ padding:9px 12px; color:#ccc; }}
    .top30 tr:hover td {{ background:rgba(255,255,255,.03); }}
    .rank-num {{ font-weight:bold; color:#7c83fd; font-size:1rem; width:36px; }}
    .rank-1 .rank-num {{ color:#ffd700; }}
    .rank-2 .rank-num {{ color:#c0c0c0; }}
    .rank-3 .rank-num {{ color:#cd7f32; }}
    .score-bar {{ display:inline-block; height:6px; border-radius:3px;
                  background:linear-gradient(90deg,#7c83fd,#e74c3c); vertical-align:middle;
                  margin-left:6px; }}
    .addr {{ max-width:280px; }}
    .period-dot {{ display:inline-block; width:8px; height:8px; border-radius:50%;
                   margin-right:2px; }}
    .no-data-dash {{ color:#444; }}
  </style>
</head>
<body>
<header>
  <h1>🚖 滴滴司机热点地图 · 周报</h1>
  <p>数据周期: {stats.get('earliest', 'N/A')} → {stats.get('latest', 'N/A')} &nbsp;|&nbsp;
     城市: {config.CITY.upper()} &nbsp;|&nbsp; 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
</header>
<div class="container">
  <div class="stats-row">
    <div class="stat-card">
      <div class="value">{stats.get('total_records', 0):,}</div>
      <div class="label">总采样记录</div>
    </div>
    {_stat_period_cards(all_data)}
  </div>

  {top30_html}

  <div class="tabs-wrapper">
    <div class="tab-buttons">
      {tab_buttons_html}
    </div>
    {tabs_html}
  </div>

  <div class="map-combined">
    <h2>📍 全时段综合图（可切换图层）</h2>
    <iframe src="{os.path.basename(combined_path)}" width="100%" height="620px" frameborder="0"></iframe>
  </div>

  <div style="margin-top:24px; background:#1a1a2e; border:1px solid #2d2d4e; border-radius:8px; padding:16px;">
    <h3 style="font-size:.9rem; color:#888; margin-bottom:10px;">各时段采样量</h3>
    <table>{stat_rows}</table>
  </div>
</div>
<footer>由高德地图 API 提供路况数据 &nbsp;·&nbsp; 仅供参考，实际接单请结合本地经验</footer>

<script>
function switchTab(periodKey) {{
  document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active','show'));
  document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
  document.getElementById('tab-' + periodKey).classList.add('active','show');
  document.querySelector('[data-period="' + periodKey + '"]').classList.add('active');
}}
</script>
</body>
</html>"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("周报已生成: %s", report_path)
    return report_path


def _stat_period_cards(all_data: dict) -> str:
    cards = ""
    for key, cfg in config.TIME_PERIODS.items():
        df = all_data.get(key, pd.DataFrame())
        top = data_processor.get_top_hotspots(df, top_n=10) if not df.empty else pd.DataFrame()
        avg_score = f"{df['score_norm'].mean():.2f}" if not df.empty and "score_norm" in df else "—"
        cards += f"""
    <div class="stat-card">
      <div class="value" style="color:{cfg['color']}">{len(top)}</div>
      <div class="label">{cfg['label']} 推荐热点</div>
      <div style="font-size:.75rem;color:#666;margin-top:4px">平均热力: {avg_score}</div>
    </div>"""
    return cards


def _render_top30(top30: list) -> str:
    """把 Top 30 列表渲染成 HTML 卡片（置于报告顶部）。"""
    if not top30:
        return '<div class="top30"><h2>🏆 Top 30 热门接单地点</h2><p class="no-data">暂无足够数据</p></div>'

    period_colors = {
        "morning": config.TIME_PERIODS["morning_peak"]["color"],
        "daytime": config.TIME_PERIODS["daytime"]["color"],
        "evening": config.TIME_PERIODS["evening_peak"]["color"],
    }

    def _score_cell(score: float, color: str) -> str:
        if score < 0.05:
            return '<span class="no-data-dash">—</span>'
        bar_w = int(score * 60)
        return (f'<span style="color:{color};font-weight:500">{score:.2f}</span>'
                f'<span class="score-bar" style="width:{bar_w}px;background:{color}"></span>')

    def _rank_class(rank: int) -> str:
        return f"rank-{rank}" if rank <= 3 else ""

    rows_html = ""
    for item in top30:
        r = item["rank"]
        rows_html += f"""
      <tr class="{_rank_class(r)}">
        <td class="rank-num">#{r}</td>
        <td class="addr">{item['address']}</td>
        <td>{_score_cell(item['morning'], period_colors['morning'])}</td>
        <td>{_score_cell(item['daytime'], period_colors['daytime'])}</td>
        <td>{_score_cell(item['evening'], period_colors['evening'])}</td>
        <td style="color:#888;font-size:.75rem">{item['lng']:.4f},{item['lat']:.4f}</td>
      </tr>"""

    return f"""
  <div class="top30">
    <h2>🏆 Top 30 热门接单地点（综合全时段得分）</h2>
    <table>
      <thead>
        <tr>
          <th>排名</th>
          <th>地点</th>
          <th><span class="period-dot" style="background:{period_colors['morning']}"></span>早高峰</th>
          <th><span class="period-dot" style="background:{period_colors['daytime']}"></span>白天</th>
          <th><span class="period-dot" style="background:{period_colors['evening']}"></span>晚高峰</th>
          <th>坐标</th>
        </tr>
      </thead>
      <tbody>{rows_html}
      </tbody>
    </table>
  </div>"""


def _add_legend(m, period_label: str = ""):
    """在地图右下角注入简单图例 HTML。"""
    legend_html = f"""
    <div style="position:fixed;bottom:30px;right:10px;z-index:9999;
                background:rgba(0,0,0,.75);color:#eee;padding:12px 16px;
                border-radius:8px;font-size:12px;line-height:1.8">
      {'<b>' + period_label + '</b><br>' if period_label else ''}
      🔴 高热力区（接单黄金区域）<br>
      🟡 中热力区<br>
      🔵 低热力区<br>
      ● 圆圈 = Top 热点标注
    </div>"""
    m.get_root().html.add_child(folium.Element(legend_html))
