import streamlit as st
import pandas as pd
from src.services.nkod_data_processor import NkodDataProcessor

catalog_name = "nkod"
nkod_data_processor = NkodDataProcessor(catalog_name)
df = pd.read_csv(nkod_data_processor.ofn_metadata_csv_path)

st.title("NKOD data of our App")

# Render dataframe
st.dataframe(df, width=2000, height=800)
