import streamlit as st


def select_chapter(chapters):
    """
    Display the chapter selector and return the selected chapter.
    """

    st.header("Select Chapter")

    chapter_options = [
        f"Chapter {chapter['chapter_number']}: {chapter['chapter_title']}"
        for chapter in chapters
    ]

    selected_label = st.selectbox(
        "Choose a chapter",
        chapter_options
    )

    selected_index = chapter_options.index(selected_label)

    return chapters[selected_index]


def render_chapter_information(chapter):
    """
    Display chapter statistics.
    """

    st.header("Chapter Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Chapter Number",
            chapter["chapter_number"]
        )

    with col2:
        st.metric(
            "Sections",
            len(chapter["sections"])
        )


def render_chapter_preview(chapter, max_preview=5000):
    """
    Preview the extracted chapter text.
    """

    with st.expander(
        "Preview Extracted Chapter",
        expanded=False
    ):

        preview = chapter["text"]

        if len(preview) > max_preview:

            st.text(preview[:max_preview])
            st.info("Preview truncated.")

        else:

            st.text(preview)
