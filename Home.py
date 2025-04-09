import streamlit as st
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from math import pi
from windrose import WindroseAxes
import folium
from streamlit_folium import folium_static
import plotly.express as px
import altair as alt
from PIL import Image

st.set_page_config(
    page_title='Multipage App',
    page_icon='🗾',
    layout='wide',
)




st.title('環境設計ツール')
st.sidebar.success('Select a page above')
location=['TOKYO','SAPPORO','OSAKA','FUKUOKA','KAGOSHIMA']
select_location =st.selectbox('地域を選択してください:',location)
point_data=pd.read_csv('地点データ/5地点の緯度経度.csv',index_col=None, header=0,sep=',',engine='python')
site=str(select_location)
point=list(point_data[site])
map = folium.Map(location=point,zoom_start=4.7,width=450,height=380)

col1, col2 = st.columns(2)
img1=Image.open(Rf"image\標準住宅モデル.png")
with col1:
    folium.Marker(point,popup=site,icon=folium.Icon(color='red')).add_to(map)
    folium_static(map)
with col2:
   st.header("標準住宅モデル")
   st.image(img1)


#気象データの選択
wea=pd.read_csv(Rf"{site}/site/eplusout.csv")
month=wea['Date/Time'].str[:3].astype(int)
date=wea['Date/Time'].str[4:6].astype(int)
time=wea['Date/Time'].str[6:10].astype(int)
Md=wea['Date/Time'].str[:6]
datetime=[month,date,time,Md]
datetime=pd.DataFrame(datetime)
datetime=datetime.T
datetime.columns=['month','date','time','month/date']
Wea = pd.concat([datetime, wea], axis=1)


load=pd.read_csv(Rf"{site}/grade4 Zone Ideal Loads Supply Enegy/eplusout.csv")
Load=pd.concat([datetime, load], axis=1)

A=list(Wea.columns.str.endswith('Site Outdoor Air Drybulb Temperature [C](Hourly)') )
A_list=[]
for i in range(len(Wea.columns)):
    if A[i]==True:
        A_list.append(i)
Tem=Wea.iloc[:,A_list]
Tem = pd.concat([datetime, Tem], axis=1)
Tem_max=np.empty(12)
Tem_min=np.empty(12)
Tem_ave=np.empty(12)
for j in range(1,13):
    Temm=Tem[Tem['month']==j]
    Temm=Temm.reset_index(drop=True)
    Teml=Temm['Environment:Site Outdoor Air Drybulb Temperature [C](Hourly)'].astype(float)
    Tem_max[j-1]=max(Teml)
    Tem_min[j-1]=min(Teml)
    Tem_ave[j-1]=sum(Teml) / len(Teml)
Tem_month=[Tem_max,Tem_min,Tem_ave]
Tem_month=pd.DataFrame(Tem_month)
Tem_month.columns=['January',
 'February',
 'March',
 'April',
 'May',
 'June',
 'July',
 'August',
 'September',
 'October',
 'November',
 'December']
Tem_month.index=['最高気温[℃]','最低気温[℃]','平均気温[℃]']
Tem_month=Tem_month.T

Tem_data=Tem_month.T

B=list(Load.columns.str.endswith('Air Sensible Heating Energy [J](Hourly)') )
B_list=[]
for i in range(len(Load.columns)):
    if B[i]==True:
        B_list.append(i)
Load_01=Load.iloc[:,B_list]
Load_01mass=(Load_01.sum(axis=1))/10**6
C=list(Load.columns.str.endswith('Air Sensible Cooling Energy [J](Hourly)') )
C_list=[]
for i in range(len(Load.columns)):
    if C[i]==True:
        C_list.append(i)
Load_02=Load.iloc[:,C_list]
Load_02mass=(Load_02.sum(axis=1))/10**6
D=list(Load.columns.str.endswith('Loads Supply Air Latent Cooling Energy [J](Hourly)') )
D_list=[]
for i in range(len(Load.columns)):
    if D[i]==True:
        D_list.append(i)
Load_03=Load.iloc[:,D_list]
Load_03mass=(Load_03.sum(axis=1))/10**6
Load_mass=[Load_01mass,Load_02mass,Load_03mass]
Load_mass=pd.DataFrame(Load_mass)
Load_mass=Load_mass.T
Load_mass.columns=['暖房負荷','冷房顕熱負荷','冷房潜熱負荷']
Load_mass = pd.concat([datetime, Load_mass], axis=1)
H_el=np.empty(12)#暖房負荷の月ごとの積算
C_el=np.empty(12)#冷房負荷の月ごとの積算
C_el1=np.empty(12)#冷房顕熱負荷の月ごとの積算
C_el2=np.empty(12)#冷房潜熱負荷の月ごとの積算
for j in range(1,13):
    Load_massm=Load_mass[Load_mass['month']==j]
    H_e=Load_massm['暖房負荷'].astype(float)
    C_e1=Load_massm['冷房顕熱負荷'].astype(float)
    C_e2=Load_massm['冷房潜熱負荷'].astype(float)
    H_el[j-1]=sum(H_e)
    C_el[j-1]=sum(C_e1)+sum(C_e2)
    C_el1[j-1]=sum(C_e1)
    C_el2[j-1]=sum(C_e2)

Load_month=[H_el,C_el1,C_el2]
Load_month=pd.DataFrame(Load_month)
Load_month=Load_month.T
Load_month.columns=['暖房負荷','冷房顕熱負荷','冷房潜熱負荷']
Month=['January',
 'February',
 'March',
 'April',
 'May',
 'June',
 'July',
 'August',
 'September',
 'October',
 'November',
 'December']
Load_data=Load_month.T
Load_data.columns=Month
def plot_temperature():
    sns.set(style="whitegrid",font=["Times New Roman","Yu Gothic"])
    fig = plt.figure(figsize=(15,7),dpi=250,facecolor='silver')
    plt.title(f'月の最高気温・最低気温・平均気温の推移 地点:{site}')
    plt.plot(Tem_month['最高気温[℃]'],color='orange', label='最高気温[℃]',linestyle='dashed',marker="D",markersize=8,alpha=0.6)
    plt.plot(Tem_month['平均気温[℃]'],color='green', label='平均気温[℃]',linestyle='dashed',marker="D",markersize=8,alpha=0.6)
    plt.plot(Tem_month['最低気温[℃]'],color='deepskyblue', label='最低気温[℃]',linestyle='dashed',marker="D",markersize=8,alpha=0.6)
    plt.legend(fontsize=14,ncol=1)
    plt.ylabel('温度[℃]',size=14)
    plt.xlabel('Month',size=14)
    plt.ylim([-15,42])
    plt.yticks(np.arange(-15,42+0.01,3))
    st.pyplot(plt)
def plot_load():
    sns.set(style="darkgrid",font=["Times New Roman","Yu Gothic"])
    fig = plt.figure(figsize=(15,7),dpi=250,facecolor='silver')
    plt.title(f'月の最高気温・最低気温・平均気温の推移 地点:{site}')
    w=0.4
    plt.title(f"年間月積算負荷                site:{site}", fontsize = 20) # (3)タイトル
    plt.bar(Load_month.index,Load_month['暖房負荷'],width=-w,label='Heating energy[MJ]',color='r',ec='gray',tick_label=Month,align='edge')
    plt.bar(Load_month.index,Load_month['冷房顕熱負荷'],bottom=Load_month['冷房潜熱負荷'],width=w,label='Cooling  Sensible energy[MJ]',tick_label=Month,color='dodgerblue',ec='gray',align='edge')
    plt.bar(Load_month.index,Load_month['冷房潜熱負荷'],width=w,label='Cooling  Latent energy[MJ]',tick_label=Month,color='lightblue',ec='gray',align='edge')
    plt.xlabel("Month", fontsize = 10)
    plt.ylabel("Energy[MJ]", fontsize = 10)
    plt.legend(loc=0,fontsize=14)
    plt.tick_params(labelsize=12)
    plt.grid(True)
    st.pyplot(plt)
    


st.header(f'　地点:{site}')

    
# グラフを表示するボタンを表示する
if st.button('気象データを読み取る'):
    st.title(f'気温の推移 地点:{site}')
    plot_temperature()
    st.dataframe(Tem_data, height=150)
    st.title('月ごとの負荷推移(省エネ基準)')
    plot_load()
    st.dataframe(Load_data)
    
    
Month=['January',
 'February',
 'March',
 'April',
 'May',
 'June',
 'July',
 'August',
 'September',
 'October',
 'November',
 'December']


Month=pd.DataFrame(Month)
Month.columns=['month']




