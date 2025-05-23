import streamlit as st
from PIL import Image
import pandas as pd
import matplotlib.pyplot as plt
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

wepc_data=wepc.T

weph_data=weph.T

wept_data=wept.T

st.title(f"wepc 省エネ基準 地点:{site}")
fig = plt.figure(figsize=(15,7),dpi=250,facecolor='silver')
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)
ax1.bar(wepc.index,wepc['S'],color='lightblue')
ax2.bar(wepc.index,wepc['N'],color='lightblue')
ax3.bar(wepc.index,wepc['E'],color='lightblue')
ax4.bar(wepc.index,wepc['W'],color='lightblue')
st.pyplot(fig)
st.dataframe(wepc_data, height=200)

st.title(f"weph 省エネ基準地点:{site}")
fig = plt.figure(figsize=(15,7),dpi=250,facecolor='silver')
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)
ax1.bar(weph.index,weph['S'],color='crimson')
ax2.bar(weph.index,weph['N'],color='crimson')
ax3.bar(weph.index,weph['E'],color='crimson')
ax4.bar(weph.index,weph['W'],color='crimson')
st.pyplot(fig)
st.dataframe(weph_data, height=200)
st.title(f"wept 省エネ基準 地点:{site}")
fig = plt.figure(figsize=(15,7),dpi=250,facecolor='silver')
ax1 = fig.add_subplot(2, 2, 1)
ax2 = fig.add_subplot(2, 2, 2)
ax3 = fig.add_subplot(2, 2, 3)
ax4 = fig.add_subplot(2, 2, 4)
ax1.bar(wept.index,wept['S'],color='crimson')
ax2.bar(wept.index,wept['N'],color='blue')
ax3.bar(wept.index,wept['E'],color='darkorange')
ax4.bar(wept.index,wept['W'],color='green')
st.pyplot(fig)
st.dataframe(wept_data, height=200)
