import os
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

st.title("NKOD LLM Search")

st.markdown("This application is designed to help you query NKOD data catalog using natural language. The app allows to configure your preferred LLM and translate your natural language query to SPARQL.")

st.markdown("""
### Process Flow:

1. **Configuration** - Input the query and configure the LLM of your choice

2. **Language Detection** - Detect the language of the user query

3. **Timeframe Detection** - Detect the timeframe of the user query

4. **Query matching** - Natural language query matched with relevant datasets from NKOD

5. **Recap of matched datasets** - Confirm the relevant NKOD datasets for the subsequent SPARQL generation

6. **SPARQL query generation** - Generated SPARQL query together with the output when executed

""")

st.markdown("---")
st.markdown("Ready to get started?")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    st.link_button(
        "Inspect available data",
        os.getenv("DATA_VIEWER_URL"),   # <-- replace with your real link
        use_container_width=True
    )

with col3:
    if st.button("Next →", use_container_width=True, type="primary"):
        st.session_state.loading = True
        st.session_state.next_page = 'config'
        st.rerun()
