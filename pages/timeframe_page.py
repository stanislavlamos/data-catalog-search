import streamlit as st

if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = None

st.title("Timeframe Detection")
st.write("Detected timeframe of your input query")

timeframe_to_print = {
    "week": "Last week",
    "month": "Last month",
    "custom": "Custom",
}

print(st.session_state)
detected_timeframe = st.session_state.result.get('result')
st.write(f"**Detected Timeframe:** {st.session_state.result['start_date']} -> {st.session_state.result['end_date']}")
st.markdown("---")

if st.session_state.loading:
    st.markdown("<style>.centered-spinner {display: flex; justify-content: center; align-items: center; height: 60vh;}</style>", unsafe_allow_html=True)
    st.markdown('<div class="centered-spinner">', unsafe_allow_html=True)
    st.spinner('Detecting timeframe...')
    st.markdown('</div>', unsafe_allow_html=True)
else:
    change_tf = st.selectbox("Do you wish to change the detected timeframe?", ["No", "Yes"], key="change_tf_select")
    if change_tf == "Yes":
        tf_options = ["Last week", "Last month", "Custom"]
        selected = st.selectbox("Select timeframe", tf_options, key="tf_select")
        tf_code = {"Last week": "week", "Last month": "month", "Custom": "custom"}[selected]
        st.session_state.selected_timeframe = tf_code
    else:
        st.session_state.selected_timeframe = detected_timeframe

    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.loading = False
            st.session_state.current_page = 'language'
            st.rerun()
    with col2:
        if st.button("Next →", use_container_width=True, type="primary"):
            st.session_state.loading = True
            st.session_state.next_page = 'query_matching'
            st.session_state.loading_msg = "Matching query..."
            st.rerun()
