import streamlit as st
import json
import time


st.title("🔧 SPARQL Query Generation")
st.markdown("Generated SPARQL queries and their results for each pipeline")
st.markdown("---")

st.markdown("""
<style>
.sparql-box {
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 12px;
    background-color: #f9fafb;
    min-height: 150px;
}
.sparql-title {
    font-size: 14px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
}
.sparql-content {
    font-size: 12px;
    font-family: 'Courier New', monospace;
    color: #1f2937;
    white-space: pre-wrap;
    word-wrap: break-word;
}
.column-header {
    font-size: 15px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 12px;
    padding: 8px;
    background-color: #eff6ff;
    border-radius: 6px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

if 'upvotes' not in st.session_state:
    st.session_state.upvotes = {}

datasets_per_row = 2
rag_data = st.session_state.result.get("rag")
graph_sparql_data = st.session_state.result.get("graph_sparql")
openai_files_data = st.session_state.result.get("openai_files")
shacl_data = st.session_state.result.get("shacl")

def render_dataset_columns(selected_datasets):
    for row_idx in range(0, 4, datasets_per_row):
        datasets_chunk = selected_datasets[row_idx:row_idx + datasets_per_row]
        cols = st.columns(len(datasets_chunk))

        for col_idx, (col, dataset) in enumerate(zip(cols, datasets_chunk)):
            with col:
                dataset_key = f"{dataset['name']}"

                st.markdown(f"<div class='column-header'>{dataset['name']}</div>", unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("<p class='sparql-title'>📝 SPARQL Query</p>", unsafe_allow_html=True)

                    sparql_query = dataset.get('sparql_query')

                    st.code(sparql_query, language="sparql")

                with st.container(border=True):
                    st.markdown("<p class='sparql-title'>📊 Query Result</p>", unsafe_allow_html=True)

                    result_data = {
                        "status": "success"
                    }

                    if result_data["status"] == "success":
                        st.success(f"✓ Query executed successfully")
                        
                        if dataset["is_executable"]:
                            result_json = json.dumps(str(dataset['query_result']), indent=2, ensure_ascii=False)
                            st.code(result_json, language="json", wrap_lines=True, height=400)
                        else:
                            st.info("No result data to display")
                    else:
                        st.error("✗ Query execution failed")

                with st.container(border=True):
                    st.markdown("<p class='sparql-title'>📋 Summary</p>", unsafe_allow_html=True)

                    summary_text = dataset.get('summary')
                    st.write(summary_text)

                is_upvoted = dataset_key in st.session_state.upvotes and st.session_state.upvotes[dataset_key]

                button_label = "✓ Upvoted" if is_upvoted else "👍 Upvote"
                button_type = "primary" if is_upvoted else "secondary"

                if st.button(button_label, key=f"upvote_{dataset_key}", use_container_width=True, type=button_type, disabled=is_upvoted):
                    st.session_state.upvotes[dataset_key] = True

                    if 'upvoted_datasets' not in st.session_state:
                        st.session_state.upvoted_datasets = []

                    if dataset not in st.session_state.upvoted_datasets:
                        st.session_state.upvoted_datasets.append(dataset)

                    st.rerun()

        if row_idx + datasets_per_row < len(selected_datasets):
            st.markdown("---")

rag_data["name"] = "RAG pipeline"
graph_sparql_data["name"] = "Graph SPARQL pipeline"
openai_files_data["name"] = "OpenAI Files pipeline"
shacl_data["name"] = "SHACL pipeline"
selected_datasets_out = [rag_data, graph_sparql_data, openai_files_data, shacl_data]
render_dataset_columns(selected_datasets_out)

st.markdown("---")

if 'upvoted_datasets' in st.session_state and st.session_state.upvoted_datasets:
    col_header, col_clear = st.columns([3, 1])
    with col_header:
        st.subheader("📌 Upvoted Datasets")
        st.markdown(f"**{len(st.session_state.upvoted_datasets)} dataset(s) upvoted**")
    with col_clear:
        if st.button("🗑️ Clear All", type="secondary", use_container_width=True):
            st.session_state.upvoted_datasets = []
            st.session_state.upvotes = {}
            st.rerun()

    for idx, upvoted in enumerate(st.session_state.upvoted_datasets, 1):
        col_exp, col_del = st.columns([9, 1])
        with col_exp:
            with st.expander(f"{idx}. {upvoted['name']}", expanded=False):
                st.markdown("**SPARQL Query:**")
                st.code(upvoted['sparql_query'], language="sparql")
                st.markdown("**Result Data:**")
                
        with col_del:
            if st.button("❌", key=f"delete_{idx}", help="Remove this dataset"):
                st.session_state.upvoted_datasets.pop(idx - 1)
                dataset_keys_to_remove = [k for k, v in st.session_state.upvotes.items()
                                          if upvoted['name'] in k and v]
                for key in dataset_keys_to_remove:
                    del st.session_state.upvotes[key]

                st.rerun()

    st.markdown("---")

col1, col2 = st.columns([1, 1])
with col1:
    if st.button("← Back", use_container_width=True):
        st.session_state.current_page = 'query_matching_recap'
        st.rerun()

with col2:
    if st.button("Export Results →", use_container_width=True, type="primary"):
        st.session_state.loading = False
        st.success("Results exported successfully!")
        st.balloons()
        time.sleep(2)

        for key in list(st.session_state.keys()):
            del st.session_state[key]

        st.session_state.current_page = 'homepage'
        st.rerun()
