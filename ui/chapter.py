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
    selected_chapter = chapters[selected_index]

    start_page = selected_chapter.get("start_page")
    end_page = selected_chapter.get("end_page")

    if start_page is not None and end_page is not None:
        st.caption(
            f"Chapter {selected_chapter['chapter_number']}: "
            f"pages {start_page} to {end_page}"
        )
    elif start_page is not None:
        st.caption(
            f"Chapter {selected_chapter['chapter_number']}: "
            f"starts on page {start_page}"
        )

    return selected_chapter


def render_chapter_information(chapter):
    """
    Display chapter statistics.
    """

    st.header("Chapter Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Chapter Number",
            chapter["chapter_number"]
        )

    with col2:
        st.metric(
            "Sections",
            len(chapter.get("sections", []))
        )

    with col3:
        start_page = chapter.get("start_page")
        end_page = chapter.get("end_page")

        if start_page is not None and end_page is not None:
            page_range = f"{start_page}–{end_page}"
        elif start_page is not None:
            page_range = f"{start_page}+"
        else:
            page_range = "Unknown"

        st.metric(
            "Page Range",
            page_range
        )


def render_chapter_preview(chapter, max_preview=5000):
    """
    Preview the extracted chapter text.
    """

    with st.expander(
        "Preview Extracted Chapter",
        expanded=False
    ):
        preview = chapter.get("text", "")

        if len(preview) > max_preview:
            st.text(preview[:max_preview])
            st.info("Preview truncated.")
        else:
            st.text(preview)
