import streamlit as st


st.title("🔍 Query Matching")
st.markdown("Select relevant datasets that match your query criteria")
st.markdown("---")


matched_datasets = st.session_state.result[0]["matched_lst_dict"]
all_datasets = st.session_state.result[1]["all_datasets"]   

if "selected_datasets" not in st.session_state:
    st.session_state.selected_datasets = []

selected_ids = [ds['dataset_uri'] for ds in st.session_state.selected_datasets]

st.markdown("""
<style>
.dataset-card {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 10px 12px 8px 12px;
    margin-bottom: 10px;
    background-color: #f9fafb;
    transition: all 0.2s;
    position: relative;
}
.dataset-card.selected {
    border-color: #3b82f6;
    background-color: #eff6ff;
}
.dataset-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.dataset-title {
    font-size: 13px;
    font-weight: 600;
    color: #111827;
    margin: 0;
}
.dataset-meta {
    font-size: 11px;
    margin-top: 4px;
}
.dataset-small {
    font-size: 11px;
    margin-top: 4px;
}

/* Make add/remove buttons inside each dataset card the same size */
.dataset-card .stButton > button {
    width: 36px !important;
    height: 28px !important;
    padding: 0 !important;
    font-size: 14px !important;
    line-height: 28px !important;
}

/* fallback smaller global button styling for compactness */
.small-btn {
    font-size: 12px !important;
    padding: 0 4px !important;
    height: 1.4rem !important;
    min-height: 1.4rem !important;
}
</style>
""", unsafe_allow_html=True)


def render_card(ds, source, idx):
    ds_id = ds["dataset_uri"]
    is_selected = ds_id in selected_ids  # Use pre-computed set
    btn_label = "✕" if is_selected else "➕"
    btn_key = f"{source}_{idx}"  # Simplified key
    
    cols = st.columns([10, 1])
    with cols[0]:
        st.markdown(f"<p class='dataset-title'>{ds['title_cs']}</p>", unsafe_allow_html=True)
        st.markdown(f"<span class='match-badge'>Matched on: {ds.get('matched_on', 'Search')}</span>", unsafe_allow_html=True)
        st.markdown(f"<p class='dataset-small'>Publisher: {ds['publisher_cs']}</p>", unsafe_allow_html=True)
        st.markdown(
            f"<p class='recap-dataset-uri'>URI: <a href='{ds['dataset_uri']}' target='_blank'>{ds['dataset_uri']}</a></p>",
            unsafe_allow_html=True)
        rdf_status = "rdf-available" if ds["has_rdf_distribution"] else "rdf-unavailable"
        rdf_text = "✓ RDF available" if ds["has_rdf_distribution"] else "✗ No RDF"
        st.markdown(f"<p class='dataset-meta {rdf_status}' style='color:#22C55E;'>{rdf_text}</p>", unsafe_allow_html=True)
    with cols[1]:
        if st.button(btn_label, key=btn_key):
            if is_selected:
                st.session_state.selected_datasets = [x for x in st.session_state.selected_datasets if x["dataset_uri"] != ds_id]
            else:
                st.session_state.selected_datasets.append(ds)
            st.rerun()

# Added helper to filter datasets by query (title, description, tags)
def filter_datasets(datasets, query: str):
    q = (query or "").strip().lower()
    
    if not q:
        return []
    
    out = []
    for ds in datasets:
        if q in ds.get('title_cs', '').lower() or q in ds.get('publisher_cs', '').lower():
            out.append(ds)
            continue

    return out

with st.container(height=600):
    for i, ds in enumerate(matched_datasets):
        render_card(ds, "matched", i)
        if i < len(matched_datasets) - 1:  # Avoid extra divider at end
            st.divider()

st.markdown("---")
search_query = st.text_input(
    "🔎 Search datasets",
    value=st.session_state.get('search_query', ''),
    placeholder="Search by title, description, or tags...",
    key="search_input"
)

st.session_state.search_query = search_query

filtered_datasets = filter_datasets(all_datasets, search_query)
selected_ids = [ds['dataset_uri'] for ds in st.session_state.selected_datasets]
available_datasets = [ds for ds in filtered_datasets if ds['dataset_uri'] not in selected_ids]

st.markdown(""" 
<style>
    .dataset-card {
        border: 2px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: white;
        transition: all 0.2s;
        position: relative;
    }
    .dataset-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dataset-card-selected {
        border: 2px solid #3b82f6;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        background-color: #eff6ff;
        transition: all 0.2s;
        position: relative;
    }
    .dataset-card-selected:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .dataset-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 8px;
        gap: 12px;
    }
    .dataset-title {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
        flex: 1;
    }
    .dataset-description {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 12px;
        line-height: 1.5;
    }
    .dataset-meta {
        display: flex;
        gap: 8px;
        align-items: center;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .dataset-score {
        color: #3b82f6;
        font-weight: 600;
    }
    .dataset-tags {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
    }
    .dataset-tag {
        background-color: #f3f4f6;
        color: #374151;
        padding: 4px 8px;
        border-radius: 12px;
        font-size: 11px;
    }
    .scrollable-container {
        height: 500px;
        overflow-y: auto;
        padding-right: 8px;
    }
    .scrollable-container::-webkit-scrollbar {
        width: 8px;
    }
    .scrollable-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    .scrollable-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    .scrollable-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    div[data-testid="column"] > div > div > div > button {
        margin-bottom: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f"### Available Datasets ({len(available_datasets)})")

if len(available_datasets) == 0:
    st.info("No datasets match your search")
else:
    container = st.container(height=600)
    with container:
        for idx, dataset in enumerate(available_datasets):
            # Use the shared renderer so look & behavior are consistent with other lists
            render_card(dataset, "search", idx)

st.markdown("---")

st.markdown(f"### Selected Datasets ({len(st.session_state.selected_datasets)})")
with st.container(height=600, border=True):
    if not st.session_state.selected_datasets:
        st.info("No datasets selected yet")
    else:
        max_per_row = 3
        selected = st.session_state.selected_datasets
        for i, ds in enumerate(selected):
            render_card(ds, "selected", i)
            if i < len(selected) - 1:  # Avoid extra divider at end
                st.divider()

st.markdown("---")

too_many_selected = len(st.session_state.selected_datasets) > 3
has_invalid_rdf = any(not ds.get("has_rdf_distribution", False) for ds in st.session_state.selected_datasets)

invalid_selection = too_many_selected or has_invalid_rdf

if invalid_selection:
    if "shown_popup" not in st.session_state or not st.session_state.shown_popup:
        st.warning("⚠️ Invalid selection detected! Please adjust before proceeding.")
        st.session_state.shown_popup = True
    with st.expander("Details of the issue", expanded=True):
        if too_many_selected:
            st.write("- You have selected **more than 3 datasets**.")
        if has_invalid_rdf:
            st.write("- One or more selected datasets **do not have RDF distributions**.")
else:
    st.session_state.shown_popup = False


col_back, col_next = st.columns([1, 1])
with col_back:
    if st.button("← Back", use_container_width=True):
        st.session_state.loading = False
        st.session_state.current_page = 'timeframe'
        st.rerun()

with col_next:
    if invalid_selection:
        st.button("Next →", use_container_width=True, type="primary", disabled=True)
    
    else:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.loading = False
            st.session_state.current_page = 'query_matching_recap'
            st.rerun()

