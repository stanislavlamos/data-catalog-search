import streamlit as st
from src.fe_handler import get_language


if 'loading' not in st.session_state:
    st.session_state.loading = False

st.title("⚙️ Configuration")

st.write("Configure the application settings")

query = st.text_area("Query", value=st.session_state.config.get('query', ''), help="Enter your search query")

llm_model = st.selectbox(
    "LLM Model",
    options=["gpt-5", "gpt-4.1", "claude_sonnet_4.5", "claude_sonnet_4"],
    index=0 if 'llm_model' not in st.session_state.config else ["gpt-5", "gpt-4.1", "claude_sonnet_4.5", "claude_sonnet_4"].index(st.session_state.config.get('llm_model', 'gpt-5')),
    help="Select the LLM model to use for SPARQL query generation"
)

llm_providers = {
    "gpt-5": "openai",
    "gpt-4.1": "openai",
    "claude_sonnet_4.5": "anthropic",
    "claude_sonnet_4": "anthropic"
}

st.session_state.config = {
    'query': query,
    'model_name': llm_model,
    "llm_provider": llm_providers[llm_model]
}

st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("← Back", use_container_width=True):
        st.session_state.loading = False
        st.session_state.current_page = 'homepage'
        st.rerun()
with col2:
    if st.button("Next →", use_container_width=True, type="primary"):
        if query.strip():
            st.session_state.fnc_to_call = get_language
            st.session_state.params_for_fnc = {
                "query": query,
                "model_name": llm_model,
                "llm_provider": llm_providers[llm_model]
            }

            st.session_state.loading_msg = "Detecting language..."
            st.session_state.loading = True
            st.session_state.next_page = 'language'
            st.rerun()
        else:
            st.error("Please enter a non-empty query before proceeding")
