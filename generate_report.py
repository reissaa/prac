"""
パッシブ住宅効果 静的レポート生成スクリプト
EPWデータを解析し、インタラクティブHTMLチャートと集計CSVを生成する。
GitHub Actions から自動実行される。
"""

import os
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
CHARTS_DIR = os.path.join(DOCS_DIR, 'charts')
os.makedirs(CHARTS_DIR, exist_ok=True)

CITIES = {
    'TOKYO':     {'name': '東京',   'lat': 35.6892, 'lon': 139.6917, 'zone': '6地域', 'color': '#e74c3c'},
    'SAPPORO':   {'name': '札幌',   'lat': 43.0642, 'lon': 141.3469, 'zone': '1地域', 'color': '#3498db'},
    'OSAKA':     {'name': '大阪',   'lat': 34.6864, 'lon': 135.5200, 'zone': '6地域', 'color': '#27ae60'},
    'FUKUOKA':   {'name': '福岡',   'lat': 33.6064, 'lon': 130.4181, 'zone': '7地域', 'color': '#f39c12'},
    'KAGOSHIMA': {'name': '鹿児島', 'lat': 31.5603, 'lon': 130.5603, 'zone': '7地域', 'color': '#9b59b6'},
}

MONTHS_JP = ['1月', '2月', '3月', '4月', '5月', '6月',
             '7月', '8月', '9月', '10月', '11月', '12月']
DIRECTIONS = {'S': '南', 'E': '東', 'N': '北', 'W': '西'}
DIR_COLORS = {'S': '#e74c3c', 'E': '#e67e22', 'N': '#3498db', 'W': '#27ae60'}

EPW_COLS = [
    'datetime', 'temp_db', 'temp_dp', 'temp_wb', 'humidity_ratio', 'rh',
    'pressure', 'wind_speed', 'wind_dir', 'sky_temp', 'infrared_rad',
    'solar_diffuse', 'solar_direct', 'precip_rate', 'precip_depth',
    'ground_solar', 'ground_temp', 'surface_ground_temp', 'deep_ground_temp',
    'factor_ground_temp', 'total_sky_cover', 'opaque_sky_cover', 'enthalpy',
    'density', 'solar_azimuth', 'solar_altitude', 'solar_hour_angle',
    'rain_status', 'snow_status', 'sky_illuminance', 'beam_illuminance',
    'beam_normal_illuminance', 'sky_luminous_efficacy', 'beam_luminous_efficacy',
    'sky_clearness', 'sky_brightness', 'dst_status', 'day_type', 'mains_temp',
]

PLOTLY_CONFIG = {'responsive': True, 'displayModeBar': True, 'scrollZoom': False}


# ──────────────────────────────────────────────────────────────────────────────
# データ読み込み
# ──────────────────────────────────────────────────────────────────────────────

def load_climate(city_code):
    fp = os.path.join(BASE_DIR, '地点データ', city_code, 'site', 'eplusout.csv')
    df = pd.read_csv(fp, skiprows=1, header=None, names=EPW_COLS)
    df['datetime'] = df['datetime'].str.strip()
    df['month'] = df['datetime'].str[0:2].str.strip().astype(int)
    df['hour']  = df['datetime'].str[7:9].str.strip().astype(int)
    df['ghi']   = df['solar_diffuse'] + df['solar_direct']
    return df


def load_mwep(city_code):
    base = os.path.join(BASE_DIR, '地点データ', city_code, 'wep_base')
    mweph = pd.read_csv(f'{base}/MWEPh({city_code}・省エネ).csv')
    mwepc = pd.read_csv(f'{base}/MWEPc({city_code}・省エネ).csv')
    mwept = pd.read_csv(f'{base}/MWEPt({city_code}・省エネ).csv')
    for d in [mweph, mwepc, mwept]:
        d.index = range(1, len(d) + 1)
    return mweph, mwepc, mwept


def load_energy(city_code):
    fp = os.path.join(BASE_DIR, '地点データ', city_code,
                      'grade4 Zone Ideal Loads Supply Enegy', 'eplusout.csv')
    df = pd.read_csv(fp, header=0)
    cols = list(df.columns)
    hc = [c for c in cols if 'Heating Energy' in c]
    sc = [c for c in cols if 'Sensible Cooling Energy' in c]
    lc = [c for c in cols if 'Latent Cooling Energy' in c]
    df['heating_kWh'] = df[hc].sum(axis=1) / 3_600_000
    df['cooling_kWh'] = (df[sc].sum(axis=1) + df[lc].sum(axis=1)) / 3_600_000
    df['month'] = df[cols[0]].str.strip().str[0:2].astype(int)
    return df


# ──────────────────────────────────────────────────────────────────────────────
# チャート生成
# ──────────────────────────────────────────────────────────────────────────────

def fig_temperature(df, city_name):
    monthly = df.groupby('month')['temp_db'].agg(['mean', 'min', 'max']).reset_index()
    rh_avg  = df.groupby('month')['rh'].mean().reset_index()

    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.65, 0.35],
        subplot_titles=['外気温 [°C]', '相対湿度 [%]'],
        vertical_spacing=0.10,
    )
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['max'], name='最高気温',
        mode='lines+markers', line=dict(color='#e74c3c', width=2),
        marker=dict(size=7),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['min'], name='最低気温',
        mode='lines+markers', fill='tonexty',
        fillcolor='rgba(231,76,60,0.10)',
        line=dict(color='#3498db', width=2), marker=dict(size=7),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['mean'], name='平均気温',
        mode='lines+markers',
        line=dict(color='#f39c12', width=2.5, dash='dash'),
        marker=dict(size=9, symbol='diamond'),
    ), row=1, col=1)
    for y, txt, col in [(18, '暖房基準 18°C', 'limegreen'), (26, '冷房基準 26°C', 'orange')]:
        fig.add_hline(y=y, line_dash='dot', line_color=col, line_width=1.5,
                      annotation_text=txt, annotation_position='right',
                      annotation_font_color=col, row=1, col=1)
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=rh_avg['rh'], name='相対湿度',
        marker_color='rgba(52,152,219,0.65)',
        text=rh_avg['rh'].round(0).astype(int).astype(str) + '%',
        textposition='outside', textfont=dict(size=10),
    ), row=2, col=1)
    fig.update_layout(
        title=f'月別気温・湿度プロファイル — {city_name}',
        height=520,
        legend=dict(orientation='h', y=1.02, x=0, font=dict(size=12)),
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')
    return fig


def fig_solar(df, city_name):
    monthly = df.groupby('month').agg(
        ghi_kWh=('ghi', lambda x: x.sum() / 1000),
        diffuse=('solar_diffuse', 'mean'),
        direct=('solar_direct', 'mean'),
    ).reset_index()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['月別全天日射量 [kWh/m²/月]', '月別平均日射成分 [W/m²]'],
    )
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['ghi_kWh'], name='全天日射量',
        marker_color='#F39C12',
        text=monthly['ghi_kWh'].round(1), textposition='outside',
        textfont=dict(size=10),
    ), row=1, col=1)
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['diffuse'], name='散乱日射',
        marker_color='#F9E79F',
    ), row=1, col=2)
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['direct'], name='直達日射',
        marker_color='#E67E22',
    ), row=1, col=2)
    fig.update_layout(
        barmode='stack', height=380,
        title=f'日射量分析 — {city_name}',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        legend=dict(orientation='h', y=-0.2),
        margin=dict(l=10, r=10, t=50, b=60),
    )
    return fig


def fig_wind_rose(df, city_name):
    df_w = df[df['wind_speed'] > 0.3].copy()
    df_w['dir_bin'] = ((df_w['wind_dir'] + 11.25) / 22.5).astype(int) % 16
    theta = [i * 22.5 for i in range(16)]
    tick_jp = ['北', 'NNE', '北東', 'ENE', '東', 'ESE', '南東', 'SSE',
               '南', 'SSW', '南西', 'WSW', '西', 'WNW', '北西', 'NNW']
    ranges = [
        (0, 2,   '< 2 m/s',   '#D6EAF8'),
        (2, 4,   '2〜4 m/s',  '#5DADE2'),
        (4, 6,   '4〜6 m/s',  '#1A5276'),
        (6, 8,   '6〜8 m/s',  '#F39C12'),
        (8, 999, '> 8 m/s',   '#C0392B'),
    ]
    fig = go.Figure()
    for lo, hi, label, color in ranges:
        mask = (df_w['wind_speed'] >= lo) & (df_w['wind_speed'] < hi)
        cnt  = df_w[mask].groupby('dir_bin').size().reindex(range(16), fill_value=0)
        fig.add_trace(go.Barpolar(
            r=cnt.values, theta=theta, name=label, marker_color=color,
        ))
    fig.update_layout(
        title=f'年間風配図 — {city_name}',
        polar=dict(
            angularaxis=dict(
                ticktext=tick_jp, tickvals=theta,
                direction='clockwise', rotation=90,
            ),
        ),
        height=460, showlegend=True,
        legend=dict(x=1.05, y=0.5),
        paper_bgcolor='white',
    )
    return fig


def fig_heatmap(df, city_name):
    pivot = df.pivot_table(values='temp_db', index='hour', columns='month', aggfunc='mean')
    pivot.columns = MONTHS_JP

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=[f'{h}時' for h in pivot.index],
        colorscale='RdBu_r',
        colorbar=dict(title='気温 [°C]'),
        hovertemplate='%{x} %{y}<br>平均気温: %{z:.1f}°C<extra></extra>',
    ))
    fig.add_hline(y=8,  line_dash='dot', line_color='white',
                  annotation_text='日出頃', annotation_font_color='white')
    fig.add_hline(y=18, line_dash='dot', line_color='white',
                  annotation_text='日没頃', annotation_font_color='white')
    fig.update_layout(
        title=f'時刻別・月別 平均外気温 [°C] — {city_name}',
        height=460, paper_bgcolor='white',
    )
    return fig


def fig_mwep_heating(mweph, city_name):
    fig = go.Figure()
    for d, dn in DIRECTIONS.items():
        fig.add_trace(go.Bar(
            name=f'{dn}面 ({d})', x=MONTHS_JP,
            y=mweph[d].values, marker_color=DIR_COLORS[d],
        ))
    fig.add_hline(y=0, line_color='black', line_width=1.5)
    fig.add_hrect(y0=-800, y1=0, fillcolor='rgba(52,152,219,0.05)', line_width=0,
                  annotation_text='▼ 暖房負荷削減域（パッシブ効果）',
                  annotation_position='bottom right',
                  annotation_font=dict(color='steelblue', size=11))
    fig.update_layout(
        title=f'パッシブ太陽熱 暖房効果 (MWEPh) [MJ/m²/月] — {city_name}',
        barmode='group', height=420,
        xaxis_title='月', yaxis_title='MJ/m²',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        legend=dict(orientation='h', y=1.02, x=0),
    )
    return fig


def fig_mwep_cooling(mwepc, city_name):
    fig = go.Figure()
    for d, dn in DIRECTIONS.items():
        fig.add_trace(go.Bar(
            name=f'{dn}面 ({d})', x=MONTHS_JP,
            y=mwepc[d].values, marker_color=DIR_COLORS[d],
        ))
    fig.add_hline(y=0, line_color='black', line_width=1.5)
    fig.add_hrect(y0=0, y1=600, fillcolor='rgba(231,76,60,0.05)', line_width=0,
                  annotation_text='▲ 冷房負荷増加域',
                  annotation_position='top right',
                  annotation_font=dict(color='crimson', size=11))
    fig.update_layout(
        title=f'日射による冷房負荷増加 (MWEPc) [MJ/m²/月] — {city_name}',
        barmode='group', height=420,
        xaxis_title='月', yaxis_title='MJ/m²',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        legend=dict(orientation='h', y=1.02, x=0),
    )
    return fig


def fig_mwep_net(mwept, city_name):
    fig = go.Figure()
    for d, dn in DIRECTIONS.items():
        fig.add_trace(go.Bar(
            name=f'{dn}面 ({d})', x=MONTHS_JP,
            y=mwept[d].values, marker_color=DIR_COLORS[d],
        ))
    fig.add_hline(y=0, line_color='black', line_width=1.5)
    fig.update_layout(
        title=f'正味窓面熱的影響 (MWEPt) [MJ/m²/月] — {city_name}',
        barmode='group', height=420,
        xaxis_title='月',
        yaxis_title='MJ/m²（負値=暖房有利 / 正値=冷房不利）',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        legend=dict(orientation='h', y=1.02, x=0),
    )
    return fig


def fig_annual_radar(mweph, mwepc, city_name):
    dirs = list(DIRECTIONS.keys())
    dnames = [f'{DIRECTIONS[d]}面 ({d})' for d in dirs]
    ann_h = [abs(mweph[d].sum()) for d in dirs]
    ann_c = [mwepc[d].sum() for d in dirs]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=ann_h + [ann_h[0]], theta=dnames + [dnames[0]],
        fill='toself', name='暖房パッシブ効果 [MJ/m²/年]',
        line=dict(color='#e74c3c', width=2), fillcolor='rgba(231,76,60,0.20)',
    ))
    fig.add_trace(go.Scatterpolar(
        r=ann_c + [ann_c[0]], theta=dnames + [dnames[0]],
        fill='toself', name='冷房負荷増加 [MJ/m²/年]',
        line=dict(color='#3498db', width=2), fillcolor='rgba(52,152,219,0.20)',
    ))
    fig.update_layout(
        title=f'年間パッシブ効果 方位別比較 — {city_name}',
        polar=dict(radialaxis=dict(visible=True)),
        height=460, showlegend=True,
        legend=dict(x=0, y=-0.12, orientation='h'),
        paper_bgcolor='white',
    )
    return fig


def fig_energy(df_e, city_name):
    monthly = df_e.groupby('month')[['heating_kWh', 'cooling_kWh']].sum().reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['heating_kWh'],
        name='暖房負荷', marker_color='rgba(231,76,60,0.85)',
    ))
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['cooling_kWh'],
        name='冷房負荷', marker_color='rgba(52,152,219,0.85)',
    ))
    fig.update_layout(
        barmode='group', height=400,
        title=f'月別暖冷房エネルギー需要 [kWh/月] — {city_name}',
        xaxis_title='月', yaxis_title='kWh',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        legend=dict(orientation='h', y=1.02, x=0),
    )
    return fig


def fig_5city_comparison(all_data):
    """5都市まとめ比較チャート"""
    cities_jp  = [all_data[c]['city_name'] for c in all_data]
    colors     = [CITIES[c]['color'] for c in all_data]
    ann_h_S    = [all_data[c]['ann_heat_S'] for c in all_data]
    ann_c_S    = [all_data[c]['ann_cool_S'] for c in all_data]
    net_S      = [all_data[c]['net_S']      for c in all_data]
    ann_temp   = [all_data[c]['avg_temp']   for c in all_data]
    heat_total = [all_data[c]['heat_kWh']   for c in all_data]
    cool_total = [all_data[c]['cool_kWh']   for c in all_data]

    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[
            '南面 暖房パッシブ効果 [MJ/m²/年]',
            '南面 冷房負荷増加 [MJ/m²/年]',
            '南面 正味パッシブ収支 [MJ/m²/年]',
            '年間暖冷房エネルギー需要 [kWh]',
        ],
        vertical_spacing=0.18, horizontal_spacing=0.12,
    )

    for col_idx, (vals, col_name) in enumerate([
        (ann_h_S, '暖房効果'), (ann_c_S, '冷房増加'),
    ], start=1):
        fig.add_trace(go.Bar(
            x=cities_jp, y=vals, name=col_name,
            marker_color=colors,
            text=[f'{v:.0f}' for v in vals], textposition='auto',
        ), row=1, col=col_idx)

    fig.add_trace(go.Bar(
        x=cities_jp, y=net_S, name='正味収支',
        marker_color=['#27ae60' if v > 0 else '#e74c3c' for v in net_S],
        text=[f'{v:+.0f}' for v in net_S], textposition='auto',
    ), row=2, col=1)

    fig.add_trace(go.Bar(
        x=cities_jp, y=heat_total, name='暖房需要',
        marker_color='rgba(231,76,60,0.8)',
    ), row=2, col=2)
    fig.add_trace(go.Bar(
        x=cities_jp, y=cool_total, name='冷房需要',
        marker_color='rgba(52,152,219,0.8)',
    ), row=2, col=2)

    fig.add_hline(y=0, row=2, col=1, line_color='black', line_width=1)

    fig.update_layout(
        barmode='group', height=680,
        title='5都市 パッシブ住宅効果 総合比較',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='white',
        showlegend=False,
        margin=dict(l=10, r=10, t=80, b=20),
    )
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# HTML ページ組み立て
# ──────────────────────────────────────────────────────────────────────────────

CHART_TEMPLATE = """
<div class="chart-block" id="{anchor}">
  <h3>{title}</h3>
  <div class="chart-wrap">{chart_html}</div>
</div>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
  :root {{
    --accent: {accent};
    --bg: #f4f6f9;
    --card: #ffffff;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Helvetica Neue', Arial, sans-serif; background: var(--bg); color: #2c3e50; }}
  header {{
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white; padding: 24px 40px;
    border-bottom: 4px solid var(--accent);
  }}
  header h1 {{ font-size: 1.9em; letter-spacing: 0.02em; }}
  header p  {{ margin-top: 8px; opacity: 0.85; font-size: 1em; }}
  nav {{
    background: white; padding: 12px 40px;
    border-bottom: 1px solid #dde; position: sticky; top: 0; z-index: 100;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
  }}
  nav a {{
    color: var(--accent); text-decoration: none; font-weight: 600;
    padding: 6px 14px; border-radius: 20px;
    border: 1.5px solid var(--accent); font-size: 0.88em;
    transition: all 0.2s;
  }}
  nav a:hover {{ background: var(--accent); color: white; }}
  .kpi-bar {{
    display: flex; gap: 16px; flex-wrap: wrap;
    padding: 24px 40px; background: white;
    border-bottom: 1px solid #eee;
  }}
  .kpi {{
    flex: 1; min-width: 160px;
    background: linear-gradient(135deg, #f8f9fa, #e9ecef);
    border-left: 4px solid var(--accent);
    border-radius: 8px; padding: 14px 18px;
  }}
  .kpi .label {{ font-size: 0.8em; color: #666; margin-bottom: 4px; }}
  .kpi .value {{ font-size: 1.5em; font-weight: 700; color: #2c3e50; }}
  .kpi .sub   {{ font-size: 0.78em; color: #888; margin-top: 2px; }}
  main {{ max-width: 1280px; margin: 0 auto; padding: 32px 24px; }}
  .section-title {{
    font-size: 1.3em; font-weight: 700; color: #2c3e50;
    margin: 36px 0 16px; padding-bottom: 8px;
    border-bottom: 3px solid var(--accent);
  }}
  .chart-block {{
    background: var(--card); border-radius: 12px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    padding: 24px; margin-bottom: 24px;
  }}
  .chart-block h3 {{
    font-size: 1.02em; color: #444; margin-bottom: 14px;
    padding-bottom: 8px; border-bottom: 1px solid #eee;
  }}
  .chart-wrap {{ width: 100%; overflow-x: auto; }}
  .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  @media (max-width: 800px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}
  footer {{
    background: #2c3e50; color: rgba(255,255,255,0.7);
    text-align: center; padding: 24px; font-size: 0.85em; margin-top: 48px;
  }}
  .badge {{
    display: inline-block; background: var(--accent); color: white;
    border-radius: 12px; padding: 2px 10px; font-size: 0.8em; font-weight: 600;
  }}
  .city-links {{ display: flex; gap: 10px; flex-wrap: wrap; padding: 20px 40px; background: #f8f9fa; }}
  .city-link {{
    display: block; text-decoration: none; padding: 10px 20px;
    border-radius: 8px; border: 2px solid; font-weight: 600; font-size: 0.9em;
    transition: all 0.2s;
  }}
  .city-link:hover {{ opacity: 0.8; transform: translateY(-2px); }}
</style>
</head>
<body>
<header>
  <h1>🏠 {title}</h1>
  <p>{subtitle}</p>
</header>
{nav}
{kpi_bar}
<main>
{body}
</main>
<footer>
  データ出典: EnergyPlus 気象シミュレーション（省エネ基準）｜MWEP = 月別窓面エネルギー性能<br>
  Generated by passive-housing-viz · {gen_date}
</footer>
</body>
</html>"""


def chart_to_html(fig):
    return fig.to_html(
        full_html=False, include_plotlyjs='cdn',
        config=PLOTLY_CONFIG,
        div_id=None,
    )


def build_city_page(code, city, df, mweph, mwepc, mwept, df_e):
    """都市別詳細ページを生成"""
    city_name = city['name']
    accent    = city['color']
    avg_temp  = df['temp_db'].mean()
    ann_ghi   = df['ghi'].sum() / 1000
    heat_kWh  = df_e['heating_kWh'].sum()
    cool_kWh  = df_e['cooling_kWh'].sum()
    ann_h_S   = abs(mweph['S'].sum())
    ann_c_S   = mwepc['S'].sum()
    net_S     = ann_h_S - ann_c_S
    summer_avg = df[df['month'].isin([7, 8])]['temp_db'].mean()
    winter_avg = df[df['month'].isin([1, 2, 12])]['temp_db'].mean()

    kpi_bar = f"""
<div class="kpi-bar">
  <div class="kpi">
    <div class="label">年間平均気温</div>
    <div class="value">{avg_temp:.1f}°C</div>
    <div class="sub">夏{summer_avg:.1f}°C / 冬{winter_avg:.1f}°C</div>
  </div>
  <div class="kpi">
    <div class="label">年間日射量</div>
    <div class="value">{ann_ghi:.0f} kWh/m²</div>
    <div class="sub">全天日射（GHI）</div>
  </div>
  <div class="kpi">
    <div class="label">南面 暖房パッシブ効果</div>
    <div class="value">{ann_h_S:.0f} MJ/m²</div>
    <div class="sub">年間・省エネ基準 (MWEPh)</div>
  </div>
  <div class="kpi">
    <div class="label">南面 冷房負荷増加</div>
    <div class="value">{ann_c_S:.0f} MJ/m²</div>
    <div class="sub">年間・省エネ基準 (MWEPc)</div>
  </div>
  <div class="kpi">
    <div class="label">南面 正味収支</div>
    <div class="value" style="color:{'#27ae60' if net_S > 0 else '#e74c3c'}">{net_S:+.0f} MJ/m²</div>
    <div class="sub">{'暖房有利 ✅' if net_S > 0 else '日射遮蔽重要 ⚠️'}</div>
  </div>
  <div class="kpi">
    <div class="label">年間暖冷房エネルギー</div>
    <div class="value">{heat_kWh + cool_kWh:.0f} kWh</div>
    <div class="sub">暖房{heat_kWh:.0f} + 冷房{cool_kWh:.0f}</div>
  </div>
</div>"""

    city_nav_links = ''.join(
        f'<a href="{c}.html" style="border-color:{CITIES[c]["color"]};color:{CITIES[c]["color"]}">'
        f'{CITIES[c]["name"]}</a>'
        for c in CITIES
    )
    nav = f'<nav>\n  <a href="index.html">← 全地点比較</a>\n  {city_nav_links}\n</nav>'

    sections = [
        '<h2 class="section-title">📊 気候データ（EPW）</h2>',
        '<div class="grid-2">',
        CHART_TEMPLATE.format(anchor='temp', title='月別気温プロファイル',
                              chart_html=chart_to_html(fig_temperature(df, city_name))),
        CHART_TEMPLATE.format(anchor='solar', title='月別日射量',
                              chart_html=chart_to_html(fig_solar(df, city_name))),
        '</div>',
        '<div class="grid-2">',
        CHART_TEMPLATE.format(anchor='wind', title='年間風配図',
                              chart_html=chart_to_html(fig_wind_rose(df, city_name))),
        CHART_TEMPLATE.format(anchor='heatmap', title='時刻別・月別 外気温ヒートマップ',
                              chart_html=chart_to_html(fig_heatmap(df, city_name))),
        '</div>',
        '<h2 class="section-title">☀️ パッシブ効果（MWEP）</h2>',
        CHART_TEMPLATE.format(anchor='mweph', title='パッシブ太陽熱 暖房効果 (MWEPh)',
                              chart_html=chart_to_html(fig_mwep_heating(mweph, city_name))),
        CHART_TEMPLATE.format(anchor='mwepc', title='日射による冷房負荷増加 (MWEPc)',
                              chart_html=chart_to_html(fig_mwep_cooling(mwepc, city_name))),
        CHART_TEMPLATE.format(anchor='mwept', title='正味窓面熱的影響 (MWEPt)',
                              chart_html=chart_to_html(fig_mwep_net(mwept, city_name))),
        '<div class="grid-2">',
        CHART_TEMPLATE.format(anchor='radar', title='年間パッシブ効果 方位別レーダー',
                              chart_html=chart_to_html(fig_annual_radar(mweph, mwepc, city_name))),
        CHART_TEMPLATE.format(anchor='energy', title='月別暖冷房エネルギー需要',
                              chart_html=chart_to_html(fig_energy(df_e, city_name))),
        '</div>',
    ]

    import datetime
    html = PAGE_TEMPLATE.format(
        title=f'パッシブ住宅効果 — {city_name}',
        subtitle=(f'省エネ地域区分: {city["zone"]} | '
                  f'緯度: {city["lat"]}°N | 経度: {city["lon"]}°E | '
                  f'EPW気象データによるパッシブ効果分析'),
        accent=accent,
        nav=nav,
        kpi_bar=kpi_bar,
        body='\n'.join(sections),
        gen_date=datetime.date.today().isoformat(),
    )
    return html


def build_index_page(all_data):
    """トップページ（5都市比較）を生成"""
    import datetime

    nav = """<nav>
  <a href="index.html">🏠 ホーム</a>
""" + ''.join(
        f'  <a href="{c}.html" style="border-color:{CITIES[c]["color"]};color:{CITIES[c]["color"]}">'
        f'{CITIES[c]["name"]}</a>\n'
        for c in CITIES
    ) + '</nav>'

    # KPI cards for all cities
    city_cards = '\n'.join(
        f'''<a class="city-link" href="{code}.html"
          style="border-color:{CITIES[code]['color']};color:{CITIES[code]['color']}">
          {CITIES[code]['name']}<br>
          <small style="font-weight:normal">
            {data['avg_temp']:.1f}°C | 南面正味 {data['net_S']:+.0f} MJ
          </small>
        </a>'''
        for code, data in all_data.items()
    )

    comparison_html = chart_to_html(fig_5city_comparison(all_data))

    # Summary table
    rows = '\n'.join(
        f'<tr>'
        f'<td><a href="{c}.html" style="color:{CITIES[c]["color"]};font-weight:bold">{d["city_name"]}</a></td>'
        f'<td>{CITIES[c]["zone"]}</td>'
        f'<td>{d["avg_temp"]:.1f}°C</td>'
        f'<td>{d["ann_ghi"]:.0f}</td>'
        f'<td>{d["ann_heat_S"]:.0f}</td>'
        f'<td>{d["ann_cool_S"]:.0f}</td>'
        f'<td style="color:{"#27ae60" if d["net_S"]>0 else "#e74c3c"};font-weight:bold">'
        f'{d["net_S"]:+.0f}</td>'
        f'<td>{d["heat_kWh"]:.0f}</td>'
        f'<td>{d["cool_kWh"]:.0f}</td>'
        f'</tr>'
        for c, d in all_data.items()
    )

    table_html = f"""
<table style="width:100%;border-collapse:collapse;font-size:0.92em">
  <thead style="background:#f0f2f5">
    <tr>
      <th style="padding:10px;text-align:left;border-bottom:2px solid #ddd">地点</th>
      <th style="padding:10px;text-align:center;border-bottom:2px solid #ddd">地域区分</th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">年均温</th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">日射量<br><small>kWh/m²</small></th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">南面暖房効果<br><small>MJ/m²</small></th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">南面冷房増加<br><small>MJ/m²</small></th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">南面正味収支<br><small>MJ/m²</small></th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">年間暖房<br><small>kWh</small></th>
      <th style="padding:10px;text-align:right;border-bottom:2px solid #ddd">年間冷房<br><small>kWh</small></th>
    </tr>
  </thead>
  <tbody>
    {rows}
  </tbody>
</table>"""

    body = f"""
<div class="city-links">
  {''.join(f'<a class="city-link" href="{c}.html" style="border-color:{CITIES[c]["color"]};color:{CITIES[c]["color"]}">{CITIES[c]["name"]}<br><small style="font-weight:normal">{CITIES[c]["zone"]}</small></a>' for c in CITIES)}
</div>
<main>
<h2 class="section-title">📊 5都市 総合比較チャート</h2>
<div class="chart-block">
  <div class="chart-wrap">{comparison_html}</div>
</div>
<h2 class="section-title">📋 統計サマリーテーブル</h2>
<div class="chart-block">{table_html}</div>
<h2 class="section-title">📖 データの見方</h2>
<div class="chart-block">
  <h3>MWEP（月別窓面エネルギー性能）について</h3>
  <ul style="line-height:2;margin:12px 0 0 20px">
    <li><strong>MWEPh（暖房効果）</strong>: 窓からの日射取得による暖房負荷削減量 [MJ/m²]。負値ほど冬の暖房削減効果が大きい。</li>
    <li><strong>MWEPc（冷房増加）</strong>: 窓からの日射による冷房負荷増加量 [MJ/m²]。正値ほど夏の日射遮蔽が重要。</li>
    <li><strong>MWEPt（正味）</strong>: 暖房効果と冷房増加の合計。負値=年間を通して暖房有利、正値=冷房不利。</li>
    <li><strong>南面正味収支</strong>: 正値の地域（寒冷地）は南窓拡大が有効。負値の地域（温暖地）は庇・ルーバーによる日射遮蔽が重要。</li>
  </ul>
</div>
</main>"""

    import datetime
    return PAGE_TEMPLATE.format(
        title='パッシブ住宅効果 可視化 — 5都市比較',
        subtitle='EPW気象データに基づく日本5都市のパッシブ住宅設計効果分析',
        accent='#2c3e50',
        nav=nav,
        kpi_bar='',
        body=body,
        gen_date=datetime.date.today().isoformat(),
    )


# ──────────────────────────────────────────────────────────────────────────────
# CSV サマリー出力
# ──────────────────────────────────────────────────────────────────────────────

def export_summary_csv(all_data):
    rows = []
    for code, d in all_data.items():
        rows.append({
            '地点コード': code,
            '都市名':     d['city_name'],
            '省エネ地域区分': CITIES[code]['zone'],
            '緯度[°N]':  CITIES[code]['lat'],
            '経度[°E]':  CITIES[code]['lon'],
            '年間平均気温[°C]':   round(d['avg_temp'], 2),
            '夏季平均気温[°C]':   round(d['summer_avg'], 2),
            '冬季平均気温[°C]':   round(d['winter_avg'], 2),
            '年間日射量[kWh/m²]': round(d['ann_ghi'], 1),
            '南面MWEPh[MJ/m²]':  round(d['ann_heat_S'], 1),
            '東面MWEPh[MJ/m²]':  round(d['ann_heat_E'], 1),
            '北面MWEPh[MJ/m²]':  round(d['ann_heat_N'], 1),
            '西面MWEPh[MJ/m²]':  round(d['ann_heat_W'], 1),
            '南面MWEPc[MJ/m²]':  round(d['ann_cool_S'], 1),
            '東面MWEPc[MJ/m²]':  round(d['ann_cool_E'], 1),
            '北面MWEPc[MJ/m²]':  round(d['ann_cool_N'], 1),
            '西面MWEPc[MJ/m²]':  round(d['ann_cool_W'], 1),
            '南面正味収支[MJ/m²]': round(d['net_S'], 1),
            '年間暖房需要[kWh]':  round(d['heat_kWh'], 1),
            '年間冷房需要[kWh]':  round(d['cool_kWh'], 1),
        })
    df = pd.DataFrame(rows)
    out = os.path.join(DOCS_DIR, 'passive_summary.csv')
    df.to_csv(out, index=False, encoding='utf-8-sig')
    print(f'  CSV → {out}')


# ──────────────────────────────────────────────────────────────────────────────
# メイン処理
# ──────────────────────────────────────────────────────────────────────────────

def main():
    print('=' * 60)
    print('パッシブ住宅効果 レポート生成')
    print('=' * 60)

    all_data = {}

    for code, city in CITIES.items():
        print(f'\n📍 {city["name"]} ({code}) を処理中...')

        df    = load_climate(code)
        mweph, mwepc, mwept = load_mwep(code)
        df_e  = load_energy(code)

        # 集計値
        avg_temp   = df['temp_db'].mean()
        summer_avg = df[df['month'].isin([7, 8])]['temp_db'].mean()
        winter_avg = df[df['month'].isin([1, 2, 12])]['temp_db'].mean()
        ann_ghi    = df['ghi'].sum() / 1000
        heat_kWh   = df_e['heating_kWh'].sum()
        cool_kWh   = df_e['cooling_kWh'].sum()

        all_data[code] = {
            'city_name':  city['name'],
            'avg_temp':   avg_temp,
            'summer_avg': summer_avg,
            'winter_avg': winter_avg,
            'ann_ghi':    ann_ghi,
            'heat_kWh':   heat_kWh,
            'cool_kWh':   cool_kWh,
            'ann_heat_S': abs(mweph['S'].sum()),
            'ann_heat_E': abs(mweph['E'].sum()),
            'ann_heat_N': abs(mweph['N'].sum()),
            'ann_heat_W': abs(mweph['W'].sum()),
            'ann_cool_S': mwepc['S'].sum(),
            'ann_cool_E': mwepc['E'].sum(),
            'ann_cool_N': mwepc['N'].sum(),
            'ann_cool_W': mwepc['W'].sum(),
            'net_S':      abs(mweph['S'].sum()) - mwepc['S'].sum(),
        }

        # 都市別HTMLページ生成
        html = build_city_page(code, city, df, mweph, mwepc, mwept, df_e)
        out_path = os.path.join(DOCS_DIR, f'{code}.html')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(html)
        size_kb = os.path.getsize(out_path) / 1024
        print(f'  HTML → {out_path} ({size_kb:.0f} KB)')

    # トップページ生成
    print('\n📄 トップページ（index.html）を生成中...')
    index_html = build_index_page(all_data)
    idx_path = os.path.join(DOCS_DIR, 'index.html')
    with open(idx_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    print(f'  HTML → {idx_path} ({os.path.getsize(idx_path)/1024:.0f} KB)')

    # CSVサマリー生成
    print('\n📊 集計CSVを生成中...')
    export_summary_csv(all_data)

    print('\n' + '=' * 60)
    print('✅ レポート生成完了')
    print(f'   出力先: {DOCS_DIR}/')
    for f in sorted(os.listdir(DOCS_DIR)):
        fpath = os.path.join(DOCS_DIR, f)
        if os.path.isfile(fpath):
            print(f'   📄 {f} ({os.path.getsize(fpath)/1024:.0f} KB)')
    print('=' * 60)


if __name__ == '__main__':
    main()
