import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os

st.set_page_config(
    page_title='パッシブ住宅効果 可視化',
    page_icon='🏠',
    layout='wide',
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 定数・設定
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ZONE_COLORS = {
    '1地域': '#1a237e',
    '2地域': '#1565c0',
    '3地域': '#0288d1',
    '4地域': '#2e7d32',
    '5地域': '#f57f17',
    '6地域': '#c0392b',
    '7地域': '#7b241c',
    '8地域': '#6c3483',
}

ZONE_DESC = {
    '1地域': '最寒冷地 — 暖房中心設計・超高断熱',
    '2地域': '寒冷地 — 高断熱・南面日射取得重視',
    '3地域': '準寒冷地 — 断熱と日射遮蔽のバランス',
    '4地域': '温暖地A — 暖冷房均衡・方位設計が重要',
    '5地域': '温暖地B — 冷房負荷が増大傾向',
    '6地域': '温暖地C — 日射遮蔽・通風が重要',
    '7地域': '温暖地D — 夏の日射制御・通風が最重要',
    '8地域': '暑熱地 — 冷房中心・強力な遮熱が必須',
}

_Z = ZONE_COLORS  # shorthand

CITIES = {
    # ─── 1地域 ───
    'ASAHIKAWA': {
        'name': '旭川', 'name_en': 'Asahikawa',
        'lat': 43.7706, 'lon': 142.3653,
        'prefecture': '北海道', 'region': '北海道',
        'climate_zone': '1地域', 'color': _Z['1地域'],
    },
    # ─── 2地域 ───
    'SAPPORO': {
        'name': '札幌', 'name_en': 'Sapporo',
        'lat': 43.0642, 'lon': 141.3469,
        'prefecture': '北海道', 'region': '北海道',
        'climate_zone': '2地域', 'color': _Z['2地域'],
    },
    'AOMORI': {
        'name': '青森', 'name_en': 'Aomori',
        'lat': 40.8244, 'lon': 140.7400,
        'prefecture': '青森県', 'region': '東北',
        'climate_zone': '2地域', 'color': _Z['2地域'],
    },
    'AKITA': {
        'name': '秋田', 'name_en': 'Akita',
        'lat': 39.7181, 'lon': 140.1024,
        'prefecture': '秋田県', 'region': '東北',
        'climate_zone': '2地域', 'color': _Z['2地域'],
    },
    # ─── 3地域 ───
    'MORIOKA': {
        'name': '盛岡', 'name_en': 'Morioka',
        'lat': 39.7036, 'lon': 141.1527,
        'prefecture': '岩手県', 'region': '東北',
        'climate_zone': '3地域', 'color': _Z['3地域'],
    },
    'SENDAI': {
        'name': '仙台', 'name_en': 'Sendai',
        'lat': 38.2682, 'lon': 140.8694,
        'prefecture': '宮城県', 'region': '東北',
        'climate_zone': '3地域', 'color': _Z['3地域'],
    },
    'YAMAGATA': {
        'name': '山形', 'name_en': 'Yamagata',
        'lat': 38.2404, 'lon': 140.3633,
        'prefecture': '山形県', 'region': '東北',
        'climate_zone': '3地域', 'color': _Z['3地域'],
    },
    'NAGANO': {
        'name': '長野', 'name_en': 'Nagano',
        'lat': 36.6513, 'lon': 138.1811,
        'prefecture': '長野県', 'region': '中部',
        'climate_zone': '3地域', 'color': _Z['3地域'],
    },
    # ─── 4地域 ───
    'FUKUSHIMA': {
        'name': '福島', 'name_en': 'Fukushima',
        'lat': 37.7500, 'lon': 140.4678,
        'prefecture': '福島県', 'region': '東北',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    'MAEBASHI': {
        'name': '前橋', 'name_en': 'Maebashi',
        'lat': 36.3911, 'lon': 139.0607,
        'prefecture': '群馬県', 'region': '関東',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    'NIIGATA': {
        'name': '新潟', 'name_en': 'Niigata',
        'lat': 37.9161, 'lon': 139.0364,
        'prefecture': '新潟県', 'region': '中部',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    'TOYAMA': {
        'name': '富山', 'name_en': 'Toyama',
        'lat': 36.6953, 'lon': 137.2113,
        'prefecture': '富山県', 'region': '中部',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    'FUKUI': {
        'name': '福井', 'name_en': 'Fukui',
        'lat': 36.0652, 'lon': 136.2216,
        'prefecture': '福井県', 'region': '中部',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    'KOFU': {
        'name': '甲府', 'name_en': 'Kofu',
        'lat': 35.6642, 'lon': 138.5684,
        'prefecture': '山梨県', 'region': '中部',
        'climate_zone': '4地域', 'color': _Z['4地域'],
    },
    # ─── 5地域 ───
    'MITO': {
        'name': '水戸', 'name_en': 'Mito',
        'lat': 36.3418, 'lon': 140.4468,
        'prefecture': '茨城県', 'region': '関東',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'UTSUNOMIYA': {
        'name': '宇都宮', 'name_en': 'Utsunomiya',
        'lat': 36.5545, 'lon': 139.8832,
        'prefecture': '栃木県', 'region': '関東',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'SAITAMA': {
        'name': 'さいたま', 'name_en': 'Saitama',
        'lat': 35.8617, 'lon': 139.6453,
        'prefecture': '埼玉県', 'region': '関東',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'KANAZAWA': {
        'name': '金沢', 'name_en': 'Kanazawa',
        'lat': 36.5944, 'lon': 136.6256,
        'prefecture': '石川県', 'region': '中部',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'GIFU': {
        'name': '岐阜', 'name_en': 'Gifu',
        'lat': 35.3912, 'lon': 136.7223,
        'prefecture': '岐阜県', 'region': '中部',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'OTSU': {
        'name': '大津', 'name_en': 'Otsu',
        'lat': 35.0045, 'lon': 135.8686,
        'prefecture': '滋賀県', 'region': '近畿',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'NARA': {
        'name': '奈良', 'name_en': 'Nara',
        'lat': 34.6851, 'lon': 135.8325,
        'prefecture': '奈良県', 'region': '近畿',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'TOTTORI': {
        'name': '鳥取', 'name_en': 'Tottori',
        'lat': 35.5011, 'lon': 134.2351,
        'prefecture': '鳥取県', 'region': '中国',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    'MATSUE': {
        'name': '松江', 'name_en': 'Matsue',
        'lat': 35.4723, 'lon': 133.0505,
        'prefecture': '島根県', 'region': '中国',
        'climate_zone': '5地域', 'color': _Z['5地域'],
    },
    # ─── 6地域 ───
    'CHIBA': {
        'name': '千葉', 'name_en': 'Chiba',
        'lat': 35.6073, 'lon': 140.1063,
        'prefecture': '千葉県', 'region': '関東',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'TOKYO': {
        'name': '東京', 'name_en': 'Tokyo',
        'lat': 35.6892, 'lon': 139.6917,
        'prefecture': '東京都', 'region': '関東',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'YOKOHAMA': {
        'name': '横浜', 'name_en': 'Yokohama',
        'lat': 35.4478, 'lon': 139.6425,
        'prefecture': '神奈川県', 'region': '関東',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'SHIZUOKA': {
        'name': '静岡', 'name_en': 'Shizuoka',
        'lat': 34.9769, 'lon': 138.3831,
        'prefecture': '静岡県', 'region': '中部',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'NAGOYA': {
        'name': '名古屋', 'name_en': 'Nagoya',
        'lat': 35.1802, 'lon': 136.9066,
        'prefecture': '愛知県', 'region': '中部',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'TSU': {
        'name': '津', 'name_en': 'Tsu',
        'lat': 34.7303, 'lon': 136.5086,
        'prefecture': '三重県', 'region': '近畿',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'KYOTO': {
        'name': '京都', 'name_en': 'Kyoto',
        'lat': 35.0211, 'lon': 135.7556,
        'prefecture': '京都府', 'region': '近畿',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'OSAKA': {
        'name': '大阪', 'name_en': 'Osaka',
        'lat': 34.6864, 'lon': 135.5200,
        'prefecture': '大阪府', 'region': '近畿',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'KOBE': {
        'name': '神戸', 'name_en': 'Kobe',
        'lat': 34.6913, 'lon': 135.1830,
        'prefecture': '兵庫県', 'region': '近畿',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'WAKAYAMA': {
        'name': '和歌山', 'name_en': 'Wakayama',
        'lat': 34.2261, 'lon': 135.1675,
        'prefecture': '和歌山県', 'region': '近畿',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'OKAYAMA': {
        'name': '岡山', 'name_en': 'Okayama',
        'lat': 34.6618, 'lon': 133.9350,
        'prefecture': '岡山県', 'region': '中国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'HIROSHIMA': {
        'name': '広島', 'name_en': 'Hiroshima',
        'lat': 34.3853, 'lon': 132.4553,
        'prefecture': '広島県', 'region': '中国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'YAMAGUCHI': {
        'name': '山口', 'name_en': 'Yamaguchi',
        'lat': 34.1861, 'lon': 131.4706,
        'prefecture': '山口県', 'region': '中国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'TOKUSHIMA': {
        'name': '徳島', 'name_en': 'Tokushima',
        'lat': 34.0657, 'lon': 134.5593,
        'prefecture': '徳島県', 'region': '四国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'TAKAMATSU': {
        'name': '高松', 'name_en': 'Takamatsu',
        'lat': 34.3401, 'lon': 134.0434,
        'prefecture': '香川県', 'region': '四国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'MATSUYAMA': {
        'name': '松山', 'name_en': 'Matsuyama',
        'lat': 33.8416, 'lon': 132.7658,
        'prefecture': '愛媛県', 'region': '四国',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    'OITA': {
        'name': '大分', 'name_en': 'Oita',
        'lat': 33.2382, 'lon': 131.6126,
        'prefecture': '大分県', 'region': '九州',
        'climate_zone': '6地域', 'color': _Z['6地域'],
    },
    # ─── 7地域 ───
    'KOCHI': {
        'name': '高知', 'name_en': 'Kochi',
        'lat': 33.5597, 'lon': 133.5311,
        'prefecture': '高知県', 'region': '四国',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'FUKUOKA': {
        'name': '福岡', 'name_en': 'Fukuoka',
        'lat': 33.6064, 'lon': 130.4181,
        'prefecture': '福岡県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'SAGA': {
        'name': '佐賀', 'name_en': 'Saga',
        'lat': 33.2494, 'lon': 130.2990,
        'prefecture': '佐賀県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'NAGASAKI': {
        'name': '長崎', 'name_en': 'Nagasaki',
        'lat': 32.7503, 'lon': 129.8777,
        'prefecture': '長崎県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'KUMAMOTO': {
        'name': '熊本', 'name_en': 'Kumamoto',
        'lat': 32.7898, 'lon': 130.7417,
        'prefecture': '熊本県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'MIYAZAKI': {
        'name': '宮崎', 'name_en': 'Miyazaki',
        'lat': 31.9111, 'lon': 131.4239,
        'prefecture': '宮崎県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    'KAGOSHIMA': {
        'name': '鹿児島', 'name_en': 'Kagoshima',
        'lat': 31.5603, 'lon': 130.5603,
        'prefecture': '鹿児島県', 'region': '九州',
        'climate_zone': '7地域', 'color': _Z['7地域'],
    },
    # ─── 8地域 ───
    'NAHA': {
        'name': '那覇', 'name_en': 'Naha',
        'lat': 26.2124, 'lon': 127.6809,
        'prefecture': '沖縄県', 'region': '沖縄',
        'climate_zone': '8地域', 'color': _Z['8地域'],
    },
}

MONTHS_JP = ['1月', '2月', '3月', '4月', '5月', '6月',
             '7月', '8月', '9月', '10月', '11月', '12月']

DIRECTIONS = {'S': '南', 'E': '東', 'N': '北', 'W': '西'}
DIR_COLORS = {'S': '#e74c3c', 'E': '#e67e22', 'N': '#3498db', 'W': '#27ae60'}
DIR_SYMBOLS = {'S': '↓', 'E': '→', 'N': '↑', 'W': '←'}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# データ読み込み（キャッシュ付き）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

@st.cache_data
def has_data(city_code: str) -> bool:
    """シミュレーションデータが揃っているか確認する"""
    wep = os.path.join(BASE_DIR, '地点データ', city_code, 'wep_base',
                       f'MWEPt({city_code}・省エネ).csv')
    epw = os.path.join(BASE_DIR, '地点データ', city_code, 'site', 'eplusout.csv')
    return os.path.isfile(wep) and os.path.isfile(epw)


@st.cache_data
def load_climate_data(city_code):
    """EPW由来の時間別気象データを読み込む"""
    filepath = os.path.join(BASE_DIR, '地点データ', city_code, 'site', 'eplusout.csv')
    col_names = [
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
    df = pd.read_csv(filepath, skiprows=1, header=None, names=col_names)
    df['datetime'] = df['datetime'].str.strip()
    df['month'] = df['datetime'].str[0:2].str.strip().astype(int)
    df['day'] = df['datetime'].str[3:5].str.strip().astype(int)
    df['hour'] = df['datetime'].str[7:9].str.strip().astype(int)
    df['ghi'] = df['solar_diffuse'] + df['solar_direct']
    return df


@st.cache_data
def load_mwep_data(city_code):
    """月別窓面エネルギー性能（MWEP）データを読み込む"""
    base = os.path.join(BASE_DIR, '地点データ', city_code, 'wep_base')
    mwept = pd.read_csv(f"{base}/MWEPt({city_code}・省エネ).csv").iloc[:12]
    mweph = pd.read_csv(f"{base}/MWEPh({city_code}・省エネ).csv").iloc[:12]
    mwepc = pd.read_csv(f"{base}/MWEPc({city_code}・省エネ).csv").iloc[:12]
    for df in [mwept, mweph, mwepc]:
        df.index = range(1, 13)
    return mwept, mweph, mwepc


@st.cache_data
def load_energy_data(city_code):
    """理想空調負荷（Ideal Loads）データを読み込む"""
    filepath = os.path.join(
        BASE_DIR, '地点データ', city_code,
        'grade4 Zone Ideal Loads Supply Enegy', 'eplusout.csv',
    )
    df_raw = pd.read_csv(filepath, header=0)
    cols = list(df_raw.columns)

    heating_cols = [c for c in cols if 'Heating Energy' in c]
    sens_cool_cols = [c for c in cols if 'Sensible Cooling Energy' in c]
    lat_cool_cols = [c for c in cols if 'Latent Cooling Energy' in c]

    df_raw['heating_kWh'] = df_raw[heating_cols].sum(axis=1) / 3_600_000
    df_raw['cooling_kWh'] = (
        df_raw[sens_cool_cols].sum(axis=1) + df_raw[lat_cool_cols].sum(axis=1)
    ) / 3_600_000

    dt_col = cols[0]
    df_raw['month'] = df_raw[dt_col].str.strip().str[0:2].astype(int)

    # 室別年間合計
    zone_names_jp = {
        'LIVINGDINING': 'LDK', 'BEDROOM': '寝室', 'KIDSROOM1': '子供部屋1',
        'KIDSROOM2': '子供部屋2', 'KITCHEN': 'キッチン', 'BATHROOM': '浴室',
        'JAPANESESTYLEROOM': '和室', 'CLOSET': '収納', '1F_HOLE': '1F廊下',
        '1F_TOILET': '1Fトイレ', '1F_WASHROOM': '1F洗面', '2FHOLE': '2F廊下',
        '2FWASHROOM': '2F洗面',
    }

    zone_annual = {}
    for h_col in heating_cols:
        zone_raw = h_col.split(' IDEAL')[0]
        c_col = [c for c in sens_cool_cols if c.startswith(zone_raw)]
        zone_jp = next(
            (jp for en, jp in zone_names_jp.items() if en in zone_raw.upper()),
            zone_raw.split('_')[0],
        )
        zone_annual[zone_jp] = {
            'heating': df_raw[h_col].sum() / 3_600_000,
            'cooling': df_raw[c_col[0]].sum() / 3_600_000 if c_col else 0,
        }

    return df_raw, zone_annual


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 地図作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def create_satellite_map(selected_city):
    """Esri衛星画像を用いたGoogle Earth風マップを生成"""
    m = folium.Map(
        location=[37.0, 136.5],
        zoom_start=5,
        tiles=None,
        prefer_canvas=True,
    )

    # 衛星画像タイル（Esri WorldImagery - APIキー不要）
    folium.TileLayer(
        tiles=(
            'https://server.arcgisonline.com/ArcGIS/rest/services/'
            'World_Imagery/MapServer/tile/{z}/{y}/{x}'
        ),
        attr='Esri WorldImagery',
        name='衛星画像',
        overlay=False,
        control=True,
    ).add_to(m)

    # 地名ラベルオーバーレイ
    folium.TileLayer(
        tiles=(
            'https://server.arcgisonline.com/ArcGIS/rest/services/'
            'Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}'
        ),
        attr='Esri',
        name='地名',
        overlay=True,
        control=True,
    ).add_to(m)

    for code, city in CITIES.items():
        selected = code == selected_city
        avail = has_data(code)

        if selected:
            size = 28
            bg = city['color']
            border = '3px solid white'
            shadow = '0 0 12px rgba(255,255,255,0.9)'
            opacity = '1'
            cursor = 'pointer'
        elif avail:
            size = 20
            bg = city['color']
            border = '2px solid rgba(255,255,255,0.8)'
            shadow = '0 2px 6px rgba(0,0,0,0.5)'
            opacity = '0.9'
            cursor = 'pointer'
        else:
            size = 13
            bg = '#888888'
            border = '1.5px solid rgba(200,200,200,0.6)'
            shadow = '0 1px 3px rgba(0,0,0,0.3)'
            opacity = '0.45'
            cursor = 'default'

        icon_html = (
            f'<div style="background:{bg};border:{border};border-radius:50%;'
            f'width:{size}px;height:{size}px;box-shadow:{shadow};'
            f'cursor:{cursor};opacity:{opacity};"></div>'
        )

        tooltip_text = (
            f"📍 {city['name']} ({city['climate_zone']}) — クリックして選択"
            if avail or selected
            else f"🔒 {city['name']} — データ準備中"
        )

        popup_html = (
            f"<b>{city['name']}</b><br>"
            f"{city['prefecture']} / {city['region']}<br>"
            f"省エネ地域区分: <b>{city['climate_zone']}</b><br>"
            f"緯度: {city['lat']}°N / 経度: {city['lon']}°E<br>"
            + ('✅ データ収録済み' if avail else '🔒 データ準備中')
        )

        folium.Marker(
            location=[city['lat'], city['lon']],
            tooltip=tooltip_text,
            popup=folium.Popup(popup_html, max_width=220),
            icon=folium.DivIcon(
                html=icon_html,
                icon_size=(size, size),
                icon_anchor=(size // 2, size // 2),
            ),
        ).add_to(m)

        # 都市名ラベル（収録済みと選択中のみ）
        if avail or selected:
            label_bg = 'background: rgba(0,0,0,0.45); padding: 2px 5px; border-radius: 4px;' if selected else ''
            label_html = (
                f'<div style="color:white;font-weight:bold;font-size:12px;'
                f'text-shadow:1px 1px 3px black,-1px -1px 3px black,'
                f'1px -1px 3px black,-1px 1px 3px black;white-space:nowrap;{label_bg}">'
                f'{city["name"]}</div>'
            )
            folium.Marker(
                location=[city['lat'] + 0.38, city['lon']],
                icon=folium.DivIcon(
                    html=label_html,
                    icon_size=(80, 24),
                    icon_anchor=(40, 12),
                ),
            ).add_to(m)

    folium.LayerControl().add_to(m)
    return m


def find_nearest_city(lat, lon):
    """クリック位置に最も近い都市コードを返す"""
    min_dist = float('inf')
    nearest = 'TOKYO'
    for code, city in CITIES.items():
        dist = ((city['lat'] - lat) ** 2 + (city['lon'] - lon) ** 2) ** 0.5
        if dist < min_dist:
            min_dist = dist
            nearest = code
    return nearest


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# チャート作成
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def chart_temperature(df):
    """月別気温プロファイル（最低・平均・最高）+ 相対湿度"""
    monthly = df.groupby('month').agg(
        temp_avg=('temp_db', 'mean'),
        temp_min=('temp_db', 'min'),
        temp_max=('temp_db', 'max'),
        rh_avg=('rh', 'mean'),
    ).reset_index()

    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.65, 0.35],
        shared_xaxes=True,
        subplot_titles=['外気温 [°C]', '相対湿度 [%]'],
        vertical_spacing=0.12,
    )

    # 最高気温
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['temp_max'],
        name='最高気温', mode='lines+markers',
        line=dict(color='#e74c3c', width=2),
        marker=dict(size=7),
    ), row=1, col=1)

    # 最低気温（塗りつぶし）
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['temp_min'],
        name='最低気温', mode='lines+markers',
        fill='tonexty', fillcolor='rgba(231,76,60,0.12)',
        line=dict(color='#3498db', width=2),
        marker=dict(size=7),
    ), row=1, col=1)

    # 平均気温
    fig.add_trace(go.Scatter(
        x=MONTHS_JP, y=monthly['temp_avg'],
        name='平均気温', mode='lines+markers',
        line=dict(color='#f39c12', width=2.5, dash='dash'),
        marker=dict(size=9, symbol='diamond'),
    ), row=1, col=1)

    # 快適ゾーン参考線
    for y, text, color in [(18, '暖房基準 18°C', 'limegreen'), (26, '冷房基準 26°C', 'orange')]:
        fig.add_hline(y=y, line_dash='dot', line_color=color, line_width=1.5,
                      annotation_text=text, annotation_position='right',
                      annotation_font_color=color, row=1, col=1)

    # 相対湿度
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['rh_avg'],
        name='相対湿度', marker_color='rgba(52,152,219,0.7)',
        text=monthly['rh_avg'].round(1).astype(str) + '%',
        textposition='outside',
        textfont=dict(size=10),
    ), row=2, col=1)

    fig.add_hline(y=60, line_dash='dot', line_color='gray', line_width=1, row=2, col=1)

    fig.update_layout(
        height=520, legend=dict(orientation='h', y=1.02, x=0, font=dict(size=12)),
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=60, b=10),
    )
    fig.update_xaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')

    return fig, monthly


def chart_solar_wind(df):
    """日射量 + 風況"""
    monthly = df.groupby('month').agg(
        ghi_total=('ghi', 'sum'),
        diffuse_avg=('solar_diffuse', 'mean'),
        direct_avg=('solar_direct', 'mean'),
        wind_avg=('wind_speed', 'mean'),
    ).reset_index()
    monthly['ghi_kWh'] = monthly['ghi_total'] / 1000.0

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=['月別全天日射量 [kWh/m²/月]', '月別平均日射成分 [W/m²]'],
        horizontal_spacing=0.12,
    )

    # 全天日射量
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['ghi_kWh'],
        name='全天日射量', marker_color='#f39c12',
        text=monthly['ghi_kWh'].round(1), textposition='outside',
        textfont=dict(size=10),
    ), row=1, col=1)

    # 散乱・直達
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['diffuse_avg'],
        name='散乱日射', marker_color='#F9E79F',
    ), row=1, col=2)

    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['direct_avg'],
        name='直達日射', marker_color='#E67E22',
    ), row=1, col=2)

    fig.update_layout(
        barmode='stack',
        height=380,
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.18, x=0.1),
        margin=dict(l=10, r=10, t=50, b=50),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')

    return fig, monthly


def chart_wind_rose(df):
    """プロット対話式風配図"""
    df_wind = df[df['wind_speed'] > 0.3].copy()

    dirs_jp = [
        '北', 'N北北東', '北東', '東北東', '東', '東南東', '南東', '南南東',
        '南', '南南西', '南西', '西南西', '西', '西北西', '北西', '北北西',
    ]
    theta_vals = [i * 22.5 for i in range(16)]

    df_wind['dir_bin'] = ((df_wind['wind_dir'] + 11.25) / 22.5).astype(int) % 16

    speed_ranges = [
        (0, 2, '< 2 m/s', '#D6EAF8'),
        (2, 4, '2〜4 m/s', '#5DADE2'),
        (4, 6, '4〜6 m/s', '#1A5276'),
        (6, 8, '6〜8 m/s', '#F39C12'),
        (8, 999, '> 8 m/s', '#C0392B'),
    ]

    fig = go.Figure()
    for lo, hi, label, color in speed_ranges:
        mask = (df_wind['wind_speed'] >= lo) & (df_wind['wind_speed'] < hi)
        counts = df_wind[mask].groupby('dir_bin').size().reindex(range(16), fill_value=0)
        fig.add_trace(go.Barpolar(
            r=counts.values,
            theta=theta_vals,
            name=label,
            marker_color=color,
            hovertemplate='方角: %{theta}°<br>頻度: %{r}時間<extra>' + label + '</extra>',
        ))

    fig.update_layout(
        title='年間風配図',
        polar=dict(
            radialaxis=dict(visible=True, tickfont=dict(size=10)),
            angularaxis=dict(
                ticktext=dirs_jp,
                tickvals=theta_vals,
                direction='clockwise',
                rotation=90,
            ),
        ),
        height=460,
        showlegend=True,
        legend=dict(x=1.08, y=0.5),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def chart_heatmap_temperature(df):
    """時刻 × 月の気温ヒートマップ"""
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

    fig.add_hline(y=8, line_dash='dot', line_color='white',
                  annotation_text='日出頃(6〜8時)', annotation_font_color='white')
    fig.add_hline(y=18, line_dash='dot', line_color='white',
                  annotation_text='日没頃(18時)', annotation_font_color='white')

    fig.update_layout(
        title='時刻別・月別 平均気温 [°C]',
        xaxis_title='月',
        yaxis_title='時刻',
        height=480,
        paper_bgcolor='rgba(0,0,0,0)',
    )
    return fig


def chart_mwep_heating(mweph):
    """月別・方位別 パッシブ太陽熱暖房効果（MWEPh）"""
    fig = go.Figure()
    for d, name in DIRECTIONS.items():
        fig.add_trace(go.Bar(
            name=f'{name}面 ({d})',
            x=MONTHS_JP,
            y=mweph[d].values,
            marker_color=DIR_COLORS[d],
            hovertemplate=f'%{{x}}<br>{name}面: %{{y:.1f}} MJ/m²<extra></extra>',
        ))

    fig.add_hline(y=0, line_color='black', line_width=1.5)
    fig.add_hrect(y0=-500, y1=0, fillcolor='rgba(52,152,219,0.05)', line_width=0)
    fig.add_annotation(
        x=0.99, y=0.01, xref='paper', yref='paper',
        text='▼ 暖房負荷削減域（パッシブ効果）',
        showarrow=False, xanchor='right', yanchor='bottom',
        font=dict(color='steelblue', size=11),
        bgcolor='rgba(255,255,255,0.75)', borderpad=4,
    )

    fig.update_layout(
        title='パッシブ太陽熱 暖房効果 [MJ/m²/月] — 方位別比較',
        barmode='group',
        height=420,
        xaxis_title='月',
        yaxis_title='MJ/m²',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='v',
            x=1.01, y=1,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='rgba(180,180,180,0.6)',
            borderwidth=1,
            font=dict(size=13),
        ),
        margin=dict(l=10, r=120, t=60, b=40),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')
    return fig


def chart_mwep_cooling(mwepc):
    """月別・方位別 日射による冷房負荷増加（MWEPc）"""
    fig = go.Figure()
    for d, name in DIRECTIONS.items():
        fig.add_trace(go.Bar(
            name=f'{name}面 ({d})',
            x=MONTHS_JP,
            y=mwepc[d].values,
            marker_color=DIR_COLORS[d],
            hovertemplate=f'%{{x}}<br>{name}面: %{{y:.1f}} MJ/m²<extra></extra>',
        ))

    fig.add_hline(y=0, line_color='black', line_width=1.5)
    fig.add_hrect(y0=0, y1=500, fillcolor='rgba(231,76,60,0.05)', line_width=0)
    fig.add_annotation(
        x=0.99, y=0.99, xref='paper', yref='paper',
        text='▲ 冷房負荷増加域（日射遮蔽が必要）',
        showarrow=False, xanchor='right', yanchor='top',
        font=dict(color='crimson', size=11),
        bgcolor='rgba(255,255,255,0.75)', borderpad=4,
    )

    fig.update_layout(
        title='日射による冷房負荷増加 [MJ/m²/月] — 方位別比較',
        barmode='group',
        height=420,
        xaxis_title='月',
        yaxis_title='MJ/m²',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='v',
            x=1.01, y=1,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='rgba(180,180,180,0.6)',
            borderwidth=1,
            font=dict(size=13),
        ),
        margin=dict(l=10, r=120, t=60, b=40),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')
    return fig


def chart_mwep_net(mwept):
    """月別・方位別 正味窓面熱的影響（MWEPt）"""
    fig = go.Figure()
    for d, name in DIRECTIONS.items():
        vals = mwept[d].values
        fig.add_trace(go.Bar(
            name=f'{name}面 ({d})',
            x=MONTHS_JP,
            y=vals,
            marker_color=DIR_COLORS[d],
            hovertemplate=f'%{{x}}<br>{name}面: %{{y:.1f}} MJ/m²<extra></extra>',
        ))

    fig.add_hline(y=0, line_color='black', line_width=1.5)

    fig.update_layout(
        title='窓面透過日射の正味熱的影響 (MWEPt) [MJ/m²/月]',
        barmode='group',
        height=420,
        xaxis_title='月',
        yaxis_title='MJ/m²（負値 = 暖房有利、正値 = 冷房不利）',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='v',
            x=1.01, y=1,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='rgba(180,180,180,0.6)',
            borderwidth=1,
            font=dict(size=13),
        ),
        margin=dict(l=10, r=120, t=60, b=40),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.4)')
    return fig


def chart_annual_radar(mweph, mwepc):
    """年間パッシブ効果のレーダーチャート（方位別）"""
    dirs = list(DIRECTIONS.keys())
    dir_names = [f'{DIRECTIONS[d]}面 ({d})' for d in dirs]

    annual_heat = [abs(mweph[d].sum()) for d in dirs]
    annual_cool = [mwepc[d].sum() for d in dirs]
    annual_net = [abs(mweph[d].sum()) - mwepc[d].sum() for d in dirs]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=annual_heat + [annual_heat[0]],
        theta=dir_names + [dir_names[0]],
        fill='toself',
        name='暖房パッシブ効果 [MJ/m²/年]',
        line=dict(color='#e74c3c', width=2),
        fillcolor='rgba(231,76,60,0.2)',
    ))

    fig.add_trace(go.Scatterpolar(
        r=annual_cool + [annual_cool[0]],
        theta=dir_names + [dir_names[0]],
        fill='toself',
        name='冷房負荷増加 [MJ/m²/年]',
        line=dict(color='#3498db', width=2),
        fillcolor='rgba(52,152,219,0.2)',
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, tickfont=dict(size=11)),
            angularaxis=dict(tickfont=dict(size=13)),
        ),
        height=450,
        title='年間パッシブ効果 — 方位別比較',
        showlegend=True,
        legend=dict(x=0, y=-0.1, orientation='h'),
        paper_bgcolor='rgba(0,0,0,0)',
    )

    return fig, dict(zip(dirs, annual_heat)), dict(zip(dirs, annual_cool))


def chart_passive_monthly_balance(mweph, mwepc):
    """月別パッシブ収支（全方位合計）"""
    monthly_heat = [abs(mweph['S'].iloc[i]) + abs(mweph['E'].iloc[i]) +
                    abs(mweph['N'].iloc[i]) + abs(mweph['W'].iloc[i])
                    for i in range(12)]
    monthly_cool = [mwepc['S'].iloc[i] + mwepc['E'].iloc[i] +
                    mwepc['N'].iloc[i] + mwepc['W'].iloc[i]
                    for i in range(12)]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly_heat,
        name='暖房パッシブ効果合計', marker_color='rgba(231,76,60,0.8)',
    ))
    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=[-v for v in monthly_cool],
        name='冷房負荷増加合計（逆符号）', marker_color='rgba(52,152,219,0.8)',
    ))
    fig.add_trace(go.Scatter(
        x=MONTHS_JP,
        y=[h - c for h, c in zip(monthly_heat, monthly_cool)],
        name='正味パッシブ収支',
        mode='lines+markers',
        line=dict(color='black', width=2.5, dash='dot'),
        marker=dict(size=9, symbol='diamond'),
    ))

    fig.add_hline(y=0, line_color='gray', line_width=1)
    fig.update_layout(
        title='月別パッシブ収支（全方位合計）[MJ/m²/月]',
        barmode='overlay',
        height=420,
        xaxis_title='月',
        yaxis_title='MJ/m²',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(
            orientation='v',
            x=1.01, y=1,
            xanchor='left', yanchor='top',
            bgcolor='rgba(255,255,255,0.85)',
            bordercolor='rgba(180,180,180,0.6)',
            borderwidth=1,
            font=dict(size=13),
        ),
        margin=dict(l=10, r=140, t=60, b=40),
    )
    return fig


def chart_energy_demand(df_energy, zone_annual, city_name):
    """月別暖冷房エネルギー需要 + 室別割合"""
    monthly = df_energy.groupby('month').agg(
        heating=('heating_kWh', 'sum'),
        cooling=('cooling_kWh', 'sum'),
    ).reset_index()

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            '月別暖冷房エネルギー需要 [kWh/月]',
            '室別年間暖房エネルギー割合',
        ],
        column_widths=[0.58, 0.42],
        specs=[[{"type": "xy"}, {"type": "domain"}]],
    )

    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['heating'],
        name='暖房', marker_color='rgba(231,76,60,0.85)',
    ), row=1, col=1)

    fig.add_trace(go.Bar(
        x=MONTHS_JP, y=monthly['cooling'],
        name='冷房', marker_color='rgba(52,152,219,0.85)',
    ), row=1, col=1)

    # 室別暖房パイチャート
    zone_h = {k: v['heating'] for k, v in zone_annual.items() if v['heating'] > 0.01}
    if zone_h:
        top_zones = sorted(zone_h.items(), key=lambda x: x[1], reverse=True)[:8]
        labels, values = zip(*top_zones)
        fig.add_trace(go.Pie(
            labels=labels,
            values=values,
            hole=0.38,
            textinfo='label+percent',
            textfont=dict(size=11),
            marker=dict(
                colors=px.colors.qualitative.Set3[:len(labels)],
                line=dict(color='white', width=1.5),
            ),
        ), row=1, col=2)

    fig.update_layout(
        barmode='group',
        height=420,
        title=f'暖冷房エネルギー需要 — {city_name}',
        plot_bgcolor='rgba(245,247,250,1)', paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation='h', y=-0.18, x=0.1),
        margin=dict(l=10, r=10, t=60, b=60),
    )
    return fig, monthly


def make_recommendation_cards(mweph, mwepc, monthly_temp, city_name=None):
    """設計推奨事項を生成する"""
    ann_heat = {d: abs(mweph[d].sum()) for d in 'SENW'}
    ann_cool = {d: mwepc[d].sum() for d in 'SENW'}
    net = {d: ann_heat[d] - ann_cool[d] for d in 'SENW'}

    best_dir = max(net, key=net.get)
    worst_dir = min(net, key=net.get)

    avg_temp = monthly_temp['temp_avg'].mean()
    _winter = monthly_temp[monthly_temp['month'].isin([1, 2, 12])]['temp_avg']
    _summer = monthly_temp[monthly_temp['month'].isin([7, 8])]['temp_avg']
    winter_avg = float(_winter.mean()) if len(_winter) > 0 else 0.0
    summer_avg = float(_summer.mean()) if len(_summer) > 0 else 25.0

    summer_cool_S = mwepc['S'].iloc[5:9].sum()  # Jun-Sep
    winter_heat_S = abs(mweph['S'].iloc[[0, 1, 2, 10, 11]].sum())  # Jan-Mar, Nov-Dec

    recs = []

    south_msg = ('✅ 南面窓の拡大を推奨。冬の日射取得が期待できます。'
                 if net['S'] > 0
                 else '⚠️ 冷房増加が大きいため、日射遮蔽と開口部面積のバランスが重要です。')
    recs.append({
        'icon': '🪟',
        'title': '南面窓の最適化',
        'content': (
            f"南面窓の年間パッシブ暖房効果は **{ann_heat['S']:.0f} MJ/m²**、"
            f"冷房増加は **{ann_cool['S']:.0f} MJ/m²**。\n\n"
            f"{south_msg}"
        ),
        'color': '#e74c3c',
    })

    season_icon = '❄️' if winter_avg < 5 else '☀️'
    winter_msg = '⚠️ 寒冷地。断熱・日射取得が重要。' if winter_avg < 5 else '温暖。暖房は限定的。'
    summer_msg = '⚠️ 高温。日射遮蔽が必須。' if summer_avg > 28 else '比較的過ごしやすい。'
    recs.append({
        'icon': season_icon,
        'title': '暖房・冷房シーズン特性',
        'content': (
            f"年間平均気温: **{avg_temp:.1f}°C**\n\n"
            f"冬季平均（12〜2月）: **{winter_avg:.1f}°C** → {winter_msg}\n\n"
            f"夏季平均（7〜8月）: **{summer_avg:.1f}°C** → {summer_msg}"
        ),
        'color': '#3498db',
    })

    recs.append({
        'icon': '📐',
        'title': f'最有利方位: {DIRECTIONS[best_dir]}面 ({best_dir})',
        'content': (
            f"正味パッシブ収支が最大の方位は **{DIRECTIONS[best_dir]}面（{best_dir}）** "
            f"（年間 **{net[best_dir]:.0f} MJ/m²** の正味暖房貢献）。\n\n"
            f"リビングや大きな開口部は {DIRECTIONS[best_dir]}面 への配置が有効です。"
        ),
        'color': '#27ae60',
    })

    shade_msg = ('⚠️ 夏の南面日射遮蔽（庇・ルーバー）が非常に重要です。'
                 if summer_cool_S > 200
                 else '夏の日射遮蔽は標準的な措置で対応できます。')
    recs.append({
        'icon': '🌿',
        'title': '日射遮蔽の重要方位',
        'content': (
            f"夏季（6〜9月）の南面冷房増加負荷: **{summer_cool_S:.0f} MJ/m²**\n\n"
            f"{shade_msg}\n\n"
            f"東西面は朝夕の低角度日射に注意。垂直ルーバーや植栽が効果的です。"
        ),
        'color': '#f39c12',
    })

    return recs


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# メインアプリ
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    # カスタムCSS
    st.markdown("""
    <style>
    .main { padding-top: 0.5rem; }
    .stTabs [data-baseweb="tab-list"] { gap: 12px; }
    .stTabs [data-baseweb="tab"] {
        height: 44px; padding: 0 20px;
        font-size: 15px; font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 12px; padding: 16px 20px; margin: 6px 0;
        border-left: 5px solid;
    }
    .rec-card {
        border-radius: 10px; padding: 18px; margin: 10px 0;
        border-left: 5px solid; background: #fafbfc;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .city-badge {
        display: inline-block; padding: 4px 12px;
        border-radius: 20px; color: white; font-weight: bold;
        font-size: 14px; margin-right: 8px;
    }
    .zone-badge {
        display: inline-block; padding: 2px 8px;
        border-radius: 12px; color: white; font-weight: bold;
        font-size: 12px; margin-right: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ヘッダー
    st.title('🏠 パッシブ住宅効果 可視化システム')
    st.markdown(
        '地点を選択すると、EPWデータに基づく**パッシブ住宅設計効果**を多角的に可視化します。'
        '　| 　データ出典：EnergyPlus気象シミュレーション（省エネ基準）'
    )

    # ━━━━ セッション初期化 ━━━━
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = 'TOKYO'
    if 'zone_filter' not in st.session_state:
        st.session_state.zone_filter = '全地域'

    # ━━━━ 地図セクション ━━━━
    st.markdown('---')
    st.subheader('📍 地点選択 — 衛星画像マップ（Google Earth風）')
    st.caption('🖱️ マップのマーカーをクリック、または左パネルのボタンで地点を選択してください')

    col_sidebar, col_map = st.columns([1, 3])

    # ─── 地点選択パネル ───
    with col_sidebar:
        st.markdown('#### 省エネ地域区分')

        zone_options = ['全地域'] + list(ZONE_COLORS.keys())
        sel_zone = st.selectbox(
            '地域区分でフィルタ',
            zone_options,
            index=zone_options.index(st.session_state.zone_filter),
            key='zone_select',
            label_visibility='collapsed',
        )
        st.session_state.zone_filter = sel_zone

        if sel_zone != '全地域':
            zc = ZONE_COLORS[sel_zone]
            st.markdown(
                f'<div style="background:{zc}22;border-left:4px solid {zc};'
                f'padding:6px 10px;border-radius:6px;font-size:0.82em;color:#333">'
                f'<b style="color:{zc}">{sel_zone}</b> {ZONE_DESC[sel_zone]}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('---')

        # 地点一覧（選択ゾーンでフィルタ）
        if sel_zone == '全地域':
            zone_cities = CITIES
        else:
            zone_cities = {k: v for k, v in CITIES.items()
                           if v['climate_zone'] == sel_zone}

        avail_cities = {k: v for k, v in zone_cities.items() if has_data(k)}
        unavail_cities = {k: v for k, v in zone_cities.items() if not has_data(k)}

        if avail_cities:
            st.markdown('**✅ データ収録済み**')
            for code, city in avail_cities.items():
                is_sel = (code == st.session_state.selected_city)
                zc = city['color']
                label = f"{'✔ ' if is_sel else ''}{city['name']}　{city['prefecture'][:3]}"
                if st.button(
                    label,
                    key=f'btn_{code}',
                    type='primary' if is_sel else 'secondary',
                    use_container_width=True,
                ):
                    st.session_state.selected_city = code
                    st.rerun()

        if unavail_cities:
            unavail_count = len(unavail_cities)
            with st.expander(f'🔒 準備中の地点 ({unavail_count}地点)'):
                for code, city in unavail_cities.items():
                    zc = city['color']
                    st.markdown(
                        f'<span class="zone-badge" style="background:{zc}">'
                        f'{city["climate_zone"]}</span>'
                        f'<span style="color:#888;font-size:0.9em">{city["name"]} '
                        f'({city["prefecture"][:3]})</span>',
                        unsafe_allow_html=True,
                    )

        # ゾーン凡例
        st.markdown('---')
        st.markdown('**地域区分 凡例**')
        for zone, color in ZONE_COLORS.items():
            count_total = sum(1 for v in CITIES.values() if v['climate_zone'] == zone)
            count_avail = sum(1 for k, v in CITIES.items()
                              if v['climate_zone'] == zone and has_data(k))
            st.markdown(
                f'<span class="zone-badge" style="background:{color}">{zone}</span>'
                f'<span style="font-size:0.8em;color:#555">{count_avail}/{count_total}地点</span>',
                unsafe_allow_html=True,
            )

    # ─── 地図 ───
    with col_map:
        m = create_satellite_map(st.session_state.selected_city)
        map_result = st_folium(m, width='100%', height=480,
                               returned_objects=['last_object_clicked'])

        # マーカークリック処理
        if (
            map_result
            and map_result.get('last_object_clicked')
            and map_result['last_object_clicked'] is not None
        ):
            clicked = map_result['last_object_clicked']
            if 'lat' in clicked and 'lng' in clicked:
                nearest = find_nearest_city(clicked['lat'], clicked['lng'])
                if nearest != st.session_state.selected_city:
                    st.session_state.selected_city = nearest
                    st.rerun()

    # ━━━━ 地点情報バナー ━━━━
    city_code = st.session_state.selected_city
    city = CITIES[city_code]
    zc = city['color']
    avail = has_data(city_code)

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(90deg, {zc}22, transparent);
            border-left: 5px solid {zc};
            border-radius: 8px; padding: 12px 20px; margin: 12px 0;
        ">
        <span class="city-badge" style="background:{zc}">{city['name']}</span>
        <span class="zone-badge" style="background:{zc}">{city['climate_zone']}</span>
        <strong>{city['prefecture']} / {city['region']}</strong>
        &nbsp;|&nbsp; 緯度: <strong>{city['lat']}°N</strong>
        &nbsp;|&nbsp; 経度: <strong>{city['lon']}°E</strong>
        &nbsp;|&nbsp; {'✅ データ収録済み' if avail else '🔒 データ準備中'}
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ━━━━ データ未収録の場合 ━━━━
    if not avail:
        st.info(
            f'**{city["name"]}（{city["prefecture"]}）** のシミュレーションデータはまだ収録されていません。\n\n'
            '左パネルの「✅ データ収録済み」から地点を選択してください。',
        )
        st.markdown('#### 現在データ収録済みの地点')
        avail_list = [(k, v) for k, v in CITIES.items() if has_data(k)]
        cols = st.columns(len(avail_list))
        for col, (code, c) in zip(cols, avail_list):
            with col:
                if st.button(
                    f"{c['name']}\n{c['climate_zone']}",
                    key=f'quick_{code}',
                    use_container_width=True,
                ):
                    st.session_state.selected_city = code
                    st.rerun()
        return

    # ━━━━ データ読み込み ━━━━
    with st.spinner('シミュレーションデータを読み込み中...'):
        df_climate = load_climate_data(city_code)
        mwept, mweph, mwepc = load_mwep_data(city_code)
        df_energy, zone_annual = load_energy_data(city_code)

    # ━━━━ サマリーKPI ━━━━
    st.markdown('---')
    _, monthly_temp = chart_temperature(df_climate)

    ann_heat_S = abs(mweph['S'].sum())
    ann_cool_S = mwepc['S'].sum()
    total_heating = df_energy['heating_kWh'].sum()
    total_cooling = df_energy['cooling_kWh'].sum()
    ann_avg_temp = monthly_temp['temp_avg'].mean()

    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric('📍 地点', city['name'], city['prefecture'])
    with k2:
        st.metric('🌡️ 年平均気温', f'{ann_avg_temp:.1f}°C',
                  f"夏{monthly_temp[monthly_temp['month'].isin([7,8])]['temp_avg'].mean():.1f}°C /"
                  f" 冬{monthly_temp[monthly_temp['month'].isin([1,2,12])]['temp_avg'].mean():.1f}°C")
    with k3:
        st.metric('☀️ 南面 暖房効果', f'{ann_heat_S:.0f} MJ/m²',
                  '（年間・省エネ基準）')
    with k4:
        st.metric('🌤️ 南面 冷房増加', f'{ann_cool_S:.0f} MJ/m²',
                  '（年間・省エネ基準）')
    with k5:
        net_S = ann_heat_S - ann_cool_S
        st.metric('⚖️ 南面 正味収支', f'{net_S:.0f} MJ/m²',
                  '正値=暖房有利' if net_S > 0 else '負値=冷房不利')

    # ━━━━ タブコンテンツ ━━━━
    st.markdown('---')
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        '🌡️ EPW気候データ',
        '☀️ パッシブ効果（方位別）',
        '📊 パッシブ収支分析',
        '⚡ エネルギー需要',
        '📋 設計推奨事項',
    ])

    # ─── Tab1: 気候データ ───
    with tab1:
        st.subheader(f'EPW気象データ — {city["name"]}')
        st.markdown(
            'EnergyPlusシミュレーションで使用した気象データ（EPW）の統計。'
            '外気温、湿度、日射量、風況を月別・時刻別に可視化します。'
        )

        fig_temp, monthly_temp = chart_temperature(df_climate)
        st.plotly_chart(fig_temp, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            fig_solar, monthly_solar = chart_solar_wind(df_climate)
            st.plotly_chart(fig_solar, use_container_width=True)

        with c2:
            fig_wr = chart_wind_rose(df_climate)
            st.plotly_chart(fig_wr, use_container_width=True)

        st.markdown('#### 時刻別・月別 気温分布（ヒートマップ）')
        fig_hmap = chart_heatmap_temperature(df_climate)
        st.plotly_chart(fig_hmap, use_container_width=True)

        with st.expander('月別統計データ（数値）'):
            disp = monthly_temp.copy()
            disp.insert(0, '月', MONTHS_JP)
            disp = disp.drop(columns=['month'])
            disp.columns = ['月', '平均気温[°C]', '最低気温[°C]', '最高気温[°C]', '平均相対湿度[%]']
            st.dataframe(disp.set_index('月').round(1), use_container_width=True)

    # ─── Tab2: パッシブ効果（方位別） ───
    with tab2:
        st.subheader(f'パッシブ太陽熱効果 — {city["name"]}')
        st.markdown("""
        **MWEP（月別窓面エネルギー性能）** に基づく方位別・月別のパッシブ効果分析。
        - **MWEPh**: 窓からの日射取得による **暖房負荷削減効果** （負値ほど暖房効果大）
        - **MWEPc**: 窓からの日射による **冷房負荷増加量** （正値ほど夏の遮蔽が重要）
        - **MWEPt**: 正味の窓面熱的影響（負 = 暖房有利、正 = 冷房不利）
        """)

        sub_tab1, sub_tab2, sub_tab3 = st.tabs([
            '🔴 暖房パッシブ効果 (MWEPh)',
            '🔵 冷房負荷増加 (MWEPc)',
            '⚖️ 正味熱的影響 (MWEPt)',
        ])

        with sub_tab1:
            st.plotly_chart(chart_mwep_heating(mweph), use_container_width=True)
            with st.expander('数値データ（MWEPh）'):
                df_h = mweph.copy()
                df_h.index = MONTHS_JP[:len(df_h)]
                df_h.index.name = '月'
                st.dataframe(df_h.round(2), use_container_width=True)

        with sub_tab2:
            st.plotly_chart(chart_mwep_cooling(mwepc), use_container_width=True)
            with st.expander('数値データ（MWEPc）'):
                df_c = mwepc.copy()
                df_c.index = MONTHS_JP[:len(df_c)]
                df_c.index.name = '月'
                st.dataframe(df_c.round(2), use_container_width=True)

        with sub_tab3:
            st.plotly_chart(chart_mwep_net(mwept), use_container_width=True)
            with st.expander('数値データ（MWEPt）'):
                df_t = mwept.copy()
                df_t.index = MONTHS_JP[:len(df_t)]
                df_t.index.name = '月'
                st.dataframe(df_t.round(2), use_container_width=True)

    # ─── Tab3: パッシブ収支分析 ───
    with tab3:
        st.subheader(f'年間パッシブ収支分析 — {city["name"]}')
        st.markdown('方位別の年間パッシブ効果をレーダーチャートと収支グラフで可視化します。')

        c1, c2 = st.columns([1, 1])
        with c1:
            fig_radar, ann_heat, ann_cool = chart_annual_radar(mweph, mwepc)
            st.plotly_chart(fig_radar, use_container_width=True)

        with c2:
            # 方位別KPI
            st.markdown('#### 方位別 年間パッシブ効果')
            for d, dname in DIRECTIONS.items():
                net = ann_heat[d] - ann_cool[d]
                bar_heat = min(ann_heat[d] / max(max(ann_heat.values()), 1) * 100, 100)
                bar_cool = min(ann_cool[d] / max(max(ann_cool.values()), 1) * 100, 100)
                net_color = '#27ae60' if net > 0 else '#e74c3c'
                st.markdown(f"""
                <div class="metric-card" style="border-left-color:{DIR_COLORS[d]}">
                <b>{DIR_SYMBOLS[d]} {dname}面 ({d})</b><br>
                🔴 暖房効果: <b>{ann_heat[d]:.0f} MJ/m²</b>
                <div style="background:#eee;border-radius:4px;height:8px;margin:4px 0">
                  <div style="background:#e74c3c;height:8px;border-radius:4px;width:{bar_heat:.0f}%"></div>
                </div>
                🔵 冷房増加: <b>{ann_cool[d]:.0f} MJ/m²</b>
                <div style="background:#eee;border-radius:4px;height:8px;margin:4px 0">
                  <div style="background:#3498db;height:8px;border-radius:4px;width:{bar_cool:.0f}%"></div>
                </div>
                ⚖️ 正味: <b style="color:{net_color}">{net:+.0f} MJ/m²</b>
                </div>
                """, unsafe_allow_html=True)

        st.markdown('#### 月別パッシブ収支（全方位合計）')
        fig_bal = chart_passive_monthly_balance(mweph, mwepc)
        st.plotly_chart(fig_bal, use_container_width=True)

    # ─── Tab4: エネルギー需要 ───
    with tab4:
        st.subheader(f'暖冷房エネルギー需要 — {city["name"]}')
        st.markdown(
            'EnergyPlusによる**Ideal Loads**シミュレーション結果。'
            '省エネ基準（等級4相当）の住宅モデルにおける暖冷房負荷。'
        )

        fig_energy, monthly_energy = chart_energy_demand(df_energy, zone_annual, city['name'])
        st.plotly_chart(fig_energy, use_container_width=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric('🔴 年間暖房需要', f'{total_heating:.0f} kWh',
                      f'月平均 {total_heating/12:.0f} kWh')
        with c2:
            st.metric('🔵 年間冷房需要', f'{total_cooling:.0f} kWh',
                      f'月平均 {total_cooling/12:.0f} kWh')
        with c3:
            ratio = (total_heating / (total_heating + total_cooling) * 100
                     if (total_heating + total_cooling) > 0 else 0)
            st.metric('⚖️ 暖房比率', f'{ratio:.1f}%',
                      f'冷房比率 {100-ratio:.1f}%')

        with st.expander('月別エネルギー需要データ（数値）'):
            me = monthly_energy.copy()
            me.insert(0, '月', MONTHS_JP)
            me = me.drop(columns=['month'])
            me.columns = ['月', '暖房[kWh]', '冷房[kWh]']
            me['合計[kWh]'] = me['暖房[kWh]'] + me['冷房[kWh]']
            st.dataframe(me.set_index('月').round(1), use_container_width=True)

    # ─── Tab5: 設計推奨事項 ───
    with tab5:
        st.subheader(f'パッシブ住宅 設計推奨事項 — {city["name"]}')
        st.markdown(
            'EPWデータとパッシブ効果分析に基づく、この地点に適した**設計指針**を提示します。'
        )

        _, monthly_temp = chart_temperature(df_climate)
        recs = make_recommendation_cards(mweph, mwepc, monthly_temp, city['name'])

        for rec in recs:
            st.markdown(f"""
            <div class="rec-card" style="border-left-color:{rec['color']}">
            <h4>{rec['icon']} {rec['title']}</h4>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(rec['content'])
            st.markdown('')

        st.markdown('---')
        st.markdown('#### 🗺️ データ収録済み地点 比較')

        compare_data = []
        compare_colors = []
        for code, c in CITIES.items():
            if not has_data(code):
                continue
            try:
                _, mh, mc = load_mwep_data(code)
                compare_data.append({
                    '地点': c['name'],
                    '地域区分': c['climate_zone'],
                    '南面暖房効果[MJ/m²]': round(abs(mh['S'].sum()), 0),
                    '南面冷房増加[MJ/m²]': round(mc['S'].sum(), 0),
                    '南面正味収支[MJ/m²]': round(abs(mh['S'].sum()) - mc['S'].sum(), 0),
                    '北面暖房効果[MJ/m²]': round(abs(mh['N'].sum()), 0),
                    '北面冷房増加[MJ/m²]': round(mc['N'].sum(), 0),
                })
                compare_colors.append(c['color'])
            except Exception:
                pass

        if compare_data:
            n_avail = len(compare_data)
            st.caption(f'収録済み {n_avail}地点の年間正味パッシブ収支（南面）を比較します')

            df_compare = pd.DataFrame(compare_data).set_index('地点')
            st.dataframe(df_compare, use_container_width=True)

            fig_comp = go.Figure()
            fig_comp.add_trace(go.Bar(
                x=[d['地点'] for d in compare_data],
                y=[d['南面暖房効果[MJ/m²]'] for d in compare_data],
                name='南面暖房効果',
                marker_color=compare_colors,
                opacity=0.85,
            ))
            fig_comp.add_trace(go.Bar(
                x=[d['地点'] for d in compare_data],
                y=[-d['南面冷房増加[MJ/m²]'] for d in compare_data],
                name='南面冷房増加（逆符号）',
                marker_color=compare_colors,
                opacity=0.4,
            ))
            fig_comp.add_trace(go.Scatter(
                x=[d['地点'] for d in compare_data],
                y=[d['南面正味収支[MJ/m²]'] for d in compare_data],
                name='正味収支',
                mode='markers+lines',
                marker=dict(size=14, color='black'),
                line=dict(color='black', dash='dot', width=2),
            ))
            fig_comp.add_hline(y=0, line_color='gray', line_width=1)
            fig_comp.update_layout(
                title=f'{n_avail}地点 南面パッシブ効果比較',
                barmode='overlay',
                height=400,
                xaxis_title='地点',
                yaxis_title='MJ/m² (年間)',
                plot_bgcolor='rgba(245,247,250,1)',
                paper_bgcolor='rgba(0,0,0,0)',
                legend=dict(orientation='h', y=1.02, x=0),
            )
            st.plotly_chart(fig_comp, use_container_width=True)


main()
