import streamlit as st
from libs.sidebars import workspace_sidebar, cached_client
import pandas as pd


@st.cache_data
def convert_df(df):
    return df.to_csv().encode('utf-8')


st.title("Watchlists")
workspace_sidebar(cached_client())

watchlists = cached_client().watchlists
ws_df = pd.DataFrame(watchlists)
st.dataframe(ws_df)

if watchlists:
    option = st.selectbox(
        'What Watchlist would you like to export?',
        ws_df)

    if st.button('Generate CSV'):
        st.download_button(
            label="Download data",
            data=convert_df(cached_client().watchlist(option).as_dataframe),
            file_name=f'{option}.csv',
            mime='text/csv',
        )

