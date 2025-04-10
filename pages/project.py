import streamlit as st
from PIL import Image
import pandas as pd
st.set_page_config(
    page_title='Multipage App',
    page_icon='🗾',
)

st.title('🏚️環境設計ツール')
st.sidebar.success('オプション')
st.title('環境設計ツール')
st.sidebar.success('Select a page above')
location=['TOKYO','SAPPORO','OSAKA','FUKUOKA','KAGOSHIMA']
select_location =st.selectbox('地域を選択してください:',location)
site=str(select_location)
col1, col2, col3 = st.columns(3)
img1=Image.open(Rf"Tem/{site}_tem.png")

with col1:
   st.header("外気温")
   st.image(img1)
img2=Image.open(Rf"Rh/{site}_Rh.png")

with col2:
   st.header("相対湿度")
   st.image(img2)
img3=Image.open(Rf"wind/{site}_windrose.png")
with col3:
   st.header("風配図")
   st.image(img3)
wepc=pd.read_csv(Rf"地点データ/{site}/wep_base/MWEPc({site}・省エネ).csv")
weph=pd.read_csv(Rf"地点データ/{site}/wep_base/MWEPh({site}・省エネ).csv")
wept=pd.read_csv(Rf"地点データ/{site}/wep_base/MWEPt({site}・省エネ).csv")
st.dataframe(wepc, height=150)
st.dataframe(weph, height=150)
st.dataframe(wept, height=150)
