import streamlit as st
import time
import numpy as np

st.set_page_config(
    page_title='Multipage App',
    page_icon='🗾',
)

st.title('環境設計ツール')
st.sidebar.success('Select a page above')
st.markdown("# Plotting Demo")
st.sidebar.header("Plotting Demo")
st.write(
    """This demo illustrates a combination of plotting and animation with
Streamlit. We're generating a bunch of random numbers in a loop for around
5 seconds. Enjoy!"""
)

progress_bar = st.sidebar.progress(0)
status_text = st.sidebar.empty()
last_rows = np.random.randn(1, 1)
chart = st.line_chart(last_rows)

for i in range(1, 101):
    new_rows = last_rows[-1, :] + np.random.randn(5, 1).cumsum(axis=0)
    status_text.text("%i%% Complete" % i)
    chart.add_rows(new_rows)
    progress_bar.progress(i)
    last_rows = new_rows
    time.sleep(0.05)

progress_bar.empty()

# Streamlit widgets automatically run the script from top to bottom. Since
# this button is not connected to any other logic, it just causes a plain
# rerun.

st.title('月ごとの負荷推移(省エネ基準)')
st.header(f'　地点:{site}')
month = st.slider(label="月を選択してください",
    min_value=1,
    max_value=12,
    step=1,
    format='%d月',
)
st.subheader(f'{month}月')
st.bar_chart(df_monthly.loc[month])