import streamlit as st
from PIL import Image
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title='環境設計ツール',
    page_icon='🗾',
    layout='wide',
)

st.title('🏚️ 環境設計ツール')
st.sidebar.success('ページを選択してください')

MONTHS = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']

location = ['TOKYO', 'SAPPORO', 'OSAKA', 'FUKUOKA', 'KAGOSHIMA']
select_location = st.selectbox('地域を選択してください:', location)
site = str(select_location)

# ── 気象画像（既存PNGをそのまま表示）────────────────────────────
col1, col2, col3 = st.columns(3)
with col1:
    st.header('外気温')
    st.image(Image.open(Rf'Tem/{site}_tem.png'))
with col2:
    st.header('相対湿度')
    st.image(Image.open(Rf'Rh/{site}_Rh.png'))
with col3:
    st.header('風配図')
    st.image(Image.open(Rf'wind/{site}_windrose.png'))

# ── MWEPデータ読み込み ────────────────────────────────────────────
wepc = pd.read_csv(Rf'地点データ/{site}/wep_base/MWEPc({site}・省エネ).csv')
weph = pd.read_csv(Rf'地点データ/{site}/wep_base/MWEPh({site}・省エネ).csv')
wept = pd.read_csv(Rf'地点データ/{site}/wep_base/MWEPt({site}・省エネ).csv')

months = MONTHS[:len(wepc)]

def make_mwep_fig(df, title, colors):
    """4方位のMWEPを2×2サブプロットで表示（Plotly版）"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=['南(S)', '北(N)', '東(E)', '西(W)'],
        vertical_spacing=0.15, horizontal_spacing=0.08,
    )
    for direction, row, col in [('S', 1, 1), ('N', 1, 2), ('E', 2, 1), ('W', 2, 2)]:
        fig.add_trace(
            go.Bar(x=months, y=df[direction].values,
                   name=direction, marker_color=colors.get(direction, '#4472C4'),
                   showlegend=False),
            row=row, col=col,
        )
    fig.update_layout(
        title_text=title, height=520,
        plot_bgcolor='rgba(220,220,220,0.3)', paper_bgcolor='white',
        margin=dict(l=20, r=20, t=60, b=20),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor='rgba(180,180,180,0.5)')
    return fig

st.title(f'MWEPc（冷房増加）　省エネ基準　地点: {site}')
st.plotly_chart(make_mwep_fig(
    wepc, f'日射冷房増加負荷 [MJ/m²/月] — {site}',
    {'S': '#5BC0DE', 'N': '#5BC0DE', 'E': '#5BC0DE', 'W': '#5BC0DE'},
), use_container_width=True)
st.dataframe(wepc.T, height=200)

st.title(f'MWEPh（暖房効果）　省エネ基準　地点: {site}')
st.plotly_chart(make_mwep_fig(
    weph, f'パッシブ暖房効果 [MJ/m²/月] — {site}',
    {'S': '#DC3545', 'N': '#DC3545', 'E': '#DC3545', 'W': '#DC3545'},
), use_container_width=True)
st.dataframe(weph.T, height=200)

st.title(f'MWEPt（正味）　省エネ基準　地点: {site}')
st.plotly_chart(make_mwep_fig(
    wept, f'正味窓面熱的影響 [MJ/m²/月] — {site}',
    {'S': '#DC3545', 'N': '#0D6EFD', 'E': '#FD7E14', 'W': '#198754'},
), use_container_width=True)
st.dataframe(wept.T, height=200)
