import streamlit as st
from PIL import Image

st.set_page_config(
    page_title='Multipage App',
    page_icon='🗾',
)

st.title('🏚️環境設計ツール')
st.sidebar.success('オプション')
location=['Tokyo','Sapporo','Osaka','Fukuoka','Kagoshima']
select_location =st.selectbox('地域を選択してください:',location)
site=select_location
col1, col2, col3 = st.columns(3)
img1=Image.open(Rf"Tem\{site}_tem.png")

with col1:
   st.header("外気温")
   st.image(img1)
img2=Image.open(Rf"Rh\{site}_Rh.png")

with col2:
   st.header("相対湿度")
   st.image(img2)
img3=Image.open(Rf"wind\{site}_windrose.png")
with col3:
   st.header("風配図")
   st.image(img3)
