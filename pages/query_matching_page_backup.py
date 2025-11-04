import streamlit as st
from src.data_service import get_mock_datasets, filter_datasets

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

selected_ids = [ds['id'] for ds in st.session_state.selected_datasets]

st.markdown(f"### Selected Datasets ({len(st.session_state.selected_datasets)})")
with st.container(height=200, border=True):
    if len(st.session_state.selected_datasets) == 0:
        st.info("No datasets selected yet")
    else:
        cols = st.columns(min(len(st.session_state.selected_datasets), 4))
        for idx, ds in enumerate(st.session_state.selected_datasets):
            with cols[idx % 4]:
                btn_key = f"top_remove_{ds['id']}"
                st.markdown(f"""
                <div style="padding: 8px; background-color: #eff6ff; border: 1px solid #3b82f6; border-radius: 6px; margin-bottom: 4px;">
                    <p style="margin: 0; font-size: 12px; font-weight: 600; color: #111827; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">{ds['title']}</p>
                    <p style="margin: 4px 0 0 0; font-size: 10px; color: #6b7280;">{int(ds['relevance_score'] * 100)}%</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✕", key=btn_key, help="Remove"):
                    st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                    st.rerun()

st.markdown("---")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown(f"### Matched by Title ({len(matched_by_title)})")
    with st.container(height=600):
        if len(matched_by_title) == 0:
            st.info("No matches")
        else:
            for idx, ds in enumerate(matched_by_title):
                is_selected = ds['id'] in selected_ids
                btn_label = "✕" if is_selected else "➕"
                btn_key = f"title_{'remove' if is_selected else 'add'}_{ds['id']}_{idx}"

                cols = st.columns([20, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div style="padding: 8px; background-color: {'#eff6ff' if is_selected else '#f9fafb'}; border: 1px solid {'#3b82f6' if is_selected else '#e5e7eb'}; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <p style="margin: 0; font-size: 13px; font-weight: 600; color: #111827;">{ds['title']}</p>
                            <p style="margin: 4px 0 0 0; font-size: 11px; color: #6b7280;">{ds['source']} • {int(ds['relevance_score'] * 100)}%</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button(btn_label, key=btn_key, help="Remove" if is_selected else "Add"):
                        if is_selected:
                            st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                        else:
                            st.session_state.selected_datasets.append(ds)
                        st.rerun()

with col2:
    st.markdown(f"### Matched by Desc ({len(matched_by_desc)})")
    with st.container(height=600):
        if len(matched_by_desc) == 0:
            st.info("No matches")
        else:
            for idx, ds in enumerate(matched_by_desc):
                is_selected = ds['id'] in selected_ids
                btn_label = "✕" if is_selected else "➕"
                btn_key = f"desc_{'remove' if is_selected else 'add'}_{ds['id']}_{idx}"

                cols = st.columns([20, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div style="padding: 8px; background-color: {'#eff6ff' if is_selected else '#f9fafb'}; border: 1px solid {'#3b82f6' if is_selected else '#e5e7eb'}; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <p style="margin: 0; font-size: 13px; font-weight: 600; color: #111827;">{ds['title']}</p>
                            <p style="margin: 4px 0 0 0; font-size: 11px; color: #6b7280;">{ds['source']} • {int(ds['relevance_score'] * 100)}%</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button(btn_label, key=btn_key, help="Remove" if is_selected else "Add"):
                        if is_selected:
                            st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                        else:
                            st.session_state.selected_datasets.append(ds)
                        st.rerun()

with col3:
    st.markdown(f"### Matched by Keywords ({len(matched_by_keywords)})")
    with st.container(height=600):
        if len(matched_by_keywords) == 0:
            st.info("No matches")
        else:
            for idx, ds in enumerate(matched_by_keywords):
                is_selected = ds['id'] in selected_ids
                btn_label = "✕" if is_selected else "➕"
                btn_key = f"keywords_{'remove' if is_selected else 'add'}_{ds['id']}_{idx}"

                cols = st.columns([20, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div style="padding: 8px; background-color: {'#eff6ff' if is_selected else '#f9fafb'}; border: 1px solid {'#3b82f6' if is_selected else '#e5e7eb'}; border-radius: 6px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                        <div style="flex: 1;">
                            <p style="margin: 0; font-size: 13px; font-weight: 600; color: #111827;">{ds['title']}</p>
                            <p style="margin: 4px 0 0 0; font-size: 11px; color: #6b7280;">{ds['source']} • {int(ds['relevance_score'] * 100)}%</p>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button(btn_label, key=btn_key, help="Remove" if is_selected else "Add"):
                        if is_selected:
                            st.session_state.selected_datasets = [d for d in st.session_state.selected_datasets if d['id'] != ds['id']]
                        else:
                            st.session_state.selected_datasets.append(ds)
                        st.rerun()

st.markdown("---")

col_back, col_next = st.columns([1, 1])

with col_back:
    if st.button("← Back", use_container_width=True):
        st.info("Navigation: Back button clicked")

with col_next:
    if st.button("Next →", use_container_width=True, type="primary", disabled=len(st.session_state.selected_datasets) == 0):
        if len(st.session_state.selected_datasets) > 0:
            st.success(f"Proceeding with {len(st.session_state.selected_datasets)} selected datasets")
        else:
            st.error("Please select at least one dataset before proceeding")

st.markdown("---")

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
                tags_html = ''.join([f'<span class="dataset-tag">{tag}</span>' for tag in dataset['tags'][:3]])
                if len(dataset['tags']) > 3:
                    tags_html += f'<span class="dataset-tag">+{len(dataset["tags"]) - 3}</span>'

                btn_key = f"search_add_{dataset['id']}_{idx}"

                cols = st.columns([20, 1])
                with cols[0]:
                    st.markdown(f"""
                    <div class="dataset-card">
                        <div class="dataset-header">
                            <div class="dataset-title">📊 {dataset['title']}</div>
                        </div>
                        <div class="dataset-description">{dataset['description']}</div>
                        <div class="dataset-meta">
                            <span>{dataset['source']}</span>
                            <span>•</span>
                            <span class="dataset-score">{int(dataset['relevance_score'] * 100)}% match</span>
                        </div>
                        <div class="dataset-tags">{tags_html}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cols[1]:
                    if st.button("➕", key=btn_key, help=f"Add {dataset['title']}"):
                        st.session_state.selected_datasets.append(dataset)
                        st.rerun()
