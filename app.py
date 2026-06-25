import os
import streamlit as st

from pdf_processor import extract_text_from_pdf, combine_pages
from toc_parser import extract_toc_lines, parse_toc
from chapter_extractor import extract_chapters_from_pages
from chunker import create_chapter_chunks
from vector_store import VectorStore
from lesson_generator import generate_instructor_guide

from pdf_generator import generate_lesson_pdf


PAGE_OFFSET = 23

st.set_page_config(
    page_title="Capstone AI Teaching Assistant",
    layout="wide"
)

st.title("Capstone AI Teaching Assistant")

uploaded_file = st.file_uploader(
    "Upload textbook PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    with st.spinner("Processing textbook..."):
        pages = extract_text_from_pdf(uploaded_file)
        full_text = combine_pages(pages)

        toc_lines = extract_toc_lines(full_text)
        structure = parse_toc(toc_lines)
        chapters = extract_chapters_from_pages(pages, structure)

    st.success("Textbook processed successfully.")

    chapter_options = [
        f"Chapter {chapter['chapter_number']}: {chapter['chapter_title']}"
        for chapter in chapters
    ]

    selected_chapter_label = st.selectbox(
        "Select chapter",
        chapter_options
    )

    selected_index = chapter_options.index(selected_chapter_label)
    selected_chapter = chapters[selected_index]



    st.write(
        f"Selected: Chapter {selected_chapter['chapter_number']} — "
        f"{selected_chapter['chapter_title']}"
    )

    if st.button("Generate lesson"):

        progress = st.progress(0)
        status = st.empty()

        status.write("Creating chapter chunks...")
        selected_chapter_chunks = create_chapter_chunks(
            selected_chapter,
            max_words=500,
            overlap_words=75
        )
        progress.progress(20)

        status.write("Retrieving relevant textbook content...")
        vector_store = VectorStore()
        vector_store.add_chunks(selected_chapter_chunks)

        lesson_query = (
            f"Create instructor guide for Chapter "
            f"{selected_chapter['chapter_number']}: "
            f"{selected_chapter['chapter_title']}"
        )

        retrieved_chunks = vector_store.search(lesson_query, k=20)
        progress.progress(45)

        status.write("Generating instructor guide...")
        instructor_guide = generate_instructor_guide(
            selected_chapter=selected_chapter,
            retrieved_chunks=retrieved_chunks,

        )
        progress.progress(65)

        progress.progress(80)

        status.write("Creating PDF...")

        os.makedirs("outputs/lessons", exist_ok=True)

        output_path = (
            f"outputs/lessons/"
            f"chapter_{selected_chapter['chapter_number']}_instructor_guide.pdf"
        )

        generate_lesson_pdf(
            instructor_guide=instructor_guide,
            output_path=output_path
        )

        progress.progress(100)
        status.success("Lesson generated successfully.")

        with open(output_path, "rb") as pdf_file:
            st.download_button(
                label="Download PDF",
                data=pdf_file,
                file_name=f"chapter_{selected_chapter['chapter_number']}_instructor_guide.pdf",
                mime="application/pdf"
            )
