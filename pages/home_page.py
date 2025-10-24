import streamlit as st


st.title("NKOD LLM Search")

st.markdown("This application is designed to help you query NKOD data catalog using natural language. The app allows to configure your preferred LLM and translate your natural language query to SPARQL.")

st.markdown("""
### Process Flow:

1. **Configuration** - Input the query and configure the LLM of your choice

2. **Query matching** - Natural language query matched with relevant datasets from NKOD

3. **Recap of matched datasets** - Confirm the relevant NKOD datasets for the subsequent SPARQL generation

4. **SPARQL query generation** - Generated SPARQL query together with the output when executed

5. **Feedback loop** - Submit feedback to the generated SPARQL query and possibly regenerate it
""")

st.markdown("---")
st.markdown("Ready to get started?")
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("Next →", use_container_width=True, type="primary"):
        st.session_state.loading = True
        st.session_state.next_page = 'config'
        st.rerun()
