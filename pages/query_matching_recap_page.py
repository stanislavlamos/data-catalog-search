import streamlit as st
from src.fe_handler import generate_sparql


st.title("📊 Query Matching Recap")
st.markdown("Review your query configuration and selected datasets")
st.markdown("---")

st.subheader("Query Configuration")
config_col1, config_col2 = st.columns(2)

with config_col1:
    st.markdown("**Original Query:**")
    st.info(st.session_state.config.get('query', 'N/A'))

with config_col2:
    st.markdown("**LLM Model:**")
    st.info(st.session_state.config.get('model_name', 'N/A'))

st.markdown("---")

st.subheader("Extracted Information")
extract_col1, extract_col2 = st.columns(2)

with extract_col1:
    st.markdown("**Detected Language:**")
    language_map = {
        "cs": "Czech",
        "en": "English",
        "other": "Other (Czech will be used)"
    }
    selected_lang = st.session_state.get('selected_language', 'N/A')
    display_lang = language_map.get(selected_lang, selected_lang)
    st.success(display_lang)

with extract_col2:
    st.markdown("**Detected Timeframe:**")
    st.success(f"{st.session_state.selected_timeframe}")

st.markdown("---")
st.subheader(f"Selected Datasets ({len(st.session_state.get('selected_datasets', []))})")

if not st.session_state.get('selected_datasets', []):
    st.warning("No datasets selected")
else:
    st.markdown("""
    <style>
    .recap-dataset-card {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: white;
        transition: all 0.2s;
    }
    .recap-dataset-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .recap-dataset-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
    }
    .recap-dataset-uri {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    .recap-rdf-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    .recap-rdf-available {
        background-color: #d1fae5;
        color: #065f46;
    }
    .recap-rdf-unavailable {
        background-color: #fee2e2;
        color: #991b1b;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.container(height=400):
        for idx, dataset in enumerate(st.session_state.selected_datasets, 1):
            with st.container(border=True):
                st.markdown(f"<p class='recap-dataset-title'>{idx}. {dataset['dataset_title']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='recap-dataset-uri'>URI: <a href='{dataset['dataset_uri']}' target='_blank'>{dataset['dataset_uri']}</a></p>", unsafe_allow_html=True)

                has_rdf = dataset.get('has_rdf_distribution', False)
                if has_rdf:
                    st.markdown("<span class='recap-rdf-badge recap-rdf-available'>RDF Distribution Available</span>", unsafe_allow_html=True)
                else:
                    st.markdown("<span class='recap-rdf-badge recap-rdf-unavailable'>No RDF Distribution</span>", unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("← Back", use_container_width=True):
        st.session_state.loading = False
        st.session_state.current_page = 'query_matching'
        st.rerun()
with col2:
    if st.button("Next →", use_container_width=True, type="primary"):
        st.session_state.loading = True
        st.session_state.next_page = 'sparql_generation'
        st.session_state.loading_msg = "Generating SPARQL queries..."
        st.session_state.fnc_to_call = generate_sparql
        dataset_uris = [ds['dataset_uri'] for ds in st.session_state.selected_datasets]
        st.session_state.params_for_fnc = {
            "query": st.session_state.config.get('query'),
            "model_name": st.session_state.config.get('model_name'),
            "selected_datasets": dataset_uris,
            "language": st.session_state.selected_language
        }
        st.rerun()
