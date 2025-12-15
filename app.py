import streamlit as st


st.set_page_config(
    page_title="NKOD LLM search",
    page_icon="📝",
    layout="wide"
)

if 'config' not in st.session_state:
    st.session_state.config = {}

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'homepage'

if 'loading' not in st.session_state:
    st.session_state.loading = False

if 'loading_msg' not in st.session_state:
    st.session_state.loading_msg = ""

if 'fnc_to_call' not in st.session_state:
    st.session_state.fnc_to_call = None

if 'params_for_fnc' not in st.session_state:
    st.session_state.params_for_fnc = {}

if 'result' not in st.session_state:
    st.session_state.result = {}

pages = {
    'homepage': st.Page("pages/home_page.py", title="Homepage", icon="🏠"),
    'config': st.Page("pages/config_page.py", title="Config", icon="⚙️"),
    'language': st.Page("pages/language_page.py", title="Language Detection", icon="📝"),
    'timeframe': st.Page("pages/timeframe_page.py", title="Timeframe Detection", icon="⚙️"),
    'query_matching': st.Page("pages/query_matching_page.py", title="Query Matching", icon="📋"),
    'query_matching_recap': st.Page("pages/query_matching_recap_page.py", title="Query Matching Recap", icon="📊"),
    'sparql_generation': st.Page("pages/sparql_generation_page.py", title="SPARQL Query Generation", icon="🔧")
}

with st.sidebar:
    st.header("Current configuration")
    query = st.session_state.config.get('query', None)
    if query is not None and query:
        st.info(f"**Current Query:**\n\n{query}")
    else:
        st.warning("No query configured yet")

    st.markdown("---")
    st.subheader("Navigation")

    for key, page in pages.items():
        if key == st.session_state.current_page:
            st.markdown(f"**→ {page.title}**")
        else:
            st.markdown(f"   {page.title}")

    st.markdown("---")

    if st.button("🔄 Start Over", use_container_width=True, type="secondary"):
        st.session_state.clear()
        st.session_state.loading = True
        st.rerun()

if st.session_state.loading:
    st.markdown("""
        <style>
        .stApp > header {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    with st.spinner(st.session_state.loading_msg):
        if 'next_page' in st.session_state:
            st.session_state.result = st.session_state.fnc_to_call(**st.session_state.params_for_fnc) if st.session_state.fnc_to_call else None
            next_page = st.session_state.next_page
            st.session_state.loading = False
            st.session_state.current_page = next_page
            del st.session_state.next_page
            st.rerun()
        else:
            for key in list(st.session_state.keys()):
                if key != 'loading':
                    continue
                    #del st.session_state[key]
            st.session_state.loading = False
            st.session_state.current_page = 'homepage'
            st.rerun()
else:
    pg = st.navigation([pages[st.session_state.current_page]])
    pg.run()
