import streamlit as st


def render_sidebar():

    with st.sidebar:

        st.title("📚 AI Teaching Assistant")

        st.divider()

        st.markdown(
            """
### Workflow

1. Upload textbook

2. Detect chapters

3. Select chapter

4. Generate lesson

5. Review output

6. Export PDF
"""
        )

        st.divider()

        st.success("GPT Powered")
