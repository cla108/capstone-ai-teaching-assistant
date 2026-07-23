import streamlit as st


def render_book_information(pages, chapters):
    """
    Display textbook statistics.
    """

    st.header("Book Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Pages", len(pages))

    with col2:
        st.metric("Detected Chapters", len(chapters))

    with col3:
        total_sections = sum(
            len(ch["sections"])
            for ch in chapters
        )

        st.metric("Sections", total_sections)


def render_table_of_contents(chapters):
    """
    Display detected chapters.
    """

    with st.expander(
        "Detected Table of Contents",
        expanded=False
    ):

        for chapter in chapters:

            st.write(
                f"Chapter {chapter['chapter_number']} — {chapter['chapter_title']}"
            )
