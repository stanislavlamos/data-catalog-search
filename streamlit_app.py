import streamlit as st
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(
    page_title="Query Matching",
    page_icon="🔍",
    layout="wide"
)

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'query_matching'

if 'selected_datasets' not in st.session_state:
    st.session_state.selected_datasets = []

if 'search_query' not in st.session_state:
    st.session_state.search_query = ''

pages = {
    'query_matching': st.Page("pages/query_matching_page.py", title="Query Matching", icon="🔍"),
}

pg = st.navigation([pages[st.session_state.current_page]])
pg.run()
