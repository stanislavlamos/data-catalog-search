import streamlit as st
import os
from typing import List, Dict

st.set_page_config(
    page_title="Search Application",
    page_icon="🔍",
    layout="wide"
)

def main():
    st.title("🔍 Search Application")
    st.markdown("---")


    col1, col2 = st.columns([3, 1])

    with col1:
        search_query = st.text_input(
            "Search",
            placeholder="Type to search...",
            label_visibility="collapsed",
            key="search_input"
        )

    with col2:
        search_button = st.button("🔍 Search", type="primary", use_container_width=True)

    if search_query or search_button:
        with st.spinner("Searching..."):
            print("Connecting to Supabase...")
        st.markdown("---")

        if results:
            st.success(f"Found {len(results)} result(s)")

            for result in results:
                with st.container():
                    col_left, col_right = st.columns([4, 1])

                    with col_left:
                        st.subheader(result.get('title', 'Untitled'))
                        if result.get('description'):
                            st.write(result['description'])

                    with col_right:
                        st.caption(f"ID: {result.get('id', 'N/A')}")

                    st.markdown("---")
        else:
            st.info("No results found. Try a different search term.")

    with st.sidebar:
        st.header("About")
        st.write("This is a search application powered by Streamlit and Supabase.")

        st.header("Database Status")
        try:
            st.success("✅ Connected to database")
            st.metric("Total Items", response.count if hasattr(response, 'count') else 0)
        except Exception as e:
            st.error("❌ Database connection failed")
            st.caption(str(e))

if __name__ == "__main__":
    main()
