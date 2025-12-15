import streamlit as st
from src.fe_handler import get_timeframe


if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = None

language_to_print = {
    "cs": "Czech",
    "en": "English",
    "other": "Other (Czech will be used for further processing)"
}

st.title("Language Detection")
st.write("Detected language of your input query")

detected_text = st.session_state.result
if isinstance(detected_text, dict) and st.session_state.result.get('text') is not None:
    detected_text = st.session_state.result.get('text')
    st.session_state.selected_language = st.session_state.result.get('text')
else:
    detected_text = None

lang_key = detected_text if detected_text is not None else st.session_state.selected_language
if lang_key is None or lang_key not in language_to_print:
    lang_key = 'cs'

st.write(f"**Detected Language:** {language_to_print[lang_key]}")
st.markdown("---")

change_lang = st.selectbox("Do you wish to change the detected language?", ["No", "Yes"], key="change_lang_select")

if change_lang == "Yes":
    lang_options = ["Czech", "English"]
    selected = st.selectbox("Select language", lang_options, key="lang_select")
    lang_code = {"Czech": "cs", "English": "cs"}[selected] #{"Czech": "cs", "English": "en"}[selected], fixed to cs since we are working on the NKOD data
    st.session_state.selected_language = lang_code
elif isinstance(detected_text, dict) and detected_text is not None:
    st.session_state.selected_language = st.session_state.result.get('text')
    if st.session_state.selected_language == "other":
        st.session_state.selected_language = "cs"

st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("← Back", use_container_width=True):
        st.session_state.loading = False
        st.session_state.current_page = 'config'
        st.rerun()
with col2:
    if st.button("Next →", use_container_width=True, type="primary"):
        st.session_state.loading = True
        st.session_state.next_page = 'timeframe'
        st.session_state.loading_msg = "Detecting timeframe..."
        st.session_state.fnc_to_call = get_timeframe
        st.session_state.params_for_fnc = {
            "query": st.session_state.config.get('query'),
            "model_name": st.session_state.config.get('model_name'),
            "llm_provider": st.session_state.config.get('llm_provider')
        }
        st.rerun()
