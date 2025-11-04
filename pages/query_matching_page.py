import streamlit as st
from src.data_service import get_mock_datasets


st.title("🔍 Query Matching")
st.markdown("Select relevant datasets that match your query criteria")
st.markdown("---")

all_datasets = get_mock_datasets()

matched_by_title = [ds for ds in all_datasets if
                    'transport' in ds['title'].lower() or
                    'quality' in ds['title'].lower() or
                    'weather' in ds['title'].lower()]

matched_by_desc = [ds for ds in all_datasets if
                   ds not in matched_by_title and (
                   'data' in ds['description'].lower() or
                   'information' in ds['description'].lower() or
                   'records' in ds['description'].lower())]

matched_by_keywords = [ds for ds in all_datasets if
                       ds not in matched_by_title and
                       ds not in matched_by_desc and
                       any(tag in ['environment', 'monitoring', 'municipal'] for tag in ds['tags'])]

if "selected_datasets" not in st.session_state:
    st.session_state.selected_datasets = []

selected_ids = [ds['id'] for ds in st.session_state.selected_datasets]

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
    color: #6b7280;
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


# Added helper to filter datasets by query (title, description, tags)
def filter_datasets(datasets, query: str):
    q = (query or "").strip().lower()
    if not q:
        return datasets
    out = []
    for ds in datasets:
        if q in ds.get('title', '').lower():
            out.append(ds)
            continue
        if q in ds.get('description', '').lower():
            out.append(ds)
            continue
        # match tags (any tag contains query)
        if any(q in tag.lower() for tag in ds.get('tags', [])):
            out.append(ds)
            continue
        # match source
        if q in ds.get('source', '').lower():
            out.append(ds)
            continue
    return out


def render_dataset_card(ds, match_type, idx, parent=None):
    is_selected = ds['id'] in selected_ids
    btn_label = "✕" if is_selected else "➕"
    btn_help = "Remove from selection" if is_selected else "Add to selection"
    btn_key = f"{match_type}_{ds['id']}_{idx}"

    card_class = "dataset-card selected" if is_selected else "dataset-card"
    container_ctx = parent if parent is not None else st.container(border=True)
    with container_ctx:
        header_cols = st.columns([10, 1])
        with header_cols[0]:
            st.markdown(f"<p class='dataset-title'>{ds['title']}</p>", unsafe_allow_html=True)
        with header_cols[1]:
            if st.button(btn_label, key=btn_key, help=btn_help, type="secondary", use_container_width=False):
                if is_selected:
                    st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                else:
                    st.session_state.selected_datasets.append(ds)
                st.rerun()
        st.markdown(f"<p class='dataset-meta'>{ds['source']} • {int(ds['relevance_score'] * 100)}%</p>", unsafe_allow_html=True)


# Integrate search bar and selectable available datasets
is_enabled = st.checkbox("Enable dataset search and selection", value=False)

if is_enabled:
    st.markdown("---")
    search_query = st.text_input(
        "🔎 Search datasets",
        value=st.session_state.get('search_query', ''),
        placeholder="Search by title, description, or tags...",
        key="search_input"
    )

    st.session_state.search_query = search_query

    st.markdown("---")

    filtered_datasets = filter_datasets(all_datasets, search_query)

    # recompute selected ids to ensure up-to-date
    selected_ids = [ds['id'] for ds in st.session_state.selected_datasets]
    available_datasets = [ds for ds in filtered_datasets if ds['id'] not in selected_ids]

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
            color: #9ca3af;
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
        container = st.container(height=500)
        with container:
            for idx, dataset in enumerate(available_datasets):
                # Use the shared renderer so look & behavior are consistent with other lists
                render_dataset_card(dataset, "search", idx)


def render_dataset_card(ds, match_type, idx, parent=None):
    is_selected = ds['id'] in selected_ids
    btn_label = "✕" if is_selected else "➕"
    btn_help = "Remove from selection" if is_selected else "Add to selection"
    btn_key = f"{match_type}_{ds['id']}_{idx}"

    card_class = "dataset-card selected" if is_selected else "dataset-card"
    container_ctx = parent if parent is not None else st.container(border=True)
    with container_ctx:
        header_cols = st.columns([10, 1])
        with header_cols[0]:
            st.markdown(f"<p class='dataset-title'>{ds['title']}</p>", unsafe_allow_html=True)
        with header_cols[1]:
            if st.button(btn_label, key=btn_key, help=btn_help, type="secondary", use_container_width=False):
                if is_selected:
                    st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                else:
                    st.session_state.selected_datasets.append(ds)
                st.rerun()
        st.markdown(f"<p class='dataset-meta'>{ds['source']} • {int(ds['relevance_score'] * 100)}%</p>", unsafe_allow_html=True)


st.markdown(f"### Selected Datasets ({len(st.session_state.selected_datasets)})")
with st.container(height=200, border=True):
    if not st.session_state.selected_datasets:
        st.info("No datasets selected yet")
    else:
        max_per_row = 3
        selected = st.session_state.selected_datasets
        for i in range(0, len(selected), max_per_row):
            chunk = selected[i:i + max_per_row]
            cols = st.columns(len(chunk), border=True)
            for col, ds in zip(cols, chunk):
                render_dataset_card(ds, "selected", i, parent=col)


st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.markdown(f"### Matched by Title")
    with st.container(height=600):
        for i, ds in enumerate(matched_by_title):
            render_dataset_card(ds, "title", i)

with col2:
    st.markdown(f"### Matched by Description")
    with st.container(height=600):
        for i, ds in enumerate(matched_by_desc):
            render_dataset_card(ds, "desc", i)

with col3:
    st.markdown(f"### Matched by Keywords")
    with st.container(height=600):
        for i, ds in enumerate(matched_by_keywords):
            render_dataset_card(ds, "keywords", i)

st.markdown("---")

col_back, col_next = st.columns([1, 1])
with col_back:
    st.button("← Back", use_container_width=True)

with col_next:
    st.button("Next →", use_container_width=True, type="primary", disabled=len(st.session_state.selected_datasets) == 0)
